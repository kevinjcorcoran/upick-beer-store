import sys
from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from . import mysql, execute_query
from werkzeug.security import generate_password_hash, check_password_hash


auth = Blueprint('auth', __name__)


@auth.route('/login')
def login():
    return render_template('login.html', page_title='Login')


@auth.route('/login', methods=['POST'])
def login_post():
    email = request.form.get('email')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False


    user = execute_query(f'SELECT * FROM Customer WHERE email = "{email}"', True)

    if not user or not check_password_hash(user['password'], password):
        flash('Incorrect email or password.')
        return redirect(url_for('auth.login'))

    session['loggedin'] = True
    session['id'] = user['email']
    session['username'] = user['first_name']

    return redirect(url_for('main.account'))


@auth.route('/signup')
def signup():
    styles = execute_query('SELECT style_name FROM Style')

    return render_template('signup.html', page_title='Signup', styles=styles)


@auth.route('/signup', methods=['GET', 'POST'])
def signup_post():
    cursor = mysql.connection.cursor()

    email = request.form.get('email')
    password = request.form.get('password')
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    street = request.form.get('street')
    city = request.form.get('city')
    state = request.form.get('state')
    zip_code = request.form.get('zip')
    favorite_style = request.form.get('favorite_style')

    user = execute_query(f'SELECT * FROM Customer WHERE email = "{email}"', True)

    if user:
        flash('Email address already exists')
        return redirect(url_for('auth.signup'))

    hashed_password = generate_password_hash(password, method='sha256')
    insert = f'INSERT INTO Customer VALUES("{email}", "{hashed_password}", "{first_name}", "{last_name}", "{street}", "{city}", "{state}", {zip_code}, "{favorite_style}")'
    execute_query(insert)

    return redirect(url_for('auth.login'))

@auth.route('/logout')
def logout():
    return 'Logout'