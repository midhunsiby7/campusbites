from flask import Flask, render_template, request, redirect, jsonify, session, url_for, g
import json
import mysql.connector
import qrcode
import io
import base64
from datetime import datetime, date, timedelta, time
import os
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from PIL import Image
import re
import time as time_module
import razorpay # Import the Razorpay library
import hmac
import hashlib
import schedule
import threading
# Background daily scheduler thread
import pytz
import firebase_admin
from firebase_admin import credentials, auth



# At the top
app = Flask(__name__)


cred = credentials.Certificate("serviceAccountKey.json")  # Download from Firebase Console > Project Settings > Service Accounts
firebase_admin.initialize_app(cred)

app.secret_key = os.getenv("FLASK_SECRET_KEY", "super-secret-key")
app.config.update(
    SESSION_COOKIE_SAMESITE="Lax",      # fine for same-origin pages
    SESSION_COOKIE_SECURE=False,        # set True in production if you’re fully on HTTPS
    PERMANENT_SESSION_LIFETIME=timedelta(days=30),
)

def daily_task():
    ist = pytz.timezone("Asia/Kolkata")

    def run_if_midnight_ist():
        now_ist = datetime.now(ist)
        if now_ist.hour == 18 and now_ist.minute == 4:
            _daily_cleanup_and_reset_at_startup()

    while True:
        run_if_midnight_ist()
        time_module.sleep(60)  # check every minute
# Start the daily task thread
threading.Thread(target=daily_task, daemon=True).start()

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
app.secret_key = 'super-secret-key'

RAZORPAY_KEY_ID = "rzp_test_6EWdw5ccuRLg2c" 
RAZORPAY_KEY_SECRET = "lV3wcbsNVEAj4mbZB8jzayBb"
# This is the secret you created in the Razorpay Webhook settings
RAZORPAY_WEBHOOK_SECRET = "99Um2MwF@jwVwtW"

# Initialize Razorpay client
razorpay_client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))

 

def get_db_connection():
    if 'db_conn' not in g:
        g.db_conn = mysql.connector.connect(
            host="127.0.0.1",
            user="root",
            password="8423",
            database="campusbites",
            port=3306,
            ssl_disabled=True,
            autocommit=False 
        )
        g.cursor = g.db_conn.cursor(dictionary=True, buffered=True)
    return g.db_conn, g.cursor

def get_or_create_user(email, name=None, provider=None):
    """Returns (user_id, need_profile, db_name, db_phone, db_role). Creates user if not found."""
    conn, cursor = get_db_connection()
    try:
        cursor.execute("SELECT id, name, phone, role FROM users WHERE email=%s LIMIT 1", (email,))
        row = cursor.fetchone()
        if not row:
            # create minimal user; you can store provider if you kept that column
            cursor.execute("""
                INSERT INTO users (email, name, phone, role)
                VALUES (%s, %s, %s, %s)
            """, (email, name, None, 'student'))
            conn.commit()
            user_id = cursor.lastrowid
            need_profile = True
            return user_id, need_profile, (name or ""), None, 'student'
        else:
            user_id = row['id']
            db_name = row['name']
            db_phone = row['phone']
            db_role = row.get('role', 'student') if isinstance(row, dict) else row['role']
            need_profile = (not db_name) or (not db_phone)
            return user_id, need_profile, db_name, db_phone, db_role
    finally:
        cursor.close()
        conn.close()


@app.before_request
def before_request():
    get_db_connection()

@app.teardown_request
def teardown_request(exception):
    db_conn = g.pop('db_conn', None)
    if db_conn is not None:
        if db_conn.is_connected():
            if exception:
                db_conn.rollback()
                print(f"Database transaction rolled back due to: {exception}")
            else:
                try:
                    db_conn.commit()
                except mysql.connector.Error as e:
                    print(f"Warning: Failed to commit on teardown: {e}")
            db_conn.close()

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def create_notification(user_id, message, notif_type, related_id=None, is_admin=False):
    """Inserts a new notification into the database."""
    print("--- [create_notification] Function called. ---")
    conn, cursor = get_db_connection()
    try:
        print(f"--- [create_notification] Executing INSERT for notification: '{message}' ---")
        cursor.execute("""
            INSERT INTO notifications (user_id, is_admin_notification, message, type, related_id)
            VALUES (%s, %s, %s, %s, %s)
        """, (user_id, is_admin, message, notif_type, related_id))
        print("--- [create_notification] INSERT statement executed (pre-commit). ---")
    except mysql.connector.Error as err:
        print(f"---!!! [create_notification] DATABASE ERROR: {err} !!!---")
        conn.rollback()

from PIL import Image
import re

def process_and_save_image(file, food_name):
    clean_name = re.sub(r'[^a-zA-Z0-9]+', '_', food_name.lower())
    timestamp = int(time_module.time())
    new_filename = f"{clean_name}_{timestamp}.webp"
    save_path = os.path.join(app.config['UPLOAD_FOLDER'], new_filename)

    try:
        image = Image.open(file)
        TARGET_SIZE = (200, 200) 
        original_width, original_height = image.size
        target_aspect = TARGET_SIZE[0] / TARGET_SIZE[1]
        original_aspect = original_width / original_height

        if original_aspect > target_aspect:
            new_width = int(original_height * target_aspect)
            left = (original_width - new_width) / 2
            top = 0
            right = (original_width + new_width) / 2
            bottom = original_height
        else:
            new_height = int(original_width / target_aspect)
            left = 0
            top = (original_height - new_height) / 2
            right = original_width
            bottom = (original_height + new_height) / 2
        
        image = image.crop((left, top, right, bottom))
        image = image.resize(TARGET_SIZE, Image.Resampling.LANCZOS)
        
        image.convert("RGB").save(save_path, "webp", quality=100)
        return new_filename
    except Exception as e:
        print(f"Error processing image {file.filename}: {e}")
        return None
    
# --- TOKEN GENERATION AND CLEANUP LOGIC ---

def _generate_daily_token_number():
    conn, cursor = get_db_connection()
    today = date.today()

    # Fetch all used tokens from today's orders
    cursor.execute("SELECT token_number FROM orders WHERE DATE(created_at) = %s", (today,))
    used_tokens_today = {row['token_number'] for row in cursor.fetchall()}

    # Fetch permanently blocked tokens from uncollected
    cursor.execute("SELECT token_number FROM uncollected_tokens")
    reserved_tokens = {row['token_number'] for row in cursor.fetchall()}

    token_number = 1
    while token_number in used_tokens_today or token_number in reserved_tokens:
        token_number += 1

    return token_number


def _daily_cleanup_and_reset_at_startup():
    startup_db_conn = None
    startup_cursor = None
    try:
        startup_db_conn = mysql.connector.connect(
            host="127.0.0.1",
            user="root",
            password="8423",
            database="campusbites",
            port=3306,
            ssl_disabled=True,
            autocommit=False
        )
        startup_cursor = startup_db_conn.cursor(dictionary=True, buffered=True)

        yesterday = date.today() - timedelta(days=1)

        # Flag file to prevent repeated cleanup per day
        cleanup_flag_file = os.path.join(app.root_path, '.last_cleanup_date')
        last_cleanup_date_str = None
        if os.path.exists(cleanup_flag_file):
            with open(cleanup_flag_file, 'r') as f:
                last_cleanup_date_str = f.read().strip()

        if last_cleanup_date_str == str(date.today()):
            print(f"[✔] Cleanup for {date.today()} already done.")
            return

        print(f"[⏳] Performing cleanup for {yesterday}...")

        # Get all orders from yesterday (no status filter)
        startup_cursor.execute("""
            SELECT * FROM orders
        """)
        old_orders = startup_cursor.fetchall()

        for order in old_orders:
            try:
                # Insert into order_history
                startup_cursor.execute("""
                    INSERT INTO order_history (id, user_id, token_number, total, status, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    order['id'], order['user_id'], order['token_number'],
                    order['total'], order['status'], order['created_at']
                ))

                # If status was still open, add to uncollected tokens
                if order['status'] in ['pending', 'confirmed']:
                    startup_cursor.execute("""
                        INSERT IGNORE INTO uncollected_tokens (token_number, order_id, order_date, reason)
                        VALUES (%s, %s, %s, %s)
                    """, (
                        order['token_number'], order['id'], order['created_at'],
                        'Not Collected/Paid'
                    ))

                # Delete from orders
                startup_cursor.execute("DELETE FROM orders")

            except mysql.connector.Error as err:
                print(f"⚠️ Error for order ID {order['id']}: {err}")

        startup_db_conn.commit()

        with open(cleanup_flag_file, 'w') as f:
            f.write(str(date.today()))

        print(f"[✅] Cleanup completed. Moved {len(old_orders)} orders to order_history.")

    except Exception as e:
        if startup_db_conn and startup_db_conn.is_connected():
            startup_db_conn.rollback()
        print(f"[❌] CRITICAL ERROR during cleanup: {e}")

    finally:
        if startup_db_conn and startup_db_conn.is_connected():
            startup_cursor.close()
            startup_db_conn.close()



@app.route('/')
def intro():
    return render_template('intro.html')

# Admin Login Page
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if session.get('admin_logged_in'):
        return redirect(url_for('admin_dashboard'))
    error = None
    if request.method == 'POST':
        conn, cursor = get_db_connection()
        username = request.form['username']
        password = request.form['password']
        cursor.execute("SELECT * FROM admin_users WHERE username = %s", (username,))
        admin = cursor.fetchone()
        #  Check hashed password
        if admin and check_password_hash(admin['password'], password):
            session['admin_logged_in'] = True
            session['admin_username'] = admin['username']
            session.permanent = True
            return redirect(url_for('admin_dashboard'))
        else:
            error = "Invalid credentials. Please try again."
    return render_template('admin_login.html', error=error)

# User Login Page

@app.route("/login")
def login_page():
        return render_template("login.html")

@app.route('/check-login', methods=['GET'])
def check_login():
    is_admin = bool(session.get('admin_id'))
    is_user = bool(session.get('user_id'))
    role = 'admin' if is_admin else ('user' if is_user else None)
    return jsonify({
        "logged_in": bool(role),
        "role": role
    })

import hashlib  # if you're using hashlib for hashing

# Load Firebase public config from file
@app.route("/firebase-config")
def firebase_config():
    return jsonify({ 
  "apiKey": "AIzaSyA_uhRgSRZ3FAEByIcy6OiDUDjg9olUepg",
  "authDomain": "campusbites-964d4.firebaseapp.com",
  "projectId": "campusbites-964d4",
  "storageBucket": "campusbites-964d4.firebasestorage.app",
  "messagingSenderId": "387692591098",
  "appId": "1:387692591098:web:373218ae5e0eba33491643",
  "measurementId": "G-JXBZ4H874P"
    })

# Handle login data from frontend
@app.route("/firebase-login", methods=["POST"])
def firebase_login():
    print("got it")
    data = request.get_json()
    id_token = data.get("idToken")
    name = data.get("name")
    phone = data.get("phone")

    if not id_token:
        return jsonify({"error": "ID token is required"}), 400

    try:
        # Verify the Firebase ID token with clock skew tolerance
        decoded_token = auth.verify_id_token(id_token, clock_skew_seconds=60)
        email = decoded_token.get('email')
        
        if not email:
            return jsonify({"error": "Email not found in token"}), 400

    except Exception as e:
        return jsonify({"error": "Invalid token: " + str(e)}), 401

    conn, cursor = get_db_connection()

    # Check if user exists
    cursor.execute("SELECT * FROM users WHERE email = %s LIMIT 1", (email,))
    user = cursor.fetchone()

    if not user:
        # Create minimal record (default role: student)
        cursor.execute("""
            INSERT INTO users (email, name, phone, role)
            VALUES (%s, %s, %s, %s)
        """, (email, name, phone, 'student'))
        conn.commit()
        cursor.execute("SELECT * FROM users WHERE email = %s LIMIT 1", (email,))
        user = cursor.fetchone()

    # Create session with correct keys
    session["user_id"] = user["id"]
    session["user_email"] = user["email"]
    session["user_name"] = user["name"] or email.split('@')[0]
    session["role"] = user.get("role", "student") if isinstance(user, dict) else "student"
    session.permanent = True

    cursor.close()
    conn.close()

    # Check if profile is incomplete
    # Check if profile is incomplete
    need_profile = (user["name"] is None or user["name"] == "") or (user["phone"] is None or user["phone"] == "")

    return jsonify({
        "ok": True,
        "need_profile": bool(need_profile),
        "role": session["role"]
    })


# Admin Route Protection & Notifications ---

@app.route("/complete-profile", methods=["GET", "POST"])
def complete_profile():
    if "user_id" not in session:  # This should match what you set in firebase-login
        return redirect("/login")

    if request.method == "POST":
        name = request.form.get("name")
        phone = request.form.get("phone")

        if not name or not phone:
            return render_template("complete_profile.html", error="Please fill all fields")

        conn, cursor = get_db_connection()
        cursor.execute(
            "UPDATE users SET name=%s, phone=%s WHERE id=%s",
            (name, phone, session["user_id"])
        )
        conn.commit()
        
        # Update session with new name
        session["user_name"] = name
        
        cursor.close()
        conn.close()

        return redirect("/home")

    return render_template("complete_profile.html")

@app.route('/admin/dashboard')
def admin_dashboard():
    conn, cursor = get_db_connection()
    if not session.get('admin_logged_in'):
        return redirect('/admin/login')

    status_filter = request.args.get('status', 'all')
    sort_by = request.args.get('sort', 'newest')
    
    query = """
    SELECT orders.id, orders.token_number, orders.status, orders.payment_status,
           users.name AS user_name, orders.created_at, orders.total
    FROM orders
    JOIN users ON orders.user_id = users.id
    WHERE DATE(orders.created_at) = %s
"""

    params = [datetime.now().date()]

    if status_filter != 'all':
        query += " AND orders.status = %s"
        params.append(status_filter)

    query += " ORDER BY orders.created_at DESC" if sort_by == 'newest' else " ORDER BY orders.created_at ASC"

    cursor.execute(query, tuple(params))
    orders = cursor.fetchall()

    now = datetime.now()
    for order in orders:
        # --- MODIFICATION START ---
        # The 10-minute time check is removed. 
        # An order is now confirmable as long as its status is 'pending'.
        order['is_confirmable'] = order['status'] == 'pending'
        # --- MODIFICATION END ---
        
        if 'created_at' in order and order['created_at']:
            elapsed = now - order['created_at']
            secs = int(elapsed.total_seconds())
            if secs < 60:
                order['time_ago'] = f"{secs}s ago"
            elif secs < 3600:
                order['time_ago'] = f"{secs // 60}m ago"
            else:
                order['time_ago'] = f"{secs // 3600}h ago"
        else:
            order['time_ago'] = "N/A"

    return render_template('admin_dashboard.html',
                           orders=orders,
                           selected_status=status_filter,
                           selected_sort=sort_by)

@app.route('/admin/foods')
def admin_foods():
    conn, cursor = get_db_connection()
    if not session.get('admin_logged_in'):
        return redirect('/admin/login')

    today = datetime.now().date()

    cursor.execute("""
        SELECT fi.*, dm.stock AS today_stock
        FROM food_items fi
        LEFT JOIN daily_menu dm ON fi.id = dm.food_id AND DATE(dm.available_date) = %s
    """, (today,))
    foods = cursor.fetchall()

    return render_template('admin_foods.html', foods=foods)

@app.route('/admin/add-food', methods=['GET', 'POST'])
def add_food():
    conn, cursor = get_db_connection()
    if not session.get('admin_logged_in'):
        return redirect('/admin/login')

    if request.method == 'POST':
        name = request.form['name']
        price = request.form['price']
        category = request.form['category']
        about = request.form['about']
        image = request.files['image']

        if image and name:
            ext = os.path.splitext(image.filename)[1].lower()
            filename = name.replace(" ", "_").lower() + '.webp'
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

            img = Image.open(image)
            img.save(filepath, format='WEBP')

            cursor.execute("""
                INSERT INTO food_items (name, price, category, about, image, stock, available)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (name, price, category, about, filename, 10, 1))
            conn.commit()

            return redirect('/admin/dashboard')

    return render_template('add_food.html')

@app.route('/admin/foods/edit/<int:food_id>', methods=['GET', 'POST'])
def edit_food(food_id):
    conn, cursor = get_db_connection()
    if not session.get('admin_logged_in'):
        return redirect('/admin/login')

    if request.method == 'POST':
        name = request.form['name']
        price = float(request.form['price'])
        category = request.form['category']
        about = request.form['about']
        available = int(request.form.get('available', 1))

        image = request.files.get('image')
        image_url = None

        if image and image.filename != '' and allowed_file(image.filename):
            image_url = process_and_save_image(image, name)
            if image_url is None:
                print(f"Warning: Image processing failed for food ID {food_id}. Skipping image update.")
                cursor.execute("""
                    UPDATE food_items
                    SET name=%s, price=%s, category=%s, about=%s, available=%s
                    WHERE id=%s
                """, (name, price, category, about, available, food_id))
            else:
                cursor.execute("""
                    UPDATE food_items
                    SET name=%s, price=%s, category=%s, about=%s, image=%s, available=%s
                    WHERE id=%s
                """, (name, price, category, about, image_url, available, food_id))
        else:
            cursor.execute("""
                UPDATE food_items
                SET name=%s, price=%s, category=%s, about=%s, available=%s
                WHERE id=%s
            """, (name, price, category, about, available, food_id))

        conn.commit()
        return redirect('/admin/foods')

    cursor.execute("SELECT * FROM food_items WHERE id = %s", (food_id,))
    food = cursor.fetchone()

    if food is None:
        return "Food item not found", 404

    return render_template('edit_food.html', food=food)

@app.route('/admin/foods/delete/<int:food_id>', methods=['POST'])
def delete_food(food_id):
    conn, cursor = get_db_connection()
    if not session.get('admin_logged_in'):
        return redirect('/admin/login')

    cursor.execute("DELETE FROM food_items WHERE id = %s", (food_id,))
    conn.commit()
    return redirect('/admin/foods')

@app.route('/admin/todays-menu', methods=['GET', 'POST'])
def admin_todays_menu():
    conn, cursor = get_db_connection()
    if not session.get('admin_logged_in'):
        return redirect('/admin/login')

    today = datetime.now().date()

    if request.method == 'POST':
        action = request.args.get('action', 'set')

        if action == 'delete':
            cursor.execute("DELETE FROM daily_menu WHERE DATE(available_date) = %s", (today,))
            conn.commit()
            return redirect('/admin/todays-menu')

        elif action == 'edit':
            cursor.execute("SELECT * FROM daily_menu WHERE DATE(available_date) = %s", (today,))
            items_on_menu_today = cursor.fetchall()
            existing_food_ids = {item['food_id'] for item in items_on_menu_today}

            for item in items_on_menu_today:
                new_stock = request.form.get(f'stock_{item["food_id"]}')
                if new_stock:
                    cursor.execute("UPDATE daily_menu SET stock = %s WHERE id = %s", (int(new_stock), item["id"]))

            b_start = request.form.get('breakfast_start')
            b_end = request.form.get('breakfast_end')
            l_start = request.form.get('lunch_start')
            l_end = request.form.get('lunch_end')

            if b_start and b_end:
                cursor.execute("""
                    UPDATE daily_menu dm
                    JOIN food_items fi ON dm.food_id = fi.id
                    SET dm.start_time = %s, dm.end_time = %s
                    WHERE DATE(dm.available_date) = %s AND fi.category = 'breakfast'
                """, (b_start, b_end, today))
            if l_start and l_end:
                cursor.execute("""
                    UPDATE daily_menu dm
                    JOIN food_items fi ON dm.food_id = fi.id
                    SET dm.start_time = %s, dm.end_time = %s
                    WHERE DATE(dm.available_date) = %s AND fi.category = 'lunch'
                """, (l_start, l_end, today))

            new_food_ids_to_add = request.form.getlist('new_food_ids')
            for food_id in new_food_ids_to_add:
                if int(food_id) not in existing_food_ids:
                    cursor.execute("SELECT category FROM food_items WHERE id = %s", (food_id,))
                    food_category = cursor.fetchone()
                    if food_category:
                        category = food_category['category']
                        stock = request.form.get(f'stock_new_{food_id}', 1)

                        start_time = b_start if category == 'breakfast' else l_start
                        end_time = b_end if category == 'breakfast' else l_end

                        if start_time and end_time:
                            cursor.execute("""
                                INSERT INTO daily_menu (food_id, available_date, start_time, end_time, stock)
                                VALUES (%s, %s, %s, %s, %s)
                            """, (food_id, today, start_time, end_time, stock))

            conn.commit()
            return redirect('/admin/todays-menu')

        else: # action == 'set'
            cursor.execute("DELETE FROM daily_menu WHERE DATE(available_date) = %s", (today,))
            food_ids = request.form.getlist('food_ids')
            b_start = request.form.get('breakfast_start')
            b_end = request.form.get('breakfast_end')
            l_start = request.form.get('lunch_start')
            l_end = request.form.get('lunch_end')

            for food_id in food_ids:
                cursor.execute("SELECT category FROM food_items WHERE id = %s", (food_id,))
                category = cursor.fetchone()['category']
                stock = request.form.get(f'stock_{food_id}', 1)

                if category == 'breakfast':
                    start_time = b_start
                    end_time = b_end
                else:
                    start_time = l_start
                    end_time = l_end

                cursor.execute("""
                    INSERT INTO daily_menu (food_id, available_date, start_time, end_time, stock)
                    VALUES (%s, %s, %s, %s, %s)
                """, (food_id, today, start_time, end_time, stock))

            conn.commit()
            return redirect('/admin/todays-menu')

    cursor.execute("""
        SELECT dm.*, fi.name, fi.category
        FROM daily_menu dm
        JOIN food_items fi ON dm.food_id = fi.id
        WHERE DATE(dm.available_date) = %s
    """, (today,))
    data = cursor.fetchall()

    current_menu_food_ids = {item['food_id'] for item in data}

    cursor.execute("SELECT * FROM food_items WHERE available = 1")
    all_foods = cursor.fetchall()

    foods_not_on_menu = [food for food in all_foods if food['id'] not in current_menu_food_ids]

    today_menu = {}
    breakfast_times = {'start': None, 'end': None}
    lunch_times = {'start': None, 'end': None}

    for item in data:
        category = item['category']
        if category not in today_menu:
            today_menu[category] = []
        today_menu[category].append(item)
        
        if category == 'breakfast' and breakfast_times['start'] is None:
            if isinstance(item['start_time'], timedelta):
                total_seconds = int(item['start_time'].total_seconds())
                hours, remainder = divmod(total_seconds, 3600)
                minutes, seconds = divmod(remainder, 60)
                breakfast_times['start'] = time(hours, minutes, seconds)
            else:
                breakfast_times['start'] = item['start_time']
            if isinstance(item['end_time'], timedelta):
                total_seconds = int(item['end_time'].total_seconds())
                hours, remainder = divmod(total_seconds, 3600)
                minutes, seconds = divmod(remainder, 60)
                breakfast_times['end'] = time(hours, minutes, seconds)
            else:
                breakfast_times['end'] = item['end_time']

        elif category == 'lunch' and lunch_times['start'] is None:
            if isinstance(item['start_time'], timedelta):
                total_seconds = int(item['start_time'].total_seconds())
                hours, remainder = divmod(total_seconds, 3600)
                minutes, seconds = divmod(remainder, 60)
                lunch_times['start'] = time(hours, minutes, seconds)
            else:
                lunch_times['start'] = item['start_time']
            if isinstance(item['end_time'], timedelta):
                total_seconds = int(item['end_time'].total_seconds())
                hours, remainder = divmod(total_seconds, 3600)
                minutes, seconds = divmod(remainder, 60)
                lunch_times['end'] = time(hours, minutes, seconds)
            else:
                lunch_times['end'] = item['end_time']

    default_breakfast_start = "08:00"
    default_breakfast_end = "11:00"
    default_lunch_start = "12:00"
    default_lunch_end = "15:00"

    return render_template('todays_menu.html', 
                            today_menu=today_menu, 
                            foods=all_foods, 
                            foods_not_on_menu=foods_not_on_menu, 
                            breakfast_times=breakfast_times, 
                            lunch_times=lunch_times,         
                            default_breakfast_start=default_breakfast_start, 
                            default_breakfast_end=default_breakfast_end,
                            default_lunch_start=default_lunch_start,
                            default_lunch_end=default_lunch_end)

@app.route('/admin/deliver/<int:order_id>', methods=['POST'])
def mark_delivered(order_id):
    conn, cursor = get_db_connection()
    if not session.get('admin_logged_in'):
        return redirect('/admin/login')

    # Admin can only deliver an order that has been confirmed (i.e., paid)
    cursor.execute("UPDATE orders SET status = 'delivered' WHERE id = %s AND status = 'confirmed'", (order_id,))
    
    # Notify user
    cursor.execute("SELECT user_id, token_number FROM orders WHERE id = %s", (order_id,))
    order_data = cursor.fetchone()
    if order_data:
        message = f"Your order #{order_data['token_number']} is out for delivery!"
        create_notification(order_data['user_id'], message, 'order_delivered', order_id)

    return redirect(url_for('admin_dashboard'))

@app.route('/admin/logout',methods=['POST'])
def admin_logout():
    session.pop('admin_logged_in', None)
    session.pop('admin_username', None)
    return redirect('/admin/login')

@app.route('/admin/collect/<int:order_id>', methods=['POST'])
def admin_mark_as_collected(order_id):
    try:
        conn, cursor = get_db_connection()
        # Check if order exists
        cursor.execute("SELECT * FROM orders WHERE id = %s", (order_id,))
        order = cursor.fetchone()

        if not order:
            return jsonify({'success': False, 'error': 'Order not found'}), 404

        if order['status'] == 'delivered' or order['status'] == 'collected':
            return jsonify({'success': False, 'error': 'Order already collected/delivered'}), 400

        if order['status'] != 'confirmed':
            return jsonify({'success': False, 'error': 'Order not confirmed yet'}), 400

        # Mark as delivered
        cursor.execute("UPDATE orders SET status = 'delivered' WHERE id = %s", (order_id,))
        conn.commit()

        return jsonify({
            'success': True,
            'message': 'Order marked as collected!',
            'status_changed_to': 'delivered'
        })

    except Exception as e:
        conn.rollback()
        print("Error in /admin/collect route:", e)
        return jsonify({'success': False, 'error': 'Server error'}), 500


@app.route('/admin/confirm-token', methods=['POST'])
def confirm_by_token():
    conn, cursor = get_db_connection()
    token = request.form['token']
    cursor.execute("SELECT * FROM orders WHERE token_number = %s", (token,))
    order = cursor.fetchone()
    if order:
        if order['status'] == 'pending':
            cursor.execute("UPDATE orders SET status = 'confirmed' WHERE id = %s", (order['id'],))
            conn.commit()
            cursor.execute("UPDATE order_history SET status = %s WHERE order_id = %s", ('confirmed', order['id']))
            conn.commit()
            session['user_notification'] = {'user_id': order['user_id'], 'message': f"Your order #{order['token_number']} has been confirmed!", 'type': 'confirmed_order'}
            session['admin_notification'] = {'admin_username': 'any', 'message': f"Order #{order['token_number']} confirmed by QR scan.", 'type': 'order_confirmed_by_qr', 'order_id': order['id']}
            return jsonify({'success': True, 'order_id': order['id'], 'status_changed_to': 'confirmed'})
        elif order['status'] == 'confirmed':
            cursor.execute("UPDATE orders SET status = 'collected' WHERE id = %s", (order['id'],))
            conn.commit()
            return jsonify({'success': True, 'order_id': order['id'], 'status_changed_to': 'collected'})
        else:
            return jsonify({'success': True, 'order_id': order['id'], 'status_changed_to': order['status'], 'message': 'Order already processed.'})
    return jsonify({'success': False, 'error': 'Invalid or already processed token.'})

@app.route('/admin/order/<int:order_id>')
def admin_view_order(order_id):
    conn, cursor = get_db_connection()
    if not session.get('admin_logged_in'):
        return redirect('/admin/login')

    cursor.execute("""
        SELECT o.id AS order_id, o.status, o.token_number, o.total, o.created_at,
               u.name AS user_name,
               fi.name AS food_name, fi.price, oi.quantity, fi.image AS food_image
        FROM orders o
        JOIN users u ON o.user_id = u.id
        JOIN order_items oi ON o.id = oi.order_id
        JOIN food_items fi ON oi.food_id = fi.id
        WHERE o.id = %s
    """, (order_id,))

    items = cursor.fetchall()
    if not items:
        return "Order not found", 404

    order_main_info = items[0]
    
    # --- MODIFICATION START ---
    # Removed the 10-minute time check here as well.
    is_confirmable_now = order_main_info['status'] == 'pending'
    # --- MODIFICATION END ---

    return render_template("admin_order_view.html", order=order_main_info, items=items, is_confirmable_now=is_confirmable_now)

@app.route('/admin/orders/confirm/<int:order_id>', methods=['POST'])
def confirm_order(order_id):
    conn, cursor = get_db_connection()
    if not session.get('admin_logged_in'):
        return redirect('/admin/login')

    cursor.execute("SELECT user_id, token_number FROM orders WHERE id = %s AND status = 'pending'", (order_id,))
    order_data = cursor.fetchone()

    if not order_data:
        return "Order not found or is not in a confirmable state.", 404

    # MODIFICATION: The entire block checking for the 10-minute delay has been removed.
    
    cursor.execute("UPDATE orders SET status = 'confirmed' WHERE id = %s", (order_id,))
    
    # You can add your notification logic here if needed
    # create_notification(...)

    return redirect(url_for('admin_dashboard'))

@app.route('/admin/food/sell/<int:food_id>', methods=['POST'])
def manual_sell(food_id):
    conn, cursor = get_db_connection()
    if not session.get('admin_logged_in'):
        return redirect('/admin/login')

    qty = int(request.form['qty'])
    today = datetime.now().date()

    cursor.execute("""
        UPDATE daily_menu
        SET stock = GREATEST(stock - %s, 0)
        WHERE food_id = %s AND DATE(available_date) = %s
    """, (qty, food_id, today))

    conn.commit()
    return redirect('/admin/foods')

@app.route('/admin/scan-qr')
def scan_qr():
    conn, cursor = get_db_connection()
    if not session.get('admin_logged_in'):
        return redirect('/admin/login')

    return render_template('scan_qr.html', order=None)

@app.route('/admin/scan_order/<int:order_id>')
def scan_order(order_id):
    conn, cursor = get_db_connection()
    if not session.get('admin_logged_in'):
        return redirect('/admin/login')

    cursor.execute("""
        SELECT o.id AS order_id, o.status, o.token_number, o.total, o.created_at,
               u.name AS user_name,
               fi.name AS food_name, fi.price, oi.quantity, fi.image AS food_image
        FROM orders o
        JOIN users u ON o.user_id = u.id
        JOIN order_items oi ON o.id = oi.order_id
        JOIN food_items fi ON oi.food_id = fi.id
        WHERE o.id = %s
    """, (order_id,))

    items = cursor.fetchall()
    if not items:
        return "Order not found", 404

    order_main_info = items[0]
    now = datetime.now()
    time_elapsed = now - order_main_info['created_at']
    is_confirmable_now = order_main_info['status'] == 'pending' and time_elapsed.total_seconds() >= 600

    return render_template("scan_qr.html", order=order_main_info, items=items, is_confirmable_now=is_confirmable_now)
@app.route('/admin/uncollected-tokens')
def get_uncollected_tokens():
    conn, cursor = get_db_connection()

    query = """
        SELECT ut.token_number, u.name as user_name, o.status as order_status, ut.order_date
        FROM uncollected_tokens ut
        JOIN orders o ON ut.order_id = o.id
        JOIN users u ON o.user_id = u.id
        ORDER BY ut.order_date DESC
    """
    
    cursor.execute(query)
    tokens = cursor.fetchall()

    for token in tokens:
        if isinstance(token['order_date'], datetime):
            token['order_date'] = token['order_date'].strftime('%d %b %Y, %I:%M %p')

    return jsonify(tokens)



@app.route('/api/live-stock')
def live_stock():
    conn, cursor = get_db_connection()
    today = datetime.now().date()
    cursor.execute("SELECT food_id, stock FROM daily_menu WHERE DATE(available_date) = %s", (today,))
    stock_data = cursor.fetchall()
    return jsonify({str(row['food_id']): row['stock'] for row in stock_data})



@app.route('/home')
def home():
    conn, cursor = get_db_connection()
    if not session.get('user_id'):
        return redirect(url_for('login'))


    now = datetime.now()
    today = datetime.now().date()
    current_time = now.time()

    cursor.execute("""
        SELECT fi.*, dm.stock
        FROM food_items fi
        JOIN daily_menu dm ON fi.id = dm.food_id
        WHERE DATE(dm.available_date) = %s
          AND %s BETWEEN dm.start_time AND dm.end_time
          AND dm.stock > 0
    """, (today, current_time))

    foods = cursor.fetchall()
    return render_template("index.html", foods=foods)

@app.route('/food/<int:food_id>')
def food_detail(food_id):
    conn, cursor = get_db_connection()
    if not session.get('user_id'):
        return redirect(url_for('login'))

    today = date.today()

    cursor.execute("""
        SELECT f.*, d.stock
        FROM food_items f
        JOIN daily_menu d ON f.id = d.food_id
        WHERE f.id = %s AND DATE(d.available_date) = %s
    """, (food_id, today))
    food = cursor.fetchone()

    if not food:
        return "Food not available today", 404

    return render_template("food_detail.html", food=food)

@app.route('/cart')
def cart():
    conn, cursor = get_db_connection()
    if not session.get('user_id'):
        return redirect(url_for('login'))


    time_threshold = datetime.now() - timedelta(hours=24)
    cursor.execute("DELETE FROM cart_items WHERE user_id = %s AND added_at < %s",
                   (session['user_id'], time_threshold))
    conn.commit()

    cursor.execute("""
        SELECT cart_items.id, food_items.name, food_items.price, food_items.image, cart_items.quantity, cart_items.food_id
        FROM cart_items
        JOIN food_items ON cart_items.food_id = food_items.id
        WHERE cart_items.user_id = %s
    """, (session['user_id'],))
    cart_items = cursor.fetchall()
    return render_template('cart.html', cart_items=cart_items)

@app.route('/order/single', methods=['POST'])
def order_single():
    if not session.get('user_id'):
        return jsonify({'success': False, 'error': 'Unauthorized'}), 401

    data = request.get_json()
    user_id = session.get('user_id')
    food_id = data['food_id']
    qty = int(data['quantity'])
    price = float(data['price'])
    total = qty * price

    try:
        conn, cursor = get_db_connection()

        # Stock validation
        cursor.execute("SELECT stock FROM daily_menu WHERE food_id = %s AND DATE(available_date) = CURDATE()", (food_id,))
        stock_data = cursor.fetchone()
        if not stock_data or stock_data['stock'] < qty:
            return jsonify({'success': False, 'error': 'Item is out of stock.'}), 400

        # Generate daily token
        token = _generate_daily_token_number()

        # Store info in Razorpay notes
        notes = {
            "user_id": str(user_id),
            "food_id": str(food_id),
            "quantity": str(qty),
            "price": str(price),
            "token_number": str(token)
        }

        razorpay_order = razorpay_client.order.create({
            "amount": int(total * 100),
            "currency": "INR",
            "receipt": f"single_{user_id}_{token}",
            "notes": notes
        })

        return jsonify({
            'success': True,
            'razorpay_order_id': razorpay_order['id'],
            'amount': int(total * 100),
            'key_id': RAZORPAY_KEY_ID,
            'user_name': session.get('name', 'Customer')
        })

    except Exception as e:
        print(f"Error creating single order: {e}")
        return jsonify({'success': False, 'error': 'Could not create order.'}), 500

@app.route('/cart/order', methods=['POST'])
def order_all_from_cart():
    conn, cursor = get_db_connection()
    if not session.get('user_id'):
        return jsonify({'success': False, 'error': 'Unauthorized'}), 401

    user_id = session.get('user_id')
    try:
        cursor.execute("""
            SELECT ci.food_id, ci.quantity, fi.price 
            FROM cart_items ci 
            JOIN food_items fi ON ci.food_id = fi.id 
            WHERE ci.user_id = %s
        """, (user_id,))
        items = cursor.fetchall()
        if not items:
            return jsonify({'success': False, 'error': 'Cart is empty'}), 400

        # ✅ Convert Decimals to float
        for item in items:
            item['quantity'] = int(item['quantity'])  # ensure integer
            item['price'] = float(item['price'])      # convert Decimal to float

        total = sum(item['price'] * item['quantity'] for item in items)
        token = _generate_daily_token_number()

        notes = {
            "user_id": str(user_id),
            "token_number": str(token),
            "items": json.dumps(items)  # ✅ No Decimal here now
        }

        razorpay_order = razorpay_client.order.create({
            "amount": int(total * 100),
            "currency": "INR",
            "receipt": f"cart_{user_id}_{token}",
            "notes": notes
        })

        return jsonify({
            'success': True,
            'razorpay_order_id': razorpay_order['id'],
            'amount': int(total * 100),
            'key_id': RAZORPAY_KEY_ID,
            'user_name': session.get('name', 'Customer')
        })


    except Exception as e:
        print(f"Error creating cart order: {e}")
        return jsonify({'success': False, 'error': 'Could not create cart order.'}), 500

    
@app.route('/payment/webhook', methods=['POST'])
def payment_webhook():
    print("⚡ Webhook hit!")
    webhook_body_bytes = request.data
    webhook_body_str = webhook_body_bytes.decode('utf-8')  # ✅ convert to string
    webhook_signature = request.headers.get('X-Razorpay-Signature')
    print(f"📦 Got signature: {webhook_signature}")

    try:
        # ✅ Fix: Pass decoded string
        razorpay_client.utility.verify_webhook_signature(
            webhook_body_str,
            webhook_signature,
            RAZORPAY_WEBHOOK_SECRET
        )
    except razorpay.errors.SignatureVerificationError:
        print("❌ Signature verification failed!")
        return 'Invalid signature', 400

    payload = json.loads(webhook_body_str)
    event = payload.get('event')
    print(f"🎯 Event received: {event}")

    if event == 'payment.captured':  # or 'order.paid' if that’s what Razorpay sends
        try:
            payment_entity = payload['payload']['payment']['entity']
            razorpay_order_id = payment_entity['order_id']
            razorpay_payment_id = payment_entity['id']
            notes = payment_entity.get('notes', {})

            user_id = int(notes['user_id'])
            token_number = int(notes['token_number'])

            if 'items' in notes:
                # 🛒 Cart order
                items = json.loads(notes['items'])
            else:
                # 🍽️ Single item order
                items = [{
                    'food_id': int(notes['food_id']),
                    'quantity': int(notes['quantity']),
                    'price': float(notes['price'])
                }]

            total = sum(item['quantity'] * item['price'] for item in items)

            conn, cursor = get_db_connection()
            cursor.execute("""
                INSERT INTO orders (user_id, total, token_number, payment_method, payment_status, status, razorpay_order_id, razorpay_payment_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (user_id, total, token_number, 'razorpay', 'paid', 'confirmed', razorpay_order_id, razorpay_payment_id))
            order_id = cursor.lastrowid

            # Save each item
            for item in items:
                cursor.execute("""
                    INSERT INTO order_items (order_id, food_id, quantity, price)
                    VALUES (%s, %s, %s, %s)
                """, (order_id, item['food_id'], item['quantity'], item['price']))

                cursor.execute("""
                    UPDATE daily_menu SET stock = stock - %s
                    WHERE food_id = %s AND DATE(available_date) = CURDATE()
                """, (item['quantity'], item['food_id']))

            conn.commit()

            # Remove admin notification
            create_notification(
               user_id=user_id,
               message=f"Payment successful! Your order #{token_number} is confirmed.",
               notif_type='payment_successful',
               related_id=order_id
            )

            print(f"✅ Order #{order_id} saved successfully after payment")

        except Exception as e:
            if conn:
                conn.rollback()
            print(f"❌ Database transaction rolled back due to: {e}")
        finally:
            if conn and conn.is_connected():
                cursor.close()
                conn.close()

    return 'OK', 200


@app.route('/cart/add', methods=['POST'])
def add_to_cart():
    conn, cursor = get_db_connection()
    if not session.get('user_id'):
        if request.is_json:
            return jsonify({'success': False, 'error': 'Unauthorized. Please log in.'}), 401
        return redirect('/login')

    data = request.get_json()
    user_id = session.get('user_id')
    food_id = data['food_id']
    qty_to_add = int(data['quantity'])
    current_time = datetime.now().time()
    today = date.today()

    cursor.execute("""
        SELECT stock FROM daily_menu
        WHERE food_id = %s
          AND DATE(available_date) = %s
          AND %s BETWEEN start_time AND end_time
          AND stock > 0
    """, (food_id, today, current_time))
    stock_row = cursor.fetchone()
    if not stock_row:
        return jsonify({'error': 'This food is not available today or current time.'}), 400

    available_stock = stock_row['stock']

    cursor.execute("""
        SELECT quantity FROM cart_items
        WHERE user_id = %s AND food_id = %s
    """, (user_id, food_id))
    cart_row = cursor.fetchone()

    current_qty = cart_row['quantity'] if cart_row else 0
    if current_qty + qty_to_add > available_stock:
        return jsonify({'error': f'Only {available_stock - current_qty} more can be added to cart.'}), 400

    if cart_row:
        cursor.execute("""
            UPDATE cart_items
            SET quantity = quantity + %s
            WHERE user_id = %s AND food_id = %s
        """, (qty_to_add, user_id, food_id))
    else:
        cursor.execute("""
            INSERT INTO cart_items (user_id, food_id, quantity, added_at)
            VALUES (%s, %s, %s, %s)
        """, (user_id, food_id, qty_to_add, datetime.now()))

    conn.commit()
    return jsonify({'success': True})


@app.route('/cart/update', methods=['POST'])
def update_cart():
    conn, cursor = get_db_connection()
    if not session.get('user_id'):
        if request.is_json:
            return jsonify({'success': False, 'error': 'Unauthorized. Please log in.'}), 401
        return '', 401
    
    data = request.get_json()
    cart_item_id = data['cart_item_id']
    action = data['action']
    if action == 'increase':
        cursor.execute("UPDATE cart_items SET quantity = quantity + 1 WHERE id = %s", (cart_item_id,))
    else:
        cursor.execute("UPDATE cart_items SET quantity = GREATEST(quantity - 1, 1) WHERE id = %s", (cart_item_id,))
    conn.commit()
    return '', 204

@app.route('/cart/remove', methods=['POST'])
def remove_cart():
    conn, cursor = get_db_connection()
    if not session.get('user_id'):
        if request.is_json:
            return jsonify({'success': False, 'error': 'Unauthorized. Please log in.'}), 401
        return '', 401

    data = request.get_json()
    cart_item_id = data['cart_item_id']
    cursor.execute("DELETE FROM cart_items WHERE id = %s", (cart_item_id,))
    conn.commit()
    return '', 204

@app.route('/order/cancel/<int:order_id>', methods=['POST'])
def cancel_order(order_id):
    conn, cursor = get_db_connection()
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'error': 'Unauthorized. Please log in.'}), 401

    try:
        # Check if the order can be cancelled and get its creation time
        cursor.execute("SELECT created_at, status FROM orders WHERE id = %s AND user_id = %s", (order_id, user_id))
        order = cursor.fetchone()

        if not order:
            return jsonify({'success': False, 'error': 'Order not found or unauthorized.'}), 404

        if order['status'] != 'pending':
            return jsonify({'success': False, 'error': 'Order can no longer be cancelled.'}), 400

        # Check if cancellation is within the 10-minute window
        time_diff_minutes = (datetime.now() - order['created_at']).total_seconds() / 60
        if time_diff_minutes > 10:
            return jsonify({'success': False, 'error': 'Cancellation window expired.'}), 400

        # 1. Get the items from the order before marking it as cancelled
        cursor.execute("SELECT food_id, quantity FROM order_items WHERE order_id = %s", (order_id,))
        items_to_restock = cursor.fetchall()

        # 2. Update the order status
        cursor.execute("UPDATE orders SET status = 'cancelled' WHERE id = %s", (order_id,))

        today = date.today()

        # 4. Loop through the fetched items and add the stock back to the daily menu
        for item in items_to_restock:
            cursor.execute("""
                UPDATE daily_menu SET stock = stock + %s 
                WHERE food_id = %s AND DATE(available_date) = %s
            """, (item['quantity'], item['food_id'], today))

        # 5. Commit all changes to the database at once
        conn.commit()

        return jsonify({'success': True, 'message': 'Order has been cancelled.'})

    except mysql.connector.Error as err:
        conn.rollback()
        print(f"Database error during cancellation: {err}")
        return jsonify({'success': False, 'error': 'A database error occurred.'}), 500

@app.route('/settings')
def settings():
    if not session.get('user_id'):
        return redirect('/login')
    
    conn, cursor = get_db_connection()
    cursor.execute("SELECT name, email, phone FROM users WHERE id = %s", (session['user_id'],))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    
    return render_template('settings.html', user=user)

@app.route('/logout', methods=['POST'])
def logout():
    session.clear() 
    return redirect('/login')

@app.route('/orders')
def orders():
    conn, cursor = get_db_connection()
    if not session.get('user_id'):
        return redirect('/login')

    cursor.execute("""
        SELECT id, token_number, total, status, created_at, payment_status
        FROM orders WHERE user_id = %s ORDER BY created_at DESC
    """, (session['user_id'],))
    all_orders = cursor.fetchall()

    today_orders = []
    past_orders = []
    now = datetime.now()
    today_date = now.date()

    for order in all_orders:
        order_items_list = []
        cursor.execute("""
            SELECT oi.quantity, fi.name, fi.image, fi.price
            FROM order_items oi
            JOIN food_items fi ON oi.food_id = fi.id
            WHERE oi.order_id = %s
        """, (order['id'],))
        items = cursor.fetchall()
        for item in items:
            order_items_list.append(item)
        order['items'] = order_items_list

        time_diff = now - order['created_at']
        order['can_cancel'] = order['status'] == 'pending' and time_diff.total_seconds() < 600
        order['time_to_cancel'] = max(0, 600 - int(time_diff.total_seconds()))

        qr_data = f"OrderID:{order['id']} Token:{order['token_number']}"
        qr_img = qrcode.make(qr_data)
        buf = io.BytesIO()
        qr_img.save(buf)
        buf.seek(0)
        order['qr'] = base64.b64encode(buf.read()).decode('utf-8')

        if order['created_at'].date() == today_date:
            today_orders.append(order)
        else:
            past_orders.append(order)

    return render_template('orders.html', today_orders=today_orders, past_orders=past_orders)

if __name__ == '__main__':
    app.run(host="0.0.0.0",debug=True, port=5055)