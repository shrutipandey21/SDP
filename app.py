from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
import os
import hashlib

app = Flask(__name__)

app.secret_key = 'xyzsdfg'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'user-system'
app.config['UPLOAD_FOLDER'] = 'static/uploads'

mysql = MySQL(app)


def hash_file(file_path):
    """Generate SHA-256 hash of the file content."""
    hasher = hashlib.sha256()
    with open(file_path, 'rb') as f:
        buf = f.read()
        hasher.update(buf)
    return hasher.hexdigest()


def compare_images(image_path1, image_path2):
    """Compare the hash of two images."""
    return hash_file(image_path1) == hash_file(image_path2)


@app.route('/')
def home():
    return redirect(url_for('register'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    message = ''
    if request.method == 'POST' and 'phone_no' in request.form and 'otp' in request.form and 'biometric' in request.files:
        phone = request.form['phone_no']
        otp = request.form['otp']
        biometric = request.files['biometric']

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM user WHERE phone = %s AND pan_no = %s', (phone, otp,))
        user = cursor.fetchone()

        if user:
            biometric_path = os.path.join(app.config['UPLOAD_FOLDER'], 'login_' + biometric.filename)
            biometric.save(biometric_path)

            if compare_images(user['biometric_path'], biometric_path):
                session['loggedin'] = True
                session['userid'] = user['userid']
                session['full_name'] = user['full_name']
                session['phone'] = user['phone']
                return redirect(url_for('user_home'))
            else:
                message = 'Biometric verification failed!'
        else:
            message = 'Please enter correct phone number / PAN number!'
    return render_template('index1.html', message=message)


@app.route('/register', methods=['GET', 'POST'])
def register():
    message = ''
    if request.method == 'POST' and all(field in request.form for field in
                                        ['account_no', 'ifsc_code', 'full_name', 'pan_no',
                                         'phone']) and 'biometric' in request.files:
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
                'INSERT INTO user (account_no, ifsc_code, full_name, pan_no, phone, biometric_path) VALUES (%s, %s, %s, %s, %s, %s)',
                (account_no, ifsc_code, full_name, pan_no, phone, biometric_path))
            mysql.connection.commit()
            session['loggedin'] = True
            session['userid'] = cursor.lastrowid
            session['full_name'] = full_name
            session['phone'] = phone
            return redirect(url_for('login'))
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


@app.route('/make_transaction')
def make_transaction():
    if 'loggedin' in session:
        return render_template('make_transaction.html')
    return redirect(url_for('login'))


@app.route('/pay', methods=['GET', 'POST'])
def pay():
    if 'loggedin' in session:
        if request.method == 'POST' and 'receiver_id' in request.form and 'amount' in request.form and 'otp' in request.form and 'biometric' in request.files:
            otp = request.form['otp']
            biometric = request.files['biometric']

            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM user WHERE userid = %s', (session['userid'],))
            user = cursor.fetchone()

            if user:
                biometric_path = os.path.join(app.config['UPLOAD_FOLDER'], 'pay_' + biometric.filename)
                biometric.save(biometric_path)

                if compare_images(user['biometric_path'], biometric_path) and otp == user['pan_no']:
                    return redirect("https://www.onlinesbi.sbi/")
                else:
                    return "Biometric or OTP verification failed!"
            else:
                return "User not found!"
        return render_template('pay.html')
    return redirect(url_for('login'))


@app.route('/profile_details')
def profile_details():
    if 'loggedin' in session:
        return render_template('profile_details.html')
    return redirect(url_for('login'))


@app.route('/transaction_history')
def transaction_history():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM transactions WHERE userid = %s', [session['userid']])
        transactions = cursor.fetchall()
        return render_template('transaction_history.html', transactions=transactions)
    return redirect(url_for('login'))

@app.route('/feedback')
def feedback():
    if 'loggedin' in session:
        return redirect(url_for('helpline'))
    return redirect(url_for('login'))

@app.route('/helpline')
def helpline():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM transactions WHERE userid = %s', [session['userid']])
        transactions = cursor.fetchall()
        return render_template('helpline.html', transactions=transactions)
    return redirect(url_for('login'))

@app.route('/back')
def back():
    if 'loggedin' in session:
        return redirect(url_for('make_transaction'))
    return redirect(url_for('login'))




if __name__ == "__main__":
    app.run(debug=True)
