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

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app = Flask(__name__)
app.secret_key = 'super-secret-key'

 

def get_db_connection():
    if 'db_conn' not in g:
        g.db_conn = mysql.connector.connect(
            host="127.0.0.1",
            user="root",
            password="8423",
            database="campusbites",
            ssl_disabled=True,
            autocommit=False 
        )
        g.cursor = g.db_conn.cursor(dictionary=True, buffered=True)
    return g.db_conn, g.cursor

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
            ssl_disabled=True,
            autocommit=False
        )
        startup_cursor = startup_db_conn.cursor(dictionary=True, buffered=True)

        yesterday = date.today() - timedelta(days=1)
        
        cleanup_flag_file = os.path.join(app.root_path, '.last_cleanup_date')
        last_cleanup_date_str = None
        if os.path.exists(cleanup_flag_file):
            with open(cleanup_flag_file, 'r') as f:
                last_cleanup_date_str = f.read().strip()
        
        if last_cleanup_date_str == str(date.today()):
            print(f"Cleanup for {date.today()} already performed during this app instance. Skipping.")
            return

        print(f"Running daily cleanup for {yesterday}...")

        startup_cursor.execute("""
            SELECT id, token_number, created_at
            FROM orders
            WHERE DATE(created_at) = %s AND status IN ('pending', 'confirmed')
        """, (yesterday,))
        uncollected_yesterday = startup_cursor.fetchall()

        for order in uncollected_yesterday:
            try:
                startup_cursor.execute("""
                    INSERT INTO uncollected_tokens (token_number, order_id, order_date, reason)
                    VALUES (%s, %s, %s, %s)
                """, (order['token_number'], order['id'], order['created_at'], 'Not Collected/Paid'))
            except mysql.connector.Error as err:
                if err.errno == 1062:
                    print(f"Warning: Token {order['token_number']} already in uncollected_tokens. Skipping insertion.")
                else:
                    raise err
        startup_db_conn.commit()
        print(f"Daily cleanup for {yesterday} completed. {len(uncollected_yesterday)} tokens saved.")

        with open(cleanup_flag_file, 'w') as f:
            f.write(str(date.today()))
        
    except Exception as e:
        if startup_db_conn and startup_db_conn.is_connected():
            startup_db_conn.rollback()
        print(f"CRITICAL ERROR during startup cleanup: {e}")
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
@app.route('/login', methods=['GET', 'POST'])
def login():
    conn, cursor = get_db_connection()
    if session.get('user_id'):
        return redirect('/home')

    error = None
    if request.method == 'POST':
        admission_number = request.form['admission_number']
        dob = request.form['dob'] 

        cursor.execute("SELECT * FROM users WHERE admission_number = %s AND dob = %s LIMIT 1", (admission_number, dob))
        user = cursor.fetchone()
        if user:
            session['user_id'] = user['id']
            session['name'] = user['name']
            session['role'] = user['role']
            session.permanent = True
            return redirect('/home')
        else:
            error = "Invalid Admission Number or DOB."
    return render_template('login.html', error=error)

# Admin Route Protection & Notifications ---

@app.route('/admin/dashboard')
def admin_dashboard():
    conn, cursor = get_db_connection()
    if not session.get('admin_logged_in'):
        return redirect('/admin/login')

    status_filter = request.args.get('status', 'all')
    sort_by = request.args.get('sort', 'newest')
    search_query = request.args.get('search', '').lower().strip()

    query = """
        SELECT orders.id, orders.token_number, orders.status,
               users.name AS user_name, users.admission_number,
               orders.created_at, orders.total
        FROM orders
        JOIN users ON orders.user_id = users.id
        WHERE DATE(orders.created_at) = %s
    """
    params = [datetime.now().date()]

    if status_filter != 'all':
        query += " AND orders.status = %s"
        params.append(status_filter)

    if search_query:
        query += " AND (LOWER(users.name) LIKE %s OR CAST(orders.token_number AS CHAR) LIKE %s)"
        params.extend([f"%{search_query}%", f"%{search_query}%"])

    query += " ORDER BY orders.created_at DESC" if sort_by == 'newest' else " ORDER BY orders.created_at ASC"

    cursor.execute(query, tuple(params))
    orders = cursor.fetchall()

    now = datetime.now()
    for order in orders:
        if 'created_at' in order and order['created_at']:
            elapsed = now - order['created_at']
            secs = int(elapsed.total_seconds())
            order['is_confirmable'] = order['status'] == 'pending' and secs >= 600

            if secs < 60:
                order['time_ago'] = f"{secs} seconds ago"
            elif secs < 3600:
                mins = secs // 60
                order['time_ago'] = f"{mins} minute{'s' if mins != 1 else ''} ago"
            elif secs < 86400:
                hrs = secs // 3600
                mins = (secs % 3600) // 60
                order['time_ago'] = f"{hrs} hour{'s' if hrs != 1 else ''}" + (f" {mins} minutes" if mins else "") + " ago"
            else:
                order['time_ago'] = order['created_at'].strftime('%Y-%m-%d %H:%M')
        else:
            order['is_confirmable'] = False
            order['time_ago'] = "N/A"

    return render_template('admin_dashboard.html',
                           orders=orders,
                           selected_status=status_filter,
                           selected_sort=sort_by,
                           search_query=search_query)

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

    cursor.execute("UPDATE orders SET status = 'delivered' WHERE id = %s", (order_id,))
    conn.commit()
    cursor.execute("UPDATE order_history SET status = %s WHERE order_id = %s", ('delivered', order_id))
    conn.commit()
    return redirect('/admin/dashboard')

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
               u.name AS user_name, u.admission_number,
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

    return render_template("admin_order_view.html", order=order_main_info, items=items, is_confirmable_now=is_confirmable_now)

@app.route('/admin/orders/confirm/<int:order_id>', methods=['POST'])
def confirm_order(order_id):
    conn, cursor = get_db_connection()
    if not session.get('admin_logged_in'):
        return redirect('/admin/login')

    cursor.execute("SELECT created_at, user_id, token_number FROM orders WHERE id = %s", (order_id,))
    order_data = cursor.fetchone()

    if not order_data:
        return "Order not found", 404

    order_creation_time = order_data['created_at']
    time_elapsed = datetime.now() - order_creation_time

    if time_elapsed.total_seconds() < 600:
        return "Cannot confirm order yet. User cancellation window is still open.", 400

    cursor.execute("UPDATE orders SET status = 'confirmed' WHERE id = %s", (order_id,))
    conn.commit()
    cursor.execute("UPDATE order_history SET status = %s WHERE order_id = %s", ('confirmed', order_id))
    conn.commit()
    session['user_notification'] = {'user_id': order_data['user_id'], 'message': f"Your order #{order_data['token_number']} has been confirmed!", 'type': 'confirmed_order'}
    session['admin_notification'] = {'admin_username': 'any', 'message': f"Order #{order_data['token_number']} confirmed from Dashboard.", 'type': 'order_confirmed_from_dashboard', 'order_id': order_id}
    return redirect('/admin/dashboard')

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
               u.name AS user_name, u.admission_number,
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
def admin_uncollected_tokens():
    conn, cursor = get_db_connection()
    if not session.get('admin_logged_in'):
        return redirect('/admin/login')

    cursor.execute("""
        SELECT 
            ut.token_number, 
            ut.order_date, 
            ut.reason,
            ut.order_id,
            o.status AS order_status,
            u.name AS user_name, 
            u.admission_number
        FROM uncollected_tokens ut
        LEFT JOIN orders o ON ut.order_id = o.id
        LEFT JOIN users u ON o.user_id = u.id
        ORDER BY ut.order_date DESC
    """)
    uncollected_data_raw = cursor.fetchall()

    uncollected_data_json_ready = []
    for record in uncollected_data_raw:
        record_copy = record.copy()
        if 'order_date' in record_copy and isinstance(record_copy['order_date'], datetime):
            record_copy['order_date'] = record_copy['order_date'].strftime('%Y-%m-%d %H:%M:%S')
        uncollected_data_json_ready.append(record_copy)

    return jsonify(uncollected_data_json_ready)


@app.route('/api/live-stock')
def live_stock():
    conn, cursor = get_db_connection()
    today = datetime.now().date()
    cursor.execute("SELECT food_id, stock FROM daily_menu WHERE DATE(available_date) = %s", (today,))
    stock_data = cursor.fetchall()
    return jsonify({str(row['food_id']): row['stock'] for row in stock_data})

@app.route('/api/notifications')
def get_notifications():
    """Unified API to fetch unread notifications for users and admins."""
    user_id, is_admin = session.get('user_id'), session.get('admin_logged_in')
    if not user_id and not is_admin: return jsonify([])

    conn, cursor = get_db_connection()
    query, params = "", []

    if is_admin:
        query = "SELECT * FROM notifications WHERE is_admin_notification = TRUE AND is_read = FALSE ORDER BY created_at DESC"
    else:
        query = "SELECT * FROM notifications WHERE user_id = %s AND is_admin_notification = FALSE AND is_read = FALSE ORDER BY created_at DESC"
        params.append(user_id)
    
    cursor.execute(query, tuple(params))
    notifications = cursor.fetchall()
    
    for n in notifications:
        if isinstance(n.get('created_at'), (datetime, date)):
            n['created_at'] = n['created_at'].isoformat()
    return jsonify(notifications)

@app.route('/api/notifications/mark-read', methods=['POST'])
def mark_notifications_read():
    """Marks specific notifications as read."""
    if not (session.get('user_id') or session.get('admin_logged_in')):
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.get_json()
    notification_ids = data.get('ids')
    if not isinstance(notification_ids, list) or not notification_ids:
        return jsonify({'error': 'Invalid payload'}), 400

    conn, cursor = get_db_connection()
    placeholders = ','.join(['%s'] * len(notification_ids))
    query = f"UPDATE notifications SET is_read = TRUE WHERE id IN ({placeholders})"
    
    cursor.execute(query, tuple(notification_ids))
    return jsonify({'success': True}), 200

@app.route('/home')
def home():
    conn, cursor = get_db_connection()
    if not session.get('user_id'):
        return redirect('/login')

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
        return redirect('/login')

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
    conn, cursor = get_db_connection()
    if not session.get('user_id'):
        return jsonify({'success': False, 'error': 'Unauthorized. Please log in.'}), 401

    data = request.get_json()
    user_id = session.get('user_id')
    food_id = data['food_id']
    qty = int(data['quantity'])
    price = float(data['price'])
    total = qty * price
    
    try:
        cursor.execute("""
            SELECT stock FROM daily_menu
            WHERE food_id = %s AND DATE(available_date) = CURDATE() AND %s BETWEEN start_time AND end_time
        """, (food_id, datetime.now().time()))
        stock_data = cursor.fetchone()

        if not stock_data or stock_data['stock'] < qty:
            return jsonify({'error': 'Food is out of stock or unavailable at this time.'}), 400

        token = _generate_daily_token_number()
        
        cursor.execute("INSERT INTO orders (user_id, total, token_number) VALUES (%s, %s, %s)",
                       (user_id, total, token))
        order_id = cursor.lastrowid

        # Insert into permanent order history table
        order_items = {
           'food_id': food_id,
           'quantity': qty,
           'price': price
        }

        cursor.execute("""
    INSERT INTO order_history 
    (order_id, token_number, user_id, user_name, admission_number, items, total_price, status)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
""", (
    order_id,
    token,
    user_id,
    session.get('name'),
    session.get('admission_number'),
    json.dumps(order_items),
    total,
    'pending'
))


        cursor.execute("INSERT INTO order_items (order_id, food_id, quantity, price) VALUES (%s, %s, %s, %s)",
                       (order_id, food_id, qty, price))

        cursor.execute("UPDATE daily_menu SET stock = stock - %s WHERE food_id = %s AND DATE(available_date) = CURDATE()", 
                       (qty, food_id))

        message = f"New Order! Token #{token} by {session.get('name', 'Unknown')}."
        create_notification(user_id=None, message=message, notif_type='new_order', related_id=order_id, is_admin=True)
                
        return jsonify({'success': True})

    except mysql.connector.Error as err:
        conn.rollback()
        print(f"Error during order/single: {err}")
        if err.errno == 1062:
            return jsonify({'success': False, 'error': 'Order failed due to a temporary token conflict. Please try again.'}), 500
        return jsonify({'success': False, 'error': f'A database error occurred: {err.msg}'}), 500

@app.route('/cart/order', methods=['POST'])
def order_all_from_cart():
    conn, cursor = get_db_connection()
    if not session.get('user_id'):
        return jsonify({'success': False, 'error': 'Unauthorized. Please log in.'}), 401

    user_id = session.get('user_id')
    today = datetime.now().date()
    current_time = datetime.now().time()

    try:
        cursor.execute("""
            SELECT ci.food_id, ci.quantity, fi.price, dm.stock 
            FROM cart_items ci
            JOIN food_items fi ON ci.food_id = fi.id
            JOIN daily_menu dm ON ci.food_id = dm.food_id AND DATE(dm.available_date) = %s
            WHERE ci.user_id = %s
        """, (today, user_id))
        items = cursor.fetchall()

        if not items:
            return jsonify({'error': 'Your cart is empty.'}), 400

        for item in items:
            if item['stock'] < item['quantity']:
                return jsonify({'success': False, 'error': 'One or more items in your cart are out of stock.'}), 400

        total = sum(item['price'] * item['quantity'] for item in items)
        token = _generate_daily_token_number()

        cursor.execute("INSERT INTO orders (user_id, total, token_number) VALUES (%s, %s, %s)",
                       (user_id, total, token))
        order_id = cursor.lastrowid

        # Prepare and insert order history entry
        order_items_for_history = [
    {
        'food_id': int(item['food_id']),
        'quantity': int(item['quantity']),
        'price': float(item['price'])
    }
    for item in items
]

        cursor.execute("""
            INSERT INTO order_history 
            (order_id, token_number, user_id, user_name, admission_number, items, total_price, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            order_id,
            token,
            user_id,
            session.get('name'),
            session.get('admission_number'),
            json.dumps(order_items_for_history),
            total,
            'pending'
        ))

        # Add items to order_items and update stock
        for item in items:
            cursor.execute("INSERT INTO order_items (order_id, food_id, quantity, price) VALUES (%s, %s, %s, %s)",
                           (order_id, item['food_id'], item['quantity'], item['price']))
            cursor.execute("UPDATE daily_menu SET stock = stock - %s WHERE food_id = %s AND DATE(available_date) = %s",
                           (item['quantity'], item['food_id'], today))

        # Clear the cart
        cursor.execute("DELETE FROM cart_items WHERE user_id = %s", (user_id,))

        # Notify admins
        message = f"New Cart Order! Token #{token} by {session.get('name', 'Unknown')}."
        create_notification(user_id=None, message=message, notif_type='new_order', related_id=order_id, is_admin=True)

        conn.commit()
        return jsonify({'success': True}), 200

    except mysql.connector.Error as err:
        conn.rollback()
        print(f"Error during cart/order: {err}")
        if err.errno == 1062:
            return jsonify({'success': False, 'error': 'Order failed due to a temporary token conflict. Please try again.'}), 500
        return jsonify({'success': False, 'error': f'A database error occurred: {err.msg}'}), 500


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
    return render_template('settings.html')

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
        SELECT id, token_number, total, status, created_at
        FROM orders
        WHERE user_id = %s
        ORDER BY created_at DESC
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

if __name__ == "__main__":
    _daily_cleanup_and_reset_at_startup()
    app.run(host="0.0.0.0", port=5055, debug=True)
