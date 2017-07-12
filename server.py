from flask import Flask, request, redirect, render_template, session, flash
from mysqlconnection import MySQLConnector
import re
import md5
import os, binascii

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

app = Flask(__name__)
app.secret_key = 'secret'
mysql = MySQLConnector(app, 'loginregistrationdb')

@app.route('/')
def index():
    if 'user_id' not in session:
        session['user_id'] = ''
    if 'first_name' not in session:
        session['first_name'] = ''
    if 'last_name' not in session:
        session['last_name'] = ''
    if 'email' not in session:
        session['email'] = ''
    return render_template('index.html')

@app.route('/register', methods=['POST'])
def register():
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    email = request.form['email']
    pw = request.form['pw']
    pw_confirm = request.form['pw_confirm']

    # FORM VALIDATION
    session['first_name'] = first_name
    session['last_name'] = last_name
    session['email'] = email

    if len(first_name) < 2 or len(last_name) < 2 or not first_name.isalpha() or not last_name.isalpha():
        flash('First and last names must be at least 2 characters and only contain letters!')
        return redirect('/')

    if len(email) < 1:
        flash('Email cannot be blank!')
        return redirect('/')
    elif not EMAIL_REGEX.match(email):
        flash('Invalid email address!')
        return redirect('/')

    if len(pw) < 8:
        flash('Password must be at least 8 characters')
        return redirect('/')

    if pw != pw_confirm:
        flash('Passwords don\'t match!')
        return redirect('/')

    session['first_name'] = ''
    session['last_name'] = ''
    session['email'] = ''

    # ADD TO DATABASE
    salt = binascii.b2a_hex(os.urandom(15))
    hashed_pw = md5.new(pw + salt).hexdigest()

    query_data = {
        'first_name': first_name,
        'last_name': last_name,
        'email': email,
        'password': hashed_pw,
        'salt': salt
    }
    insert_query = "INSERT INTO users (first_name, last_name, email, password, salt, created_at, updated_at) VALUES (:first_name, :last_name, :email, :password, :salt, NOW(), NOW())"
    user = mysql.query_db(insert_query, query_data)

    session['user_id'] = str(user)
    flash('Registration successful!')
    return redirect('/home/' + session['user_id'])

@app.route('/login', methods=['POST'])
def login():
    return redirect('/home')

@app.route('/home/<user_id>')
def homepage(user_id):
    data = {'id': int(user_id)}
    query = "SELECT * FROM users WHERE id = :id"
    user = mysql.query_db(query, data)
    return render_template('home.html', first_name=user[0]['first_name'])

app.run(debug=True)