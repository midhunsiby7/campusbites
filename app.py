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
import razorpay
import threading
import pytz
import firebase_admin
from firebase_admin import credentials, auth
from dotenv import load_dotenv
from functools import wraps
import logging
from PIL import Image
import re
import traceback

# Load environment variables
load_dotenv()  # Add this line

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# At the top
app = Flask(__name__)


# Update all your configuration to use environment variables:
app.secret_key = os.getenv("FLASK_SECRET_KEY")
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax", 
    SESSION_COOKIE_SECURE=os.getenv("FLASK_ENV") == "production",  # Only secure in production
    PERMANENT_SESSION_LIFETIME=timedelta(days=7),
    MAX_CONTENT_LENGTH=5 * 1024 * 1024,  # 5MB max file size
)

# Database configuration
DB_CONFIG = {
    'host': os.getenv("DB_HOST"),
    'user': os.getenv("DB_USER"),
    'password': os.getenv("DB_PASSWORD"),
    'database': os.getenv("DB_NAME"),
    'port': os.getenv("DB_PORT"),
    'ssl_disabled': True,
    'autocommit': False
}

# Razorpay configuration
RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID")
RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET")
RAZORPAY_WEBHOOK_SECRET = os.getenv("RAZORPAY_WEBHOOK_SECRET")

# Initialize Razorpay client
razorpay_client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))

cred = credentials.Certificate("myserviceAccountKey.json")  # Download from Firebase Console > Project Settings > Service Accounts
firebase_admin.initialize_app(cred)

# Auto menu set time (HH:MM, 24h, IST). Change via .env if you want.
MENU_AUTOSET_TIME = os.getenv("MENU_AUTOSET_TIME", "05:00")  # 5:00 AM IST default
IST = pytz.timezone("Asia/Kolkata")

AUTOSET_FILE = ".lastautosetdate"

def get_last_autoset_date():
    if os.path.exists(AUTOSET_FILE):
        with open(AUTOSET_FILE, "r") as f:
            return f.read().strip()
    return None

def set_last_autoset_date(d):
    with open(AUTOSET_FILE, "w") as f:
        f.write(str(d))


def daily_task():
    ist = pytz.timezone("Asia/Kolkata")
    last_autoset_date = None  # keep outside the loop (module/global) so it persists
    def run_if_midnight_ist():
        now_ist = datetime.now(ist)
        hhmm = now_ist.strftime("%H:%M")
        if now_ist.hour == 15 and now_ist.minute == 12:
            _daily_cleanup_and_reset_at_startup()
        if now_ist.hour == 15 and now_ist.minute == 12:
            last_run = get_last_autoset_date()
            if last_run != str(now_ist.date()):
                try:
                    auto_set_menu_for_date(now_ist.date())
                    print(f"[AUTO-MENU] Set menu for {now_ist.date()} done..")
                    set_last_autoset_date(now_ist.date())
                except Exception as e:
                    print(f"[AUTO-MENU] Failed: {e}")

    while True:
        run_if_midnight_ist()
        time_module.sleep(60)  # check every minute
# Start the daily task thread
threading.Thread(target=daily_task, daemon=True).start()

def today_ist_date():
    return datetime.now(IST).date()

def weekday_key(d: date) -> str:
    # 0=Mon...6=Sun -> keys we used in SET
    keys = ['mon','tue','wed','thu','fri','sat','sun']
    return keys[d.weekday()]

def to_time(val):
    """Convert MySQL TIME (sometimes timedelta) to datetime.time"""
    if isinstance(val, timedelta):
        total_seconds = int(val.total_seconds())
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return time(hours, minutes, seconds)
    return val

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# Initialize Razorpay client
razorpay_client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))

 

def get_db_connection():
    if 'db_conn' not in g:
        g.db_conn = mysql.connector.connect(**DB_CONFIG)
        g.cursor = g.db_conn.cursor(dictionary=True, buffered=True)
    return g.db_conn, g.cursor

def auto_set_menu_for_date(target_date: date):
    """
    Auto-create daily_menu rows for given date using food_items defaults.
    - Cleans rows older than target_date.
    - Inserts rows for foods whose `days` include that weekday.
    - Does NOT overwrite stock of existing rows (only inserts missing items).
    - Uses category-specific default times.
    """
    conn = None
    cursor = None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True, buffered=True)

        # 1) Cleanup rows older than target_date
        cursor.execute("DELETE FROM daily_menu WHERE available_date < %s", (target_date,))

        # 2) Build day key and fetch foods for that day
        day_key = ['mon','tue','wed','thu','fri','sat','sun'][target_date.weekday()]
        cursor.execute("""
            SELECT id AS food_id, category,
                   COALESCE(default_stock, 10) AS d_stock,
                   default_breakfast_start, default_breakfast_end,
                   default_lunch_start, default_lunch_end, days
            FROM food_items
            WHERE available = 1
              AND (days IS NULL OR TRIM(days) = '' OR FIND_IN_SET(%s, days) > 0)
        """, (day_key,))
        foods = cursor.fetchall()

        # 3) Fetch already present food_ids for today
        cursor.execute("SELECT food_id FROM daily_menu WHERE available_date = %s", (target_date,))
        existing = {row['food_id'] for row in cursor.fetchall()}

        inserted = 0
        for f in foods:
            if f['food_id'] in existing:
                continue  # ✅ skip if already present (don't touch stock/times)

            if f['category'] == 'breakfast':
                s_time = f['default_breakfast_start'] or '08:00:00'
                e_time = f['default_breakfast_end']   or '11:00:00'
            else:
                s_time = f['default_lunch_start'] or '12:00:00'
                e_time = f['default_lunch_end']   or '15:00:00'

            cursor.execute("""
                INSERT INTO daily_menu (food_id, available_date, category, start_time, end_time, stock)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (f['food_id'], target_date, f['category'], s_time, e_time, f['d_stock']))
            inserted += 1

        conn.commit()
        print(f"[AUTO-MENU] Auto-set for {target_date}: inserted {inserted} new items (kept existing stock).")

    except Exception as e:
        if conn and getattr(conn, 'is_connected', lambda: False)():
            conn.rollback()
        print("[AUTO-MENU] ERROR:", e)
    finally:
        try:
            if cursor:
                cursor.close()
        except Exception:
            pass
        try:
            if conn and getattr(conn, 'is_connected', lambda: False)():
                conn.close()
        except Exception:
            pass


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
    """Simulated notification system (no DB save)."""
    print(f"[NOTIFICATION] To user {user_id} | Type: {notif_type} | Message: {message} | Related ID: {related_id}")


@app.after_request
def after_request(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    if request.is_secure:
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    return response




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
        startup_db_conn = mysql.connector.connect(**DB_CONFIG)
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

def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not session.get("user_id"):
            return redirect("/login")
        return f(*args, **kwargs)
    return wrapper

def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not session.get("admin_logged_in"):
            return redirect("/admin/login")
        return f(*args, **kwargs)
    return wrapper



@app.route('/')
def intro():
    return render_template('intro.html')

# Admin Login Page
@app.route('/admin/login', methods=['GET', 'POST'])
  # ADD this line
def admin_login():
    if session.get('admin_logged_in'):
        return redirect(url_for('admin_dashboard'))
    error = None
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        if not username or not password:
            error = "Username and password are required"
        else:
            conn, cursor = get_db_connection()
            cursor.execute("SELECT * FROM admin_users WHERE username = %s", (username,))
            admin = cursor.fetchone()
            if admin and check_password_hash(admin['password'], password):
                session['admin_logged_in'] = True
                session['admin_username'] = admin['username']
                session.permanent = True
                logger.info(f"Admin login successful: {username}")
                return redirect(url_for('admin_dashboard'))
            else:
                error = "Invalid credentials. Please try again."
                logger.warning(f"Failed admin login attempt: {username} from {request.remote_addr}")
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
        "apiKey": os.getenv("FIREBASE_API_KEY"),
        "authDomain": os.getenv("FIREBASE_AUTH_DOMAIN"),
        "projectId": os.getenv("FIREBASE_PROJECT_ID"),
        "storageBucket": os.getenv("FIREBASE_STORAGE_BUCKET"),
        "messagingSenderId": os.getenv("FIREBASE_MESSAGING_SENDER_ID"),
        "appId": os.getenv("FIREBASE_APP_ID"),
        "measurementId": os.getenv("FIREBASE_MEASUREMENT_ID")
    })

# Handle login data from frontend
@app.route("/firebase-login", methods=["POST"])
  # ADD this line
def firebase_login():
    data = request.get_json()
    id_token = data.get("idToken")
    name = data.get("name", "")
    phone = data.get("phone", "")

    if not id_token:
        return jsonify({"error": "ID token is required"}), 400
    
    # ADD input validation
    if name and len(name) > 100:
        return jsonify({"error": "Name too long"}), 400
    if phone and not re.match(r'^\+?[\d\s\-\(\)]{10,15}$', phone):
        return jsonify({"error": "Invalid phone format"}), 400

    try:
        decoded_token = auth.verify_id_token(id_token, clock_skew_seconds=60)
        email = decoded_token.get('email')
        
        if not email:
            return jsonify({"error": "Email not found in token"}), 400
        
        # ADD email validation
        if len(email) > 255 or not re.match(r'^[^@]+@[^@]+\.[^@]+$', email):
            return jsonify({"error": "Invalid email format"}), 400

    except Exception as e:
        logger.warning(f"Firebase token verification failed: {e}")
        return jsonify({"error": "Invalid token"}), 401

    conn, cursor = get_db_connection()

    cursor.execute("SELECT * FROM users WHERE email = %s LIMIT 1", (email,))
    user = cursor.fetchone()

    if not user:
        cursor.execute("""
            INSERT INTO users (email, name, phone, role)
            VALUES (%s, %s, %s, %s)
        """, (email, name, phone, 'student'))
        conn.commit()
        cursor.execute("SELECT * FROM users WHERE email = %s LIMIT 1", (email,))
        user = cursor.fetchone()

    session["user_id"] = user["id"]
    session["user_email"] = user["email"]
    session["user_name"] = user["name"] or email.split('@')[0]
    session["role"] = user.get("role", "student") if isinstance(user, dict) else "student"
    session.permanent = True

    need_profile = (user["name"] is None or user["name"] == "") or (user["phone"] is None or user["phone"] == "")

    logger.info(f"User login successful: {email}")
    return jsonify({
        "ok": True,
        "need_profile": bool(need_profile),
        "role": session["role"]
    })

# Admin Route Protection & Notifications ---

@app.route("/complete-profile", methods=["GET", "POST"])
@login_required
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
        

        return redirect("/home")

    return render_template("complete_profile.html")

@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    if not session.get('admin_logged_in'):
        return redirect('/admin/login')
    
    conn, cursor = get_db_connection()
    
    status_filter = request.args.get('status', 'all')
    sort_by = request.args.get('sort', 'newest')
    
    # SECURITY FIX: Validate parameters
    allowed_statuses = ['all', 'pending', 'confirmed', 'delivered', 'cancelled']
    allowed_sorts = ['newest', 'oldest']
    
    if status_filter not in allowed_statuses:
        status_filter = 'all'
    if sort_by not in allowed_sorts:
        sort_by = 'newest'
    
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
@admin_required
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
@admin_required
def add_food():
    conn, cursor = get_db_connection()
    if not session.get('admin_logged_in'):
        return redirect('/admin/login')

    if request.method == 'POST':
        # Basic fields
        name = request.form.get('name', '').strip()
        price_raw = request.form.get('price', '0').strip()
        try:
            price = float(price_raw) if price_raw != '' else 0.0
        except ValueError:
            price = 0.0
        category = request.form.get('category', 'breakfast')   # 'breakfast' or 'lunch'
        about = request.form.get('about', '').strip()

        # Days (checkboxes)
        days_list = request.form.getlist('days')  # e.g. ['mon','tue']
        days_str = ",".join(days_list) if days_list else "mon,tue,wed,thu,fri"

        # Default stock
        default_stock = int(request.form.get('default_stock', 10))

        # Per-category default times (admin may set both or only relevant set)
        db_default_breakfast_start = request.form.get('default_breakfast_start') or None
        db_default_breakfast_end   = request.form.get('default_breakfast_end') or None
        db_default_lunch_start     = request.form.get('default_lunch_start') or None
        db_default_lunch_end       = request.form.get('default_lunch_end') or None

        # For backward compatibility, set legacy default_start_time / end_time to the chosen cat's values
        if category == 'breakfast':
            legacy_start = db_default_breakfast_start or request.form.get('default_start_time') or '08:00:00'
            legacy_end   = db_default_breakfast_end   or request.form.get('default_end_time') or '11:00:00'
        else:
            legacy_start = db_default_lunch_start or request.form.get('default_start_time') or '12:00:00'
            legacy_end   = db_default_lunch_end   or request.form.get('default_end_time') or '15:00:00'

        # Image handling (optional)
        image = request.files.get('image')
        image_filename = None
        if image and image.filename != '' and allowed_file(image.filename):
            # use your process_and_save_image helper for consistent naming/processing
            processed = process_and_save_image(image, name)
            if processed:
                image_filename = processed

        # Save to DB
        cursor.execute("""
            INSERT INTO food_items
            (name, price, image, meal_type, stock, about, category, available,
             days, default_start_time, default_end_time, default_stock,
             default_breakfast_start, default_breakfast_end, default_lunch_start, default_lunch_end)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            name,
            price,
            image_filename,
            category,               # your table has meal_type -- keep consistent (you also have category)
            default_stock,         # stock column (initial stock)
            about,
            category,              # category col (breakfast/lunch)
            1,                     # available default true
            days_str,
            legacy_start,
            legacy_end,
            default_stock,
            db_default_breakfast_start,
            db_default_breakfast_end,
            db_default_lunch_start,
            db_default_lunch_end
        ))
        conn.commit()
        return redirect('/admin/add-food')

    # GET
    return render_template('add_food.html')

@app.route('/admin/foods/edit/<int:food_id>', methods=['GET', 'POST'])
@admin_required
def edit_food(food_id):
    conn, cursor = get_db_connection()
    if not session.get('admin_logged_in'):
        return redirect('/admin/login')

    # On POST: update
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        price_raw = request.form.get('price', '0').strip()
        try:
            price = float(price_raw) if price_raw != '' else 0.0
        except ValueError:
            price = 0.0

        category = request.form.get('category', 'breakfast')
        about = request.form.get('about', '').strip()
        available = int(request.form.get('available', 1))

        # Days
        days_list = request.form.getlist('days')
        days_str = ",".join(days_list) if days_list else ""

        default_stock = int(request.form.get('default_stock', 10))

        # Per-category times
        db_default_breakfast_start = request.form.get('default_breakfast_start') or None
        db_default_breakfast_end   = request.form.get('default_breakfast_end') or None
        db_default_lunch_start     = request.form.get('default_lunch_start') or None
        db_default_lunch_end       = request.form.get('default_lunch_end') or None

        # Legacy defaults (for backward compat)
        if category == 'breakfast':
            legacy_start = db_default_breakfast_start or request.form.get('default_start_time') or '08:00:00'
            legacy_end   = db_default_breakfast_end   or request.form.get('default_end_time') or '11:00:00'
        else:
            legacy_start = db_default_lunch_start or request.form.get('default_start_time') or '12:00:00'
            legacy_end   = db_default_lunch_end   or request.form.get('default_end_time') or '15:00:00'

        # Image handling (optional)
        image = request.files.get('image')
        image_url = None
        if image and image.filename != '' and allowed_file(image.filename):
            image_url = process_and_save_image(image, name)

        # Build UPDATE SQL (include image only if updated)
        if image_url:
            cursor.execute("""
                UPDATE food_items
                SET name=%s, price=%s, image=%s, category=%s, about=%s, available=%s, stock=%s,
                    days=%s,
                    default_start_time=%s, default_end_time=%s, default_stock=%s,
                    default_breakfast_start=%s, default_breakfast_end=%s,
                    default_lunch_start=%s, default_lunch_end=%s
                WHERE id=%s
            """, (
                name, price, image_url, category, about, available, default_stock,
                days_str,
                legacy_start, legacy_end, default_stock,
                db_default_breakfast_start, db_default_breakfast_end,
                db_default_lunch_start, db_default_lunch_end,
                food_id
            ))
        else:
            cursor.execute("""
                UPDATE food_items
                SET name=%s, price=%s, category=%s, about=%s, available=%s, stock=%s,
                    days=%s,
                    default_start_time=%s, default_end_time=%s, default_stock=%s,
                    default_breakfast_start=%s, default_breakfast_end=%s,
                    default_lunch_start=%s, default_lunch_end=%s
                WHERE id=%s
            """, (
                name, price, category, about, available, default_stock,
                days_str,
                legacy_start, legacy_end, default_stock,
                db_default_breakfast_start, db_default_breakfast_end,
                db_default_lunch_start, db_default_lunch_end,
                food_id
            ))

        conn.commit()
        return redirect('/admin/foods')

    # On GET: fetch row and render
    cursor.execute("SELECT * FROM food_items WHERE id = %s", (food_id,))
    food = cursor.fetchone()
    if food is None:
        return "Food item not found", 404

    return render_template('edit_food.html', food=food)


@app.route('/admin/foods/delete/<int:food_id>', methods=['POST'])
@admin_required
def delete_food(food_id):
    conn, cursor = get_db_connection()
    if not session.get('admin_logged_in'):
        return redirect('/admin/login')

    cursor.execute("DELETE FROM food_items WHERE id = %s", (food_id,))
    conn.commit()
    return redirect('/admin/foods')

@app.route('/admin/todays-menu', methods=['GET', 'POST'])
@admin_required
def admin_todays_menu():
    conn, cursor = get_db_connection()
    if not session.get('admin_logged_in'):
        return redirect('/admin/login')

    today = today_ist_date()

    # ---------- POST branch ----------
    if request.method == 'POST':
        action = request.args.get('action', 'set')

        if action == 'delete':
            cursor.execute("DELETE FROM daily_menu WHERE DATE(available_date) = %s", (today,))
            conn.commit()
            return redirect('/admin/todays-menu')

        elif action == 'edit':
    # Update breakfast & lunch times
            breakfast_start = request.form.get("breakfast_start")
            breakfast_end   = request.form.get("breakfast_end")
            lunch_start     = request.form.get("lunch_start")
            lunch_end       = request.form.get("lunch_end")

            cursor.execute("""
                UPDATE daily_menu 
                SET start_time=%s, end_time=%s 
                WHERE DATE(available_date)=%s AND category='breakfast'
            """, (breakfast_start, breakfast_end, today))
            cursor.execute("""
                UPDATE daily_menu 
                SET start_time=%s, end_time=%s 
                WHERE DATE(available_date)=%s AND category='lunch'
            """, (lunch_start, lunch_end, today))

            # Update stock for current items
            cursor.execute("SELECT food_id FROM daily_menu WHERE DATE(available_date)=%s", (today,))
            current_food_ids = [row['food_id'] for row in cursor.fetchall()]
            for food_id in current_food_ids:
                stock_val = request.form.get(f"stock_{food_id}")
                if stock_val is not None:
                    cursor.execute(
                        "UPDATE daily_menu SET stock=%s WHERE food_id=%s AND DATE(available_date)=%s",
                        (stock_val, food_id, today)
                    )

            # Add newly selected items
            new_food_ids = request.form.getlist("new_food_ids")
            for food_id in new_food_ids:
                stock_val = request.form.get(f"stock_new_{food_id}", 10)
                cursor.execute("SELECT category FROM food_items WHERE id=%s", (food_id,))
                category_row = cursor.fetchone()
                category = category_row['category'] if category_row else "other"

                start_time = breakfast_start if category == 'breakfast' else lunch_start
                end_time   = breakfast_end if category == 'breakfast' else lunch_end

                cursor.execute("""
                    INSERT INTO daily_menu (food_id, available_date, start_time, end_time, stock, category)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (food_id, today, start_time, end_time, stock_val, category))

            conn.commit()
            return redirect('/admin/todays-menu')

        else:  # action == 'set'
            breakfast_start = request.form.get("breakfast_start")
            breakfast_end   = request.form.get("breakfast_end")
            lunch_start     = request.form.get("lunch_start")
            lunch_end       = request.form.get("lunch_end")

            food_ids = request.form.getlist("food_ids")
            for food_id in food_ids:
                stock_val = request.form.get(f"stock_{food_id}", 10)
                cursor.execute("SELECT category FROM food_items WHERE id=%s", (food_id,))
                category_row = cursor.fetchone()
                category = category_row['category'] if category_row else "other"

                start_time = breakfast_start if category == 'breakfast' else lunch_start
                end_time   = breakfast_end if category == 'breakfast' else lunch_end

                cursor.execute("""
                    INSERT INTO daily_menu (food_id, available_date, start_time, end_time, stock, category)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (food_id, today, start_time, end_time, stock_val, category))

            conn.commit()
            return redirect('/admin/todays-menu')


    # ---------- GET branch ----------
    # Fetch today's menu (with food names)
    cursor.execute("""
        SELECT dm.*, fi.name, fi.category 
        FROM daily_menu dm
        JOIN food_items fi ON dm.food_id = fi.id
        WHERE DATE(dm.available_date) = %s
    """, (today,))
    data = cursor.fetchall()



    # ✅ Build today_menu grouped by category
    today_menu = {}
    breakfast_times = {'start': None, 'end': None}
    lunch_times = {'start': None, 'end': None}

    for item in data:
        category = item['category']
        if category not in today_menu:
            today_menu[category] = []
        today_menu[category].append(item)

        if category == 'breakfast' and breakfast_times['start'] is None:
            breakfast_times['start'] = to_time(item['start_time'])
            breakfast_times['end']   = to_time(item['end_time'])
        elif category == 'lunch' and lunch_times['start'] is None:
            lunch_times['start'] = to_time(item['start_time'])
            lunch_times['end']   = to_time(item['end_time'])

    # Foods not yet on menu
    current_menu_food_ids = {item['food_id'] for item in data}
    cursor.execute("SELECT * FROM food_items WHERE available = 1")
    all_foods = cursor.fetchall()
    foods_not_on_menu = [f for f in all_foods if f['id'] not in current_menu_food_ids]

    # Default times
    default_breakfast_start = "08:00"
    default_breakfast_end   = "23:00"
    default_lunch_start     = "12:00"
    default_lunch_end       = "23:00"

    return render_template(
        "todays_menu.html",
        today_menu=today_menu,
        foods=all_foods,
        foods_not_on_menu=foods_not_on_menu,
        breakfast_times=breakfast_times,
        lunch_times=lunch_times,
        default_breakfast_start=default_breakfast_start,
        default_breakfast_end=default_breakfast_end,
        default_lunch_start=default_lunch_start,
        default_lunch_end=default_lunch_end
    )


@app.route("/admin/run-auto-menu", methods=["POST"])
@admin_required
def run_auto_menu():
    today = datetime.now().date()
    try:
        auto_set_menu_for_date(today)
        return jsonify(success=True, message=f"Menu set for {today}")
    except Exception as e:
        return jsonify(success=False, message=str(e)), 500


@app.route('/admin/deliver/<int:order_id>', methods=['POST'])
@admin_required
def mark_delivered(order_id):
    conn, cursor = get_db_connection()
    if not session.get('admin_logged_in'):
        return redirect('/admin/login')

    # Admin can only deliver an order that has been confirmed (i.e., paid)
    cursor.execute("UPDATE orders SET status = 'delivered' WHERE id = %s AND status = 'confirmed'", (order_id,))
    conn.commit()   # ✅ FIX: commit the update

    # Notify user
    cursor.execute("SELECT user_id, token_number FROM orders WHERE id = %s", (order_id,))
    order_data = cursor.fetchone()
    if order_data:
        message = f"Your order #{order_data['token_number']} is out for delivery!"
        create_notification(order_data['user_id'], message, 'order_delivered', order_id)

    return redirect(url_for('admin_dashboard'))


@app.route('/admin/logout',methods=['POST'])
@admin_required
def admin_logout():
    session.pop('admin_logged_in', None)
    session.pop('admin_username', None)
    return redirect('/admin/login')

@app.route('/admin/collect/<int:order_id>', methods=['POST'])
@admin_required
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
@admin_required
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
@admin_required
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
@admin_required
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
@admin_required
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
@admin_required
def scan_qr():
    conn, cursor = get_db_connection()
    if not session.get('admin_logged_in'):
        return redirect('/admin/login')

    return render_template('scan_qr.html', order=None)

@app.route('/admin/scan_order/<int:order_id>')
@admin_required
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
@admin_required
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
@login_required
def home():
    if not session.get('user_id'):
        return redirect(url_for('login'))

    now = datetime.now(IST)   # use IST
    today = now.date()
    current_time = now.time()

    conn, cursor = get_db_connection()
    cursor.execute("""
        SELECT fi.*, dm.stock, dm.start_time, dm.end_time
        FROM food_items fi
        JOIN daily_menu dm ON fi.id = dm.food_id
        WHERE DATE(dm.available_date) = %s
          AND %s BETWEEN dm.start_time AND dm.end_time
          AND dm.stock > 0
          AND fi.available=1
    """, (today, current_time))
    foods = cursor.fetchall()

    return render_template("index.html", foods=foods)


@app.route('/food/<int:food_id>')
@login_required
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
@login_required
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

RESERVATION_TIMEOUT_MINUTES = 10  # change as needed


def release_expired_reservations(cursor, conn, minutes=RESERVATION_TIMEOUT_MINUTES):
    """
    Release any reserved rows older than `minutes`.
    """
    try:
        cursor.execute("""
            UPDATE daily_menu
            SET availability = 'available', reserved_by = NULL, reserved_at = NULL
            WHERE availability = 'reserved' AND reserved_at < DATE_SUB(NOW(), INTERVAL %s MINUTE)
        """, (minutes,))
        conn.commit()
    except Exception as e:
        # Log but don't crash the flow
        print("Error releasing expired reservations:", e)
        conn.rollback()

@app.route('/order/single', methods=['POST'])
@login_required
def order_single():
    if not session.get('user_id'):
        return jsonify({'success': False, 'error': 'Unauthorized'}), 401

    data = request.get_json()
    user_id = session.get('user_id')
    food_id = int(data['food_id'])
    qty = int(data.get('quantity', 1))
    price = float(data['price'])
    total = qty * price

    conn, cursor = None, None
    reserved_by_me = False
    try:
        conn, cursor = get_db_connection()
        # Release old expired reservations first
        release_expired_reservations(cursor, conn)

        # Start transaction to reserve atomically for last-item case
        conn.start_transaction()
        cursor.execute("""
            SELECT stock, availability
            FROM daily_menu
            WHERE food_id = %s AND DATE(available_date) = CURDATE()
            FOR UPDATE
        """, (food_id,))
        row = cursor.fetchone()

        if not row or row['stock'] < qty:
            conn.rollback()
            return jsonify({'success': False, 'error': 'Item is out of stock.'}), 400

        # Special handling only when this is the last stock
        if row['stock'] == 1 and qty == 1:
            if row['availability'] != 'available':
                conn.rollback()
                return jsonify({'success': False, 'error': 'Item is currently reserved by another user.'}), 400

            cursor.execute("""
                UPDATE daily_menu
                SET availability = 'reserved', reserved_by = %s, reserved_at = NOW()
                WHERE food_id = %s AND DATE(available_date) = CURDATE()
            """, (user_id, food_id))
            reserved_by_me = True

        # Commit reservation / or nothing if not last-item case
        conn.commit()

        # Generate token and Razorpay order
        token = _generate_daily_token_number()
        notes = {
            "user_id": str(user_id),
            "food_id": str(food_id),
            "quantity": str(qty),
            "price": str(price),
            "token_number": str(token)
        }

        try:
            razorpay_order = razorpay_client.order.create({
                "amount": int(total * 100),
                "currency": "INR",
                "receipt": f"single_{user_id}_{token}",
                "notes": notes
            })
        except Exception as e:
            # Razorpay order creation failed -> release reservation if we made one
            if reserved_by_me:
                cursor.execute("""
                    UPDATE daily_menu
                    SET availability = 'available', reserved_by = NULL, reserved_at = NULL
                    WHERE food_id = %s AND DATE(available_date) = CURDATE() AND reserved_by = %s
                """, (food_id, user_id))
                conn.commit()
            print("Error creating Razorpay order:", e)
            return jsonify({'success': False, 'error': 'Could not create payment order.'}), 500

        return jsonify({
            'success': True,
            'razorpay_order_id': razorpay_order['id'],
            'amount': int(total * 100),
            'key_id': RAZORPAY_KEY_ID,
            'user_name': session.get('name', 'Customer')
        })

    except Exception as e:
        if conn:
            conn.rollback()
        print("Error in order_single:", e)
        traceback.print_exc()
        return jsonify({'success': False, 'error': 'Could not create order.'}), 500
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()


@app.route('/cart/order', methods=['POST'])
@login_required
def order_all_from_cart():
    if not session.get('user_id'):
        return jsonify({'success': False, 'error': 'Unauthorized'}), 401

    user_id = session.get('user_id')
    conn, cursor = get_db_connection()

    try:
        # Fetch cart items with food info
        cursor.execute("""
            SELECT ci.food_id, ci.quantity, fi.price 
            FROM cart_items ci 
            JOIN food_items fi ON ci.food_id = fi.id 
            WHERE ci.user_id = %s
        """, (user_id,))
        items = cursor.fetchall()

        if not items:
            return jsonify({'success': False, 'error': 'Cart is empty'}), 400

        # Validate stock for each item
        for item in items:
            cursor.execute("""
                SELECT stock FROM daily_menu 
                WHERE food_id = %s AND DATE(available_date) = CURDATE()
            """, (item['food_id'],))
            stock_row = cursor.fetchone()
            if not stock_row or stock_row['stock'] < item['quantity']:
                cursor.execute("SELECT name FROM food_items WHERE id = %s", (item['food_id'],))
                food_name = cursor.fetchone()['name']
                return jsonify({'success': False, 'error': f'{food_name} is out of stock'}), 400

        # Convert Decimals to float
        for item in items:
            item['quantity'] = int(item['quantity'])
            item['price'] = float(item['price'])

        total = sum(item['price'] * item['quantity'] for item in items)

        # Sanity check
        if total <= 0 or total > 50000:
            return jsonify({'success': False, 'error': 'Invalid order total'}), 400

        token = _generate_daily_token_number()

        notes = {
            "user_id": str(user_id),
            "token_number": str(token),
            "items": json.dumps(items)
        }

        # Create Razorpay order
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
            'user_name': session.get('user_name', 'Customer')
        })

    except Exception as e:
        print(f"Error creating cart order: {e}")
        return jsonify({'success': False, 'error': 'Could not create cart order.'}), 500
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()



@app.route('/payment/webhook', methods=['POST'])
def payment_webhook():
    import traceback
    print("⚡ Webhook hit!")
    webhook_body_bytes = request.data
    try:
        webhook_body_str = webhook_body_bytes.decode('utf-8')
    except Exception:
        webhook_body_str = webhook_body_bytes  # fallback

    webhook_signature = request.headers.get('X-Razorpay-Signature')
    if not webhook_signature:
        print("❌ Missing webhook signature")
        return 'Missing signature', 400

    # Verify signature
    try:
        razorpay_client.utility.verify_webhook_signature(
            webhook_body_str,
            webhook_signature,
            RAZORPAY_WEBHOOK_SECRET
        )
    except Exception as e:
        print("❌ Signature verification failed!", e)
        return 'Invalid signature', 400

    try:
        payload = json.loads(webhook_body_str)
    except Exception as e:
        print("❌ Invalid JSON payload", e)
        return 'Bad payload', 400

    event = payload.get('event', '')
    print(f"🎯 Event received: {event}")

    # Only handle payment.captured and payment.failed
    if event not in ("payment.captured", "payment.failed"):
        print("Ignoring event:", event)
        return 'Ignored', 200

    # Handle payment.failed -> release any reservations made by this user (if notes contain user_id)
    if event == "payment.failed":
        try:
            payment_entity = payload['payload']['payment']['entity']
            notes = payment_entity.get('notes', {}) or {}
            user_id_note = notes.get('user_id')
            if user_id_note:
                conn, cursor = get_db_connection()
                try:
                    cursor.execute("""
                        UPDATE daily_menu
                        SET availability = 'available', reserved_by = NULL, reserved_at = NULL
                        WHERE reserved_by = %s AND availability = 'reserved'
                    """, (int(user_id_note),))
                    conn.commit()
                    print(f"Released reservations for user {user_id_note}")
                except Exception as err:
                    print("Error releasing reservations on payment.failed:", err)
                    conn.rollback()
                finally:
                    if conn and conn.is_connected():
                        cursor.close()
                        conn.close()
            else:
                print("No user_id in notes; nothing to release.")
        except Exception as e:
            print("Error processing payment.failed webhook:", e)
            traceback.print_exc()
        return 'OK', 200

    # From here: event == "payment.captured"
    try:
        payment_entity = payload['payload']['payment']['entity']
        razorpay_order_id = payment_entity.get('order_id')
        razorpay_payment_id = payment_entity.get('id')
        amount_paid = payment_entity.get('amount')  # paisa (int)
        notes = payment_entity.get('notes', {}) or {}

        # Validate presence of critical fields
        if not (razorpay_order_id and razorpay_payment_id and notes.get('user_id') and notes.get('token_number')):
            print("❌ Missing required fields in webhook notes/order info")
            return 'Invalid payload', 400

        user_id = int(notes['user_id'])
        token_number = int(notes['token_number'])

        # Build items list (cart or single)
        if 'items' in notes:
            try:
                items = json.loads(notes['items'])
            except Exception:
                print("❌ Invalid items JSON in notes")
                return 'Invalid payload', 400
        else:
            # single order expected fields: food_id, quantity, price
            try:
                items = [{
                    'food_id': int(notes['food_id']),
                    'quantity': int(notes['quantity']),
                    'price': float(notes['price'])
                }]
            except Exception as e:
                print("❌ Missing single-order fields in notes:", e)
                return 'Invalid payload', 400

        # Validate amount matches expected total
        expected_total = 0.0
        for it in items:
            expected_total += int(it['quantity']) * float(it['price'])

        if abs(amount_paid - (expected_total * 100)) > 1:
            print(f"❌ Payment amount mismatch: expected {expected_total*100}, got {amount_paid}")
            return 'Amount mismatch', 400

        # DB work
        conn, cursor = get_db_connection()
        # NOTE: do not call conn.start_transaction() — connector handles transactions
        try:
            # Idempotency check: payment already processed?
            cursor.execute("SELECT id FROM orders WHERE razorpay_payment_id = %s", (razorpay_payment_id,))
            if cursor.fetchone():
                print(f"⚠️ Duplicate webhook: payment {razorpay_payment_id} already processed")
                return 'Already processed', 200

            # Insert order row
            cursor.execute("""
                INSERT INTO orders (user_id, total, token_number, payment_method, payment_status, status, razorpay_order_id, razorpay_payment_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (user_id, expected_total, token_number, 'razorpay', 'paid', 'confirmed', razorpay_order_id, razorpay_payment_id))
            order_id = cursor.lastrowid

            # For each item: lock row, validate, update stock/availability, insert order_items
            for item in items:
                fid = int(item['food_id'])
                qty = int(item['quantity'])
                price = float(item['price'])

                # Lock the row for update to prevent concurrent modifications
                cursor.execute("""
                    SELECT stock, availability, reserved_by
                    FROM daily_menu
                    WHERE food_id = %s AND DATE(available_date) = CURDATE()
                    FOR UPDATE
                """, (fid,))
                dm = cursor.fetchone()
                if not dm:
                    # cannot fulfill -> rollback + refund
                    conn.rollback()
                    print(f"❌ No daily_menu row for food_id {fid}")
                    try:
                        razorpay_client.payment.refund(razorpay_payment_id, {'amount': amount_paid})
                        print("Attempted refund due to missing daily_menu row")
                    except Exception as ref_err:
                        print("Refund attempt failed:", ref_err)
                    return 'Fulfillment failed', 400

                if dm['stock'] < qty:
                    conn.rollback()
                    print(f"❌ Insufficient stock for food {fid}. needed {qty}, have {dm['stock']}")
                    try:
                        razorpay_client.payment.refund(razorpay_payment_id, {'amount': amount_paid})
                        print("Attempted refund due to insufficient stock")
                    except Exception as ref_err:
                        print("Refund attempt failed:", ref_err)
                    return 'Fulfillment failed', 400

                new_stock = dm['stock'] - qty
                new_availability = 'not_available' if new_stock <= 0 else 'available'

                cursor.execute("""
                    UPDATE daily_menu
                    SET stock = %s,
                        availability = %s,
                        reserved_by = NULL,
                        reserved_at = NULL
                    WHERE food_id = %s AND DATE(available_date) = CURDATE()
                """, (new_stock, new_availability, fid))

                cursor.execute("""
                    INSERT INTO order_items (order_id, food_id, quantity, price)
                    VALUES (%s, %s, %s, %s)
                """, (order_id, fid, qty, price))

            # If it was a cart order -> clear cart
            if 'items' in notes:
                try:
                    cursor.execute("DELETE FROM cart_items WHERE user_id = %s", (user_id,))
                except Exception as e:
                    print("Warning: Failed to clear cart_items:", e)

            # Commit everything
            conn.commit()

            # Create notification (non-blocking)
            try:
                create_notification(
                    user_id=user_id,
                    message=f"Payment successful! Your order #{token_number} is confirmed.",
                    notif_type='payment_successful',
                    related_id=order_id
                )
            except Exception as e:
                print("Warning: create_notification failed:", e)

            print(f"✅ Order #{order_id} saved successfully after payment")

        except Exception as db_err:
            # Ensure rollback and attempt refund if necessary
            try:
                conn.rollback()
            except Exception:
                pass
            print("❌ Database transaction rolled back due to:", db_err)
            traceback.print_exc()
            # Attempt refund as a fallback (best-effort)
            try:
                razorpay_client.payment.refund(razorpay_payment_id, {'amount': amount_paid})
                print("Attempted refund after DB failure")
            except Exception as ref_err:
                print("Refund attempt failed after DB failure:", ref_err)
            return 'Internal error', 500

    except Exception as e:
        print("❌ Error processing webhook:", e)
        traceback.print_exc()
        return 'Server error', 500
    finally:
        try:
            if conn and conn.is_connected():
                cursor.close()
                conn.close()
        except Exception:
            pass

    return 'OK', 200


@app.route('/cart/add', methods=['POST'])
@login_required 
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
@login_required
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
@login_required
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
@login_required
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
@login_required
def settings():
    if not session.get('user_id'):
        return redirect('/login')
    
    conn, cursor = get_db_connection()
    cursor.execute("SELECT name, email, phone FROM users WHERE id = %s", (session['user_id'],))
    user = cursor.fetchone()
    
    return render_template('settings.html', user=user)

@app.route('/logout', methods=['POST'])
@login_required
def logout():
    session.clear() 
    return redirect('/login')

@app.route('/orders')
@login_required
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

@app.errorhandler(mysql.connector.Error)
def handle_db_error(error):
    print(f"Database error: {error}")
    return jsonify({'error': 'Database operation failed'}), 500

@app.errorhandler(413)
def request_entity_too_large(error):
    return jsonify({'error': 'File too large. Max 5MB allowed.'}), 413

@app.errorhandler(429)
def ratelimit_handler(e):
    return jsonify({'error': 'Too many requests. Please try again later.'}), 429

if __name__ == '__main__':
    app.run(host="0.0.0.0",debug=True, port=5055)