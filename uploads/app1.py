from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
import os

app = Flask(__name__)

app.secret_key = 'xyzsdfg'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'user-system'
app.config['UPLOAD_FOLDER'] = 'static/uploads'

mysql = MySQL(app)

@app.route('/')
def home():
    return redirect(url_for('register'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    message = ''
    if request.method == 'POST' and 'phone_no' in request.form and 'otp' in request.form:
        phone = request.form['phone_no']
        otp = request.form['otp']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM user WHERE phone = %s AND pan_no = %s', (phone, otp,))


        user = cursor.fetchone()

        if user:
            session['loggedin'] = True
            session['userid'] = user['userid']  # Use userid for session
            session['full_name'] = user['full_name']
            session['phone'] = user['phone']
            return redirect(url_for('user_home'))  # Corrected redirection to user_home
        else:
            message = 'Please enter correct phone number / PAN number!'
    return render_template('index1.html', message=message)



@app.route('/register', methods=['GET', 'POST'])
def register():
    message = ''
    if request.method == 'POST' and all(field in request.form for field in
                                        ['account_no', 'ifsc_code', 'full_name', 'pan_no', 'phone']) and 'biometric' in request.files:

        account_no = request.form['account_no']
        ifsc_code = request.form['ifsc_code']
        full_name = request.form['full_name']
        pan_no = request.form['pan_no']
        phone = request.form['phone']
        biometric = request.files['biometric']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM user WHERE phone = %s', (phone,))
        account = cursor.fetchone()
        if account:
            message = 'Account already exists!'
        elif not re.match(r'^\d{10}$', phone):
            message = 'Invalid phone number!'
        elif not account_no or not ifsc_code or not full_name or not pan_no or not phone:
            message = 'Please fill out the form!'
        else:
            biometric_path = os.path.join(app.config['UPLOAD_FOLDER'], biometric.filename)
            biometric.save(biometric_path)
            cursor.execute(
                'INSERT INTO user (account_no, ifsc_code, full_name, pan_no,  phone,biometric_path) VALUES (%s, %s, %s, %s,  %s, %s)',
                (account_no, ifsc_code, full_name, pan_no, phone,biometric_path))
            mysql.connection.commit()
            session['loggedin'] = True
            session['userid'] = cursor.lastrowid
            session['full_name'] = full_name
            session['phone'] = phone
            return redirect(url_for('login'))  # Redirect to home page after registration
    elif request.method == 'POST':
        message = 'Please fill out the form!'
    return render_template('index.html', message=message)

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('userid', None)
    session.pop('phone', None)
    return redirect(url_for('login'))

@app.route('/home')
def user_home():
    if 'loggedin' in session:
        return render_template('index2.html', name=session['full_name'])
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(debug=True)
