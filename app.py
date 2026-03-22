from flask import Flask, render_template, request, redirect, flash, session, url_for
import sqlite3
from datetime import datetime, timedelta
import smtplib
import re
import hashlib
import os

app = Flask(__name__)
app.secret_key = "supersecretkey"   # use fixed key for session

# ---------- DATABASE ----------
def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        email TEXT UNIQUE
    )
    ''')

    c.execute('''
    CREATE TABLE IF NOT EXISTS items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        name TEXT,
        category TEXT,
        expiry_date TEXT,
        reminder_days INTEGER,
        notified INTEGER DEFAULT 0
    )
    ''')

    conn.commit()
    conn.close()

init_db()

def get_db():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# ---------- EMAIL ----------
def send_email(to_email, item_name):
    try:
        sender = "your mail"
        password = "your app password"  

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender, password)

        message = f"Subject: Expiry Alert\n\nYour item '{item_name}' is expiring soon!"

        server.sendmail(sender, to_email, message)
        server.quit()

        print("EMAIL SENT SUCCESSFULLY")

    except Exception as e:
        print("EMAIL ERROR:", e)

# ---------- AUTH ----------
@app.route('/auth')
def auth():
    return render_template('login.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/register_submit', methods=['POST'])
def register_submit():
    username = request.form['username'].strip()
    password = request.form['password'].strip()
    email = request.form['email'].strip()

    if not username or not password or not email:
        flash("All fields required ❌")
        return redirect(url_for('register'))

    if len(password) < 6:
        flash("Password must be at least 6 characters ❌")
        return redirect(url_for('register'))

    conn = get_db()
    c = conn.cursor()

    c.execute("SELECT * FROM users WHERE username=? OR email=?", (username, email))
    if c.fetchone():
        flash("User already exists ❌")
        return redirect(url_for('register'))

    c.execute("INSERT INTO users VALUES (NULL,?,?,?)",
              (username, hash_password(password), email))

    conn.commit()
    conn.close()

    flash("Registered Successfully 🎉")
    return redirect(url_for('auth'))

@app.route('/login_submit', methods=['POST'])
def login_submit():
    username = request.form['username'].strip()
    password = request.form['password'].strip()

    conn = get_db()
    c = conn.cursor()

    c.execute("SELECT * FROM users WHERE username=? AND password=?",
              (username, hash_password(password)))
    user = c.fetchone()
    conn.close()

    if user:
        session['user'] = user['username']
        session['user_id'] = user['id']
        session['email'] = user['email']
        return redirect(url_for('index'))
    else:
        flash("Invalid login ❌")
        return redirect(url_for('auth'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth'))

# ---------- DASHBOARD ----------
@app.route('/')
def index():
    if 'user' not in session:
        return redirect(url_for('auth'))

    conn = get_db()
    c = conn.cursor()

    c.execute("SELECT * FROM items WHERE user_id=?", (session['user_id'],))
    data = c.fetchall()

    today = datetime.today().date()

    stats = {"total": 0, "expired": 0, "expiring": 0}

    for item in data:
        expiry = datetime.strptime(item['expiry_date'], '%Y-%m-%d').date()
        days_left = (expiry - today).days

        stats["total"] += 1
        if expiry < today:
            stats["expired"] += 1
        elif days_left <= 3:
            stats["expiring"] += 1

    conn.close()

    return render_template('index.html',
                           username=session['user'],
                           stats=stats)

# ---------- ADD ITEM ----------
@app.route('/submit', methods=['POST'])
def submit():
    name = request.form['name']
    category = request.form['category']
    expiry = request.form['expiry_date']
    reminder = int(request.form.get('reminder_days', 0))

    conn = get_db()
    c = conn.cursor()

    c.execute("INSERT INTO items VALUES (NULL,?,?,?,?,?,0)",
              (session['user_id'], name, category, expiry, reminder))

    conn.commit()
    conn.close()

    flash("Item added ✅")
    return redirect(url_for('index'))

# ---------- ITEMS ----------
@app.route('/items')
def items():
    if 'user' not in session:
        return redirect(url_for('auth'))

    conn = get_db()
    c = conn.cursor()

    c.execute("SELECT * FROM items WHERE user_id=?", (session['user_id'],))
    data = c.fetchall()

    today = datetime.today().date()
    items_list = []

    for item in data:
        expiry = datetime.strptime(item['expiry_date'], '%Y-%m-%d').date()
        days_left = (expiry - today).days

        if expiry < today:
            status = "Expired"
            badge = "danger"
        elif days_left <= 3:
            status = "Expiring Soon"
            badge = "warning"
        elif days_left <= 7:
            status = "Due Soon"
            badge = "info"
        else:
            status = "Safe"
            badge = "success"

        # EMAIL LOGIC 🔥 (CORRECT)
        reminder_date = expiry - timedelta(days=item['reminder_days'])
        if datetime.today().date() >= reminder_date and item['notified'] == 0:
            send_email(session['email'], item['name'])
            c.execute("UPDATE items SET notified=1 WHERE id=?", (item['id'],))
            conn.commit()

        items_list.append({
            "id": item['id'],
            "name": item['name'],
            "category": item['category'],
            "expiry_date": item['expiry_date'],
            "days_left": days_left,
            "status": status,
            "badge": badge
        })

    conn.close()

    return render_template('items.html', items=items_list)

# ---------- DELETE ----------
@app.route('/delete/<int:item_id>')
def delete(item_id):
    conn = get_db()
    c = conn.cursor()

    c.execute("DELETE FROM items WHERE id=?", (item_id,))
    conn.commit()
    conn.close()

    flash("Item deleted 🗑️")
    return redirect(url_for('items'))

# ---------- CALENDAR ----------
@app.route('/calendar')
def calendar():
    conn = get_db()
    c = conn.cursor()

    c.execute("SELECT * FROM items WHERE user_id=?", (session['user_id'],))
    data = c.fetchall()

    today = datetime.today().date()
    events = []

    for item in data:
        expiry = datetime.strptime(item['expiry_date'], '%Y-%m-%d').date()
        days_left = (expiry - today).days

        if expiry < today:
            color = "#ef4444"
        elif days_left <= 3:
            color = "#f59e0b"
        elif days_left <= 7:
            color = "#3b82f6"
        else:
            color = "#10b981"

        events.append({
            "title": item['name'],
            "start": item['expiry_date'],
            "color": color,
            "extendedProps": {
                "category": item['category']
            }
        })

    conn.close()

    return render_template('calendar.html', events=events)

# ---------- RUN ----------
if __name__ == '__main__':
    app.run(debug=True)
