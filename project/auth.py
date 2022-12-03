from flask import (Blueprint, flash, redirect, render_template, request,
                   session, url_for)
from werkzeug.security import check_password_hash, generate_password_hash

from .utilities import execute_query

auth = Blueprint('auth', __name__)


@auth.route('/login')
def login():
    '''Display the login page.'''
    return render_template('login.html', page_title='Login')


@auth.route('/login', methods=['POST'])
def login_post():
    '''Send a login request to the DB and logs the user into the current session.'''

    email = request.form.get('email')
    password = request.form.get('password')

    user = execute_query(
        f"SELECT * "
        f"FROM Customer "
        f"WHERE email = '{email}'", True
    )
    if not user or not check_password_hash(user['password'], password):
        flash('Incorrect email or password.')
        return redirect(url_for('auth.login'))

    session['loggedin'] = True
    session['email'] = user['email']
    session['name'] = user['first_name']

    return redirect(url_for('main.account'))


@auth.route('/signup')
def signup():
    '''Show sign up page. Sends styles for list of favorite style to choose from.'''
    styles = execute_query(
        'SELECT style_name '
        'FROM Style'
    )

    return render_template('signup.html', page_title='Signup', styles=styles)


@auth.route('/signup', methods=['GET', 'POST'])
def signup_post():
    '''Process the signup form. Checks if the email is already used and hashes their password.'''
    email = request.form.get('email')
    password = request.form.get('password')
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    street = request.form.get('street')
    city = request.form.get('city')
    state = request.form.get('state')
    zip_code = request.form.get('zip')
    favorite_style = request.form.get('favorite_style')

    user = execute_query(
        f"SELECT * "
        f"FROM Customer "
        f"WHERE email = '{email}'", True
    )

    if user:
        flash('Email address already exists')
        return redirect(url_for('auth.signup'))

    hashed_password = generate_password_hash(password, method='sha256')
    execute_query(
        f'INSERT INTO Customer VALUES( '
        f'"{email}", "{hashed_password}", '
        f'"{first_name}", "{last_name}", '
        f'"{street}", "{city}", "{state}", {zip_code}, '
        f'"{favorite_style}")'
    )

    return redirect(url_for('auth.login'))


@auth.route('/logout', methods=['GET', 'POST'])
def logout():
    '''Log out the current user.'''
    session.pop('loggedin', None)
    session.pop('email')
    session.pop('name')

    return render_template('confirmation.html', message='Logout successful!')