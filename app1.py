# app.py
from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Database connection function
def db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="your_mysql_user",
        password="your_mysql_password",
        database="travel_agency"
    )

# Home Route
@app.route('/')
def home():
    conn = db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Destinations")
    destinations = cursor.fetchall()
    conn.close()
    return render_template('index.html', destinations=destinations)

# Registration Route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])
        
        conn = db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Users (name, email, password) VALUES (%s, %s, %s)", 
                       (name, email, password))
        conn.commit()
        conn.close()
        return redirect(url_for('login'))
    
    return render_template('register.html')

# Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        conn = db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Users WHERE email=%s", (email,))
        user = cursor.fetchone()
        conn.close()
        
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['user_id']
            session['name'] = user['name']
            return redirect(url_for('home'))
    
    return render_template('login.html')

# Booking Route
@app.route('/book/<int:dest_id>', methods=['POST'])
def book(dest_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Bookings (user_id, dest_id, booking_date) VALUES (%s, %s, NOW())",
                   (session['user_id'], dest_id))
    conn.commit()
    conn.close()
    return redirect(url_for('home'))

# Logout Route
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
