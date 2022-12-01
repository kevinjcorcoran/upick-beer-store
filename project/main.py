from flask import Blueprint, redirect, render_template, session, url_for
from . import mysql, execute_query
import os

# Primary Directories
basePath = os.path.abspath(os.path.dirname(__file__))
template_dir = os.path.join(basePath, 'templates')

# SQL Statements
ddl_file = os.path.join(basePath, 'static/create_beer_db.sql')
brewery_file = os.path.join(basePath, 'static/insert_breweries.sql')
style_file = os.path.join(basePath, 'static/insert_styles.sql')
beer_file = os.path.join(basePath, 'static/insert_beers.sql')

# Setting up Flask and MySQL
main = Blueprint('main', __name__)


@main.route('/')
@main.route('/index.html', methods=['GET', 'POST']) 
def index():
    # Create and populate all the tables if they don't already exist
    with open(ddl_file, encoding='utf-8') as ddl_statements:
        execute_query(ddl_statements.read())
    with open(brewery_file, encoding='utf-8') as breweries:
        execute_query(breweries.read())
    with open(style_file, encoding='utf-8') as styles:
        execute_query(styles.read())
    with open(beer_file, encoding='utf-8') as beers:
        execute_query(beers.read())
    
    brewery_data = execute_query('SELECT * FROM Brewery')

    return render_template('index.html', page_title='Home', brewery_data=brewery_data)


@main.route('/beers.html')
def beers():
    beer_data = execute_query('''
        SELECT Beer.*, Brewery.brewery_name
        FROM Beer, Brewery
        WHERE Beer.brewery_id = Brewery.id
    ''')

    return render_template('beers.html', page_title='Beers', beer_data=beer_data)


@main.route('/breweries.html')
def breweries():
    brewery_data = execute_query('SELECT * FROM Brewery')

    return render_template('breweries.html', page_title='Breweries', brewery_data=brewery_data)


@main.route('/styles.html')
def styles():
    style_data = execute_query('SELECT * FROM Style')

    return render_template('styles.html', page_title='Styles', style_data=style_data)


@main.route('/account.html')
def account():
    if 'loggedin' in session:
        user = execute_query(f"SELECT * FROM Customer WHERE email ='{session['id']}'", True)
        return render_template('account.html', page_title='Account', name=session['username'], user=user)
    return redirect(url_for('auth.login'))

@main.route('/cart.html')
def cart():
    return render_template('cart.html', page_title='Cart')
