# RAKTADATA - BLOOD DONATION SYSTEM
from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import re
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'
DB_NAME = 'blood.db'

# Initialize database
def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS donors (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                phone TEXT NOT NULL,
                blood_group TEXT NOT NULL,
                last_donation DATE
             )''')
    conn.commit()
    conn.close()

# Validate phone number format (Bangladeshi)
def validate_phone(phone):
    return re.match(r'^01[3-9]\d{8}$', phone)

# Homepage - Dashboard
@app.route('/')
def dashboard():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # Get blood inventory
    c.execute("SELECT blood_group, COUNT(*) FROM donors GROUP BY blood_group")
    inventory = c.fetchall()
    
    # Get recent donors
    c.execute("""
        SELECT name, blood_group, last_donation 
        FROM donors 
        ORDER BY last_donation DESC 
        LIMIT 5
    """)
    recent_donors = c.fetchall()
    
    conn.close()
    return render_template('dashboard.html', 
                           inventory=inventory,
                           recent_donors=recent_donors)

# Donor Registration
@app.route('/register', methods=['GET', 'POST'])
def register_donor():
    if request.method == 'POST':
        name = request.form['name']
        phone = request.form['phone']
        blood_group = request.form['blood_group']
        last_donation = request.form['last_donation']
        
        # Input validation
        if not validate_phone(phone):
            flash('অবৈধ মোবাইল নম্বর! সঠিক ফরম্যাট: 01XXXXXXXXX', 'danger')
            return redirect(url_for('register_donor'))
        
        try:
            datetime.strptime(last_donation, '%Y-%m-%d')
        except ValueError:
            flash('অবৈধ তারিখ ফরম্যাট! YYYY-MM-DD ব্যবহার করুন', 'danger')
            return redirect(url_for('register_donor'))
        
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute('''INSERT INTO donors (name, phone, blood_group, last_donation)
                     VALUES (?, ?, ?, ?)''', 
                 (name, phone, blood_group, last_donation))
        conn.commit()
        conn.close()
        
        flash('নিবন্ধন সফলভাবে সম্পন্ন হয়েছে!', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('register.html')

# Blood Inventory
@app.route('/inventory')
def blood_inventory():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM donors ORDER BY last_donation DESC")
    donors = c.fetchall()
    conn.close()
    return render_template('inventory.html', donors=donors)

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=8080)