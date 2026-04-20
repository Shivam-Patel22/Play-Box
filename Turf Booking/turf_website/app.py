import os
import uuid
import sqlite3
import hashlib
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, flash

app = Flask(__name__)
app.secret_key = 'super_secret_key_for_turf_booking'

DB_PATH = 'turf_booking.db'
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_image(file):
    """Save uploaded image and return its relative URL path."""
    if file and file.filename and allowed_file(file.filename):
        ext = file.filename.rsplit('.', 1)[1].lower()
        filename = f"{uuid.uuid4().hex}.{ext}"
        file.save(os.path.join(UPLOAD_FOLDER, filename))
        return f"uploads/{filename}"
    return None

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        phone TEXT NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL CHECK(role IN ('Customer', 'Admin'))
    )''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS turfs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        owner_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        sport TEXT NOT NULL,
        area TEXT NOT NULL,
        location TEXT NOT NULL,
        price_per_hour REAL NOT NULL,
        available_slots INTEGER NOT NULL,
        description TEXT,
        image_path TEXT,
        FOREIGN KEY(owner_id) REFERENCES users(id)
    )''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS bookings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER NOT NULL,
        turf_id INTEGER NOT NULL,
        booking_date TEXT NOT NULL,
        start_time TEXT NOT NULL,
        end_time TEXT NOT NULL,
        total_price REAL NOT NULL,
        status TEXT NOT NULL CHECK(status IN ('Pending', 'Confirmed', 'Rejected', 'Cancelled')),
        payment_status TEXT NOT NULL CHECK(payment_status IN ('Pending', 'Paid', 'Refunded')),
        FOREIGN KEY(customer_id) REFERENCES users(id),
        FOREIGN KEY(turf_id) REFERENCES turfs(id)
    )''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS payments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        booking_id INTEGER NOT NULL,
        customer_id INTEGER NOT NULL,
        amount REAL NOT NULL,
        method TEXT NOT NULL,
        transaction_id TEXT NOT NULL,
        timestamp TEXT NOT NULL,
        FOREIGN KEY(booking_id) REFERENCES bookings(id),
        FOREIGN KEY(customer_id) REFERENCES users(id)
    )''')
    
    # Seeding Admin
    cursor.execute("SELECT id FROM users WHERE email='admin@turfbooking.com'")
    if not cursor.fetchone():
        admin_pass = hash_password('admin123')
        cursor.execute("INSERT INTO users (full_name, email, phone, password_hash, role) VALUES (?, ?, ?, ?, ?)", 
                       ('System Admin', 'admin@turfbooking.com', '9999999999', admin_pass, 'Admin'))
    
    conn.commit()
    conn.close()

@app.route('/')
def index():
    conn = get_db()
    popular_turfs = conn.execute("SELECT * FROM turfs ORDER BY id DESC LIMIT 3").fetchall()
    conn.close()
    return render_template('index.html', popular_turfs=popular_turfs)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        hashed_pw = hash_password(password)
        
        conn = get_db()
        user = conn.execute("SELECT * FROM users WHERE email=? AND password_hash=?", (email, hashed_pw)).fetchone()
        conn.close()
        
        if user:
            session['user_id'] = user['id']
            session['full_name'] = user['full_name']
            session['role'] = user['role']
            return redirect(url_for('index'))
        else:
            flash('Invalid email or password', 'error')
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        password = request.form.get('password', '')
        role = request.form.get('role', '')

        if not full_name or not email or not phone or not password or not role:
            flash('All fields are compulsory to fill!', 'error')
            return redirect(url_for('signup'))
            
        if len(phone) != 10 or not phone.isdigit():
            flash('Phone number must be exactly 10 digits.', 'error')
            return redirect(url_for('signup'))
            
        if len(password) < 8:
            flash('Password must be at least 8 characters long.', 'error')
            return redirect(url_for('signup'))
        
        hashed_pw = hash_password(password)
        conn = get_db()
        try:
            conn.execute("INSERT INTO users (full_name, email, phone, password_hash, role) VALUES (?, ?, ?, ?, ?)",
                         (full_name, email, phone, hashed_pw, role))
            conn.commit()
            flash('Account created successfully! Please log in.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Email already exists!', 'error')
        finally:
            conn.close()
    return render_template('signup.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/customer')
def customer_dashboard():
    if 'user_id' not in session or session['role'] != 'Customer':
        return redirect(url_for('login'))
        
    search = request.args.get('search', '')
    sport = request.args.get('sport', '')
    area = request.args.get('area', '')
    
    conn = get_db()
    query = "SELECT * FROM turfs WHERE 1=1"
    params = []
    
    if search:
        query += " AND (LOWER(name) LIKE LOWER(?) OR LOWER(location) LIKE LOWER(?) OR LOWER(area) LIKE LOWER(?) OR LOWER(sport) LIKE LOWER(?))"
        pattern = f"%{search}%"
        params.extend([pattern, pattern, pattern, pattern])
    if sport:
        query += " AND sport = ?"
        params.append(sport)
    if area:
        query += " AND area = ?"
        params.append(area)
        
    turfs = conn.execute(query, params).fetchall()
    sports = conn.execute("SELECT DISTINCT sport FROM turfs WHERE sport IS NOT NULL AND sport != '' ORDER BY sport").fetchall()
    areas = conn.execute("SELECT DISTINCT area FROM turfs WHERE area IS NOT NULL AND area != '' ORDER BY area").fetchall()
    conn.close()
    return render_template('customer_dashboard.html', turfs=turfs, sports=sports, areas=areas, current_search=search, current_sport=sport, current_area=area)

@app.route('/book/<int:turf_id>', methods=['GET', 'POST'])
def book_turf(turf_id):
    if 'user_id' not in session or session['role'] != 'Customer':
        return redirect(url_for('login'))
        
    conn = get_db()
    turf = conn.execute("SELECT * FROM turfs WHERE id=?", (turf_id,)).fetchone()
    
    if not turf:
        flash('Turf not found.', 'error')
        conn.close()
        return redirect(url_for('customer_dashboard'))
        
    if turf['available_slots'] <= 0:
        flash('This turf is fully booked.', 'error')
        conn.close()
        return redirect(url_for('customer_dashboard'))
        
    if request.method == 'POST':
        booking_date = request.form['booking_date']
        start_time = request.form['start_time']
        end_time = request.form['end_time']
        
        try:
            booking_date_obj = datetime.strptime(booking_date, '%Y-%m-%d').date()
            today = datetime.now().date()
            if booking_date_obj < today:
                flash('Cannot book for past dates.', 'error')
                conn.close()
                return redirect(request.url)
            
            # Check for past times if booking for today
            if booking_date_obj == today:
                now_time = datetime.now().time()
                start_time_obj = datetime.strptime(start_time, '%H:%M').time()
                if start_time_obj <= now_time:
                    flash('Cannot book for a past time today.', 'error')
                    conn.close()
                    return redirect(request.url)
        except ValueError:
            flash('Invalid date format.', 'error')
            conn.close()
            return redirect(request.url)
        
        fmt = '%H:%M'
        try:
            dt_start = datetime.strptime(start_time, fmt)
            dt_end = datetime.strptime(end_time, fmt)
            if end_time == "00:00":
                from datetime import timedelta
                dt_end += timedelta(days=1)
                
            tdelta = dt_end - dt_start
            hours = tdelta.total_seconds() / 3600
        except ValueError:
            flash('Invalid time format.', 'error')
            conn.close()
            return redirect(request.url)

        if hours <= 0:
            flash('End time must be after start time.', 'error')
            conn.close()
            return redirect(request.url)
            
        total_price = hours * turf['price_per_hour']
        
        conn.execute('''
            INSERT INTO bookings (customer_id, turf_id, booking_date, start_time, end_time, total_price, status, payment_status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (session['user_id'], turf_id, booking_date, start_time, end_time, total_price, 'Pending', 'Pending'))
        conn.commit()
        conn.close()
        
        flash('Booking created successfully! Pending manual payment.', 'success')
        return redirect(url_for('my_bookings'))
        
    conn.close()
    return render_template('book.html', turf=turf)

@app.route('/my_bookings')
def my_bookings():
    if 'user_id' not in session or session['role'] != 'Customer':
        return redirect(url_for('login'))
        
    conn = get_db()
    bookings = conn.execute('''
        SELECT b.*, t.name as turf_name, t.sport as turf_sport 
        FROM bookings b 
        JOIN turfs t ON b.turf_id = t.id 
        WHERE b.customer_id = ?
        ORDER BY b.id DESC
    ''', (session['user_id'],)).fetchall()
    conn.close()
    
    return render_template('my_bookings.html', bookings=bookings)

@app.route('/cancel_booking/<int:booking_id>', methods=['POST'])
def cancel_booking(booking_id):
    if 'user_id' not in session or session['role'] != 'Customer':
        return redirect(url_for('login'))
        
    conn = get_db()
    booking = conn.execute("SELECT * FROM bookings WHERE id=? AND customer_id=?", (booking_id, session['user_id'])).fetchone()
    
    if booking and booking['status'] == 'Pending':
        conn.execute("UPDATE bookings SET status='Cancelled' WHERE id=?", (booking_id,))
        conn.commit()
        flash('Booking cancelled.', 'success')
    else:
        flash('Cannot cancel this booking.', 'error')
        
    conn.close()
    return redirect(url_for('my_bookings'))

@app.route('/admin')
def admin_dashboard():
    if 'user_id' not in session or session['role'] != 'Admin':
        return redirect(url_for('login'))
        
    conn = get_db()
    turfs = conn.execute("SELECT * FROM turfs WHERE owner_id=?", (session['user_id'],)).fetchall()
    
    pending_bookings = conn.execute('''
        SELECT b.*, t.name as turf_name, u.full_name as customer_name, u.phone as customer_phone
        FROM bookings b
        JOIN turfs t ON b.turf_id = t.id
        JOIN users u ON b.customer_id = u.id
        WHERE t.owner_id = ? AND b.status = "Pending"
        ORDER BY b.id DESC
    ''', (session['user_id'],)).fetchall()
    
    conn.close()
    return render_template('admin_dashboard.html', turfs=turfs, pending_bookings=pending_bookings)

@app.route('/add_turf', methods=['GET', 'POST'])
def add_turf():
    if 'user_id' not in session or session['role'] != 'Admin':
        return redirect(url_for('login'))
        
    if request.method == 'POST':
        name = request.form['name']
        sport = request.form['sport']
        area = request.form['area']
        location = request.form['location']
        price_str = request.form['price_per_hour']
        slots_str = request.form['available_slots']
        desc = request.form['description']
        image_path = save_image(request.files.get('image')) or ''

        try:
            price = float(price_str)
            slots = int(slots_str)
            if price < 0 or slots < 0:
                flash('Price and slots must be valid positive numbers.', 'error')
                return redirect(request.url)
        except ValueError:
            flash('Invalid price or slots value.', 'error')
            return redirect(request.url)
        
        conn = get_db()
        conn.execute('''
            INSERT INTO turfs (owner_id, name, sport, area, location, price_per_hour, available_slots, description, image_path)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (session['user_id'], name, sport, area, location, price, slots, desc, image_path))
        conn.commit()
        conn.close()
        flash('Turf added successfully!', 'success')
        return redirect(url_for('admin_dashboard'))
        
    return render_template('add_turf.html')

@app.route('/edit_turf/<int:turf_id>', methods=['GET', 'POST'])
def edit_turf(turf_id):
    if 'user_id' not in session or session['role'] != 'Admin':
        return redirect(url_for('login'))
        
    conn = get_db()
    turf = conn.execute("SELECT * FROM turfs WHERE id=? AND owner_id=?", (turf_id, session['user_id'])).fetchone()
    
    if not turf:
        flash('Turf not found or unauthorized.', 'error')
        conn.close()
        return redirect(url_for('admin_dashboard'))
        
    if request.method == 'POST':
        name = request.form['name']
        sport = request.form['sport']
        area = request.form['area']
        location = request.form['location']
        price_str = request.form['price_per_hour']
        slots_str = request.form['available_slots']
        desc = request.form['description']
        new_image = save_image(request.files.get('image'))
        image_path = new_image if new_image else turf['image_path']

        try:
            price = float(price_str)
            slots = int(slots_str)
            if price < 0 or slots < 0:
                flash('Price and slots must be valid positive numbers.', 'error')
                conn.close()
                return redirect(request.url)
        except ValueError:
            flash('Invalid price or slots value.', 'error')
            conn.close()
            return redirect(request.url)
        
        conn.execute('''
            UPDATE turfs SET name=?, sport=?, area=?, location=?, price_per_hour=?, available_slots=?, description=?, image_path=?
            WHERE id=? AND owner_id=?
        ''', (name, sport, area, location, price, slots, desc, image_path, turf_id, session['user_id']))
        conn.commit()
        conn.close()
        flash('Turf updated successfully!', 'success')
        return redirect(url_for('admin_dashboard'))
        
    conn.close()
    return render_template('edit_turf.html', turf=turf)

@app.route('/delete_turf/<int:turf_id>', methods=['POST'])
def delete_turf(turf_id):
    if 'user_id' not in session or session['role'] != 'Admin':
        return redirect(url_for('login'))
        
    conn = get_db()
    turf = conn.execute("SELECT id FROM turfs WHERE id=? AND owner_id=?", (turf_id, session['user_id'])).fetchone()
    if turf:
        conn.execute("DELETE FROM payments WHERE booking_id IN (SELECT id FROM bookings WHERE turf_id=?)", (turf_id,))
        conn.execute("DELETE FROM bookings WHERE turf_id=?", (turf_id,))
        conn.execute("DELETE FROM turfs WHERE id=?", (turf_id,))
        conn.commit()
        flash('Turf and its associated bookings removed.', 'success')
    else:
        flash('Unauthorized or Turf not found.', 'error')
    
    conn.close()
    return redirect(url_for('admin_dashboard'))

@app.route('/manage_bookings')
def manage_bookings():
    if 'user_id' not in session or session['role'] != 'Admin':
        return redirect(url_for('login'))
        
    conn = get_db()
    bookings = conn.execute('''
        SELECT b.*, t.name as turf_name, u.full_name as customer_name, u.phone as customer_phone
        FROM bookings b
        JOIN turfs t ON b.turf_id = t.id
        JOIN users u ON b.customer_id = u.id
        WHERE t.owner_id = ?
        ORDER BY b.id DESC
    ''', (session['user_id'],)).fetchall()
    conn.close()
    
    return render_template('manage_bookings.html', bookings=bookings)

@app.route('/booking_action/<int:booking_id>', methods=['POST'])
def booking_action(booking_id):
    if 'user_id' not in session or session['role'] != 'Admin':
        return redirect(url_for('login'))
        
    action = request.form.get('action')
    
    conn = get_db()
    booking = conn.execute('''
        SELECT b.* FROM bookings b
        JOIN turfs t ON b.turf_id = t.id
        WHERE b.id = ? AND t.owner_id = ?
    ''', (booking_id, session['user_id'])).fetchone()
    
    if booking and booking['status'] == 'Pending':
        if action == 'accept':
            turf = conn.execute("SELECT available_slots FROM turfs WHERE id=?", (booking['turf_id'],)).fetchone()
            if turf and turf['available_slots'] > 0:
                # Check overlapping confirmed bookings
                overlapping = conn.execute('''
                    SELECT COUNT(*) as count FROM bookings 
                    WHERE turf_id=? AND booking_date=? AND status='Confirmed' 
                    AND (start_time < ? AND end_time > ?)
                ''', (booking['turf_id'], booking['booking_date'], booking['end_time'], booking['start_time'])).fetchone()
                
                if overlapping['count'] >= turf['available_slots']:
                    flash('Cannot accept booking. Time slot is fully booked.', 'error')
                else:
                    conn.execute("UPDATE bookings SET status='Confirmed', payment_status='Paid' WHERE id=?", (booking_id,))
                    
                    # Create a payment record to keep the database fully populated
                    transaction_id = f"TXN-{uuid.uuid4().hex[:8].upper()}"
                    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    conn.execute('''
                        INSERT INTO payments (booking_id, customer_id, amount, method, transaction_id, timestamp)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (booking_id, booking['customer_id'], booking['total_price'], 'Manual/Cash', transaction_id, timestamp))
                    
                    conn.commit()
                    flash('Booking confirmed and payment manually reconciled.', 'success')
            else:
                flash('Cannot accept booking. Turf not found or zero slots.', 'error')
        elif action == 'reject':
            conn.execute("UPDATE bookings SET status='Rejected', payment_status='Refunded' WHERE id=?", (booking_id,))
            conn.commit()
            flash('Booking rejected.', 'success')
        
        conn.close()
        return redirect(url_for('admin_dashboard'))
    
    conn.close()
    flash('Cannot act on this booking.', 'error')
    return redirect(url_for('admin_dashboard'))

@app.route('/revenue')
def revenue():
    if 'user_id' not in session or session['role'] != 'Admin':
        return redirect(url_for('login'))
        
    conn = get_db()
    turfs_revenue = conn.execute('''
        SELECT t.name, SUM(b.total_price) as total_earned, COUNT(b.id) as total_bookings
        FROM turfs t
        LEFT JOIN bookings b ON t.id = b.turf_id AND b.status = 'Confirmed' AND b.payment_status = 'Paid'
        WHERE t.owner_id = ?
        GROUP BY t.id
    ''', (session['user_id'],)).fetchall()
    
    overall_revenue = sum([t['total_earned'] or 0 for t in turfs_revenue])
    overall_bookings = sum([t['total_bookings'] or 0 for t in turfs_revenue])
    
    conn.close()
    
    labels = [t['name'] for t in turfs_revenue]
    data = [t['total_earned'] or 0 for t in turfs_revenue]
    
    return render_template('revenue.html', turfs_revenue=turfs_revenue, 
                           overall_revenue=overall_revenue, 
                           overall_bookings=overall_bookings,
                           labels=labels, data=data)

@app.route('/upload_turf_photo/<int:turf_id>', methods=['POST'])
def upload_turf_photo(turf_id):
    if 'user_id' not in session or session['role'] != 'Admin':
        return redirect(url_for('login'))
    
    image = request.files.get('image')
    new_path = save_image(image)
    
    if new_path:
        conn = get_db()
        conn.execute("UPDATE turfs SET image_path=? WHERE id=? AND owner_id=?",
                     (new_path, turf_id, session['user_id']))
        conn.commit()
        conn.close()
        flash('Photo uploaded successfully!', 'success')
    else:
        flash('Invalid file. Please upload a JPG, PNG or WEBP image.', 'error')
    
    return redirect(url_for('admin_dashboard'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)
