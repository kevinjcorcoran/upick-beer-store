import json
import os
import sys
import uuid
from datetime import datetime

from flask import (Blueprint, flash, redirect, render_template, request, session,
                   url_for)

from .utilities import execute_query

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
    '''
    Create and populate the tables if they don't exist.
    Query all breweries to show on home page.
    '''
    with open(ddl_file, encoding='utf-8') as ddl_statements:
        execute_query(ddl_statements.read())
    with open(brewery_file, encoding='utf-8') as breweries:
        execute_query(breweries.read())
    with open(style_file, encoding='utf-8') as styles:
        execute_query(styles.read())
    with open(beer_file, encoding='utf-8') as beers:
        execute_query(beers.read())

    popular_beers = execute_query(
        f"SELECT Beer.beer_name as Beer, count(*) as Likes "
        f"FROM likes, Beer "
        f"WHERE likes.beer_upc = Beer.upc "
        f"GROUP BY Beer.beer_name "
        f"ORDER BY Likes DESC"
    )

    if session.get('loggedin'):
        favorite_style = execute_query(
            f"SELECT favorite_style "
            f"FROM Customer "
            f"WHERE Customer.email = '{session.get('email')}'", True
        )
        suggestions = execute_query(
            f"SELECT * "
            f"FROM Beer "
            f"WHERE Beer.style = '{favorite_style['favorite_style']}'"
        )
    else:
        suggestions = None

    return render_template('index.html', page_title='Home', popular_beers=popular_beers, suggestions=suggestions)


@main.route('/beers.html')
def beers():
    '''Query all beers from the DB and display them on the page.'''
    beer_data = execute_query(
        'SELECT Beer.*, Brewery.brewery_name '
        'FROM Beer, Brewery '
        'WHERE Beer.brewery_id = Brewery.id'
    )

    return render_template('beers.html', page_title='Beers', beer_data=beer_data)


@main.route('/breweries.html')
def breweries():
    '''Query all breweries from the DB and display them on the page.'''
    brewery_data = execute_query(
        'SELECT * '
        'FROM Brewery'
    )

    return render_template('breweries.html', page_title='Breweries', brewery_data=brewery_data)


@main.route('/styles.html')
def styles():
    '''Query all styles and display them on the page.'''
    style_data = execute_query('SELECT * FROM Style')

    return render_template('styles.html', page_title='Styles', style_data=style_data)


@main.route('/account.html')
def account():
    '''If a user is logged in, query their data to display on the screen. 
    Otherwise redirect to login.'''
    if session.get('loggedin'):
        customer_name = session.get('name')
        customer_email = session.get('email')
        user = execute_query(
            f"SELECT * "
            f"FROM Customer "
            f"WHERE email ='{customer_email}'", True
        )
        liked_beers = execute_query(
            f"SELECT Beer.beer_name "
            f"FROM Beer, likes "
            f"WHERE Beer.upc = likes.beer_upc "
            f"AND likes.customer_email = '{customer_email}'"
        )
        order_history = execute_query(
            f"SELECT * "
            f"FROM Purchase "
            f"WHERE customer_email = '{customer_email}' "
            f"AND closed = 1 "
            f"ORDER BY last_edit DESC"
        )
        return render_template(
            'account.html', page_title='Account',
            name=customer_name, user=user, liked_beers=liked_beers,
            order_history=order_history
        )

    return redirect(url_for('auth.login'))


@main.route('/like', methods=['GET','POST'])
def like():
    '''Process a like request if a user is logged in. 
    Otherwise redirect to login.'''
    liked_beer = request.form.get('beer_upc')
    if session.get('loggedin'):
        execute_query(
            f"INSERT IGNORE INTO likes VALUES("
            f"'{session.get('email')}', '{liked_beer}')"
        )
        return redirect(url_for('main.account'))

    return redirect(url_for('auth.login'))


@main.route('/add_to_cart', methods=['GET', 'POST'])
def add_to_cart():
    '''Process an add to cart request if the user is logged in. 
    Otherwise redirect to login.'''
    item = request.form.get('beer_upc')
    price = execute_query(
        f"SELECT price "
        f"FROM Beer "
        f"WHERE upc = {item}", True
    )['price']

    if session.get('loggedin'):
        customer_email = session.get('email')
        cart_id = execute_query(
            f"SELECT id "
            f"FROM Purchase "
            f"WHERE closed = 0 "
            f"AND customer_email = '{customer_email}'", True
        )
        if not cart_id:
            # Crete a new cart if the user doesn't have one open
            cart_id = uuid.uuid1()
            execute_query(
                f"INSERT INTO Purchase VALUES("
                f"'{cart_id}', '{customer_email}', 0, "
                f"'{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}', 0)"
            )
        else:
            cart_id = cart_id['id']

        curr_quantity = execute_query(
            f"SELECT quantity "
            f"FROM Purchase_Item "
            f"WHERE purchase_id = '{cart_id}' "
            f"AND beer_upc = {item}"
        )
        if not curr_quantity:
            execute_query(
                f"INSERT INTO Purchase_Item VALUES("
                f"'{cart_id}', {item}, 1)"
            )
        else:
            execute_query(
                f"UPDATE Purchase_Item "
                f"SET quantity = quantity + 1 "
                f"WHERE purchase_id = '{cart_id}' "
                f"AND beer_upc = {item}"
            )

        execute_query(
            f"UPDATE Purchase "
            f"SET total = total + {price} "
            f"WHERE Purchase.id = '{cart_id}'"
        )

        return redirect(url_for('main.cart'))

    return redirect(url_for('auth.login'))


@main.route('/cart.html')
def cart():
    '''Query the user's cart and items if they are logged in. 
    Otherwise redirect to login.'''
    if session.get('loggedin'):
        customer_email = session.get('email')
        cart = execute_query(
            f"SELECT * "
            f"FROM Purchase "
            f"WHERE closed = 0 "
            f"AND customer_email = '{customer_email}'", True
        )
        if not cart:
            # Crete a new cart if the user doesn't have one open
            cart_id = uuid.uuid1()
            execute_query(
                f"INSERT INTO Purchase VALUES("
                f"'{cart_id}', '{customer_email}', 0, "
                f"'{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}', 0)"
            )
            cart = execute_query(
                f"SELECT * "
                f"FROM Purchase "
                f"WHERE closed = 0 "
                f"AND customer_email = '{customer_email}'", True
            )

        cart_id = cart['id']
        total = cart['total']
        cart_items = execute_query(
            f"SELECT B.beer_name AS 'name', "
                f"P.quantity AS 'quantity', "
                f"B.price * P.quantity AS 'item_total', "
                f"P.purchase_id AS 'purchase_id', "
                f"B.upc AS 'upc' ,"
                f"B.price AS 'beer_price' "
            f"FROM Beer B, Purchase_Item P "
            f"WHERE P.purchase_id = '{cart_id}' "
            f"AND B.upc = P.beer_upc"
        )

        size = 0
        for item in cart_items:
            size += item['quantity']

        return render_template(
            'cart.html', page_title='Cart', cart_items=cart_items,
            total=total, size=size
        )

    return redirect(url_for('auth.login'))


@main.route('/checkout', methods=['GET', 'POST'])
def checkout():
    '''Query the user's cart and items, remove them from the stock, and close the purchase'''
    customer_email = session.get('email')
    cart = execute_query(
        f"SELECT * "
        f"FROM Purchase "
        f"WHERE closed = 0 "
        f"AND customer_email = '{customer_email}'", True
    )

    cart_id = cart['id']
    cart_items = execute_query(
        f"SELECT B.beer_name AS 'name', "
            f"P.quantity AS 'quantity', "
            f"B.price * P.quantity AS 'item_total', "
            f"P.purchase_id AS 'purchase_id', "
            f"B.upc AS 'upc' "
        f"FROM Beer B, Purchase_Item P "
        f"WHERE P.purchase_id = '{cart_id}' "
        f"AND B.upc = P.beer_upc"
    )

    for item in cart_items:
        try:
            execute_query(
                f"UPDATE Beer "
                f"SET stock = stock - {item.get('quantity')} "
                f"WHERE upc = {int(item.get('upc'))}"
            )
        except:
            stock = execute_query(
                f"SELECT stock "
                f"FROM Beer "
                f"WHERE upc = {item.get('upc')}", True
            )['stock']
            flash(f"Too many {item.get('name')} in cart. Only {stock} in stock.")

            return redirect(url_for('main.cart'))

    # Set the Purchase as closed
    execute_query(
        f"UPDATE Purchase "
        f"SET closed = 1 "
        f"WHERE id = '{cart_id}'"
    )

    return render_template(
        'confirmation.html', message='Thanks for your order!',
         sub_message=f'Order Number: {cart_id}'
    )


@main.route('/inc_quantity', methods=['GET', 'POST'])
def inc_quantity():
    '''Increase the quantity of an item in the cart.'''
    beer_upc = request.form.get('beer_upc')
    purchase_id = request.form.get('purchase_id')
    beer_price = request.form.get('beer_price')
    execute_query(
        f"UPDATE Purchase_Item "
        f"SET quantity = quantity + 1 "
        f"WHERE purchase_id = '{purchase_id}' "
        f"AND beer_upc = {beer_upc}"
    )
    execute_query(
        f"UPDATE Purchase "
        f"SET total = total + {beer_price} "
        f"WHERE id = '{purchase_id}'"
    )

    return redirect(url_for('main.cart'))


@main.route('/dec_quantity', methods=['GET', 'POST'])
def dec_quantity():
    '''Increase the quantity of an item in the cart.'''
    beer_upc = request.form.get('beer_upc')
    purchase_id = request.form.get('purchase_id')
    beer_price = request.form.get('beer_price')
    quantity = request.form.get('quantity')

    if int(quantity) > 1:
        try:
            execute_query(
                f"UPDATE Purchase_Item "
                f"SET quantity = quantity - 1 "
                f"WHERE purchase_id = '{purchase_id}' "
                f"AND beer_upc = {beer_upc}"
            )

            execute_query(
                f"UPDATE Purchase "
                f"SET total = total - {beer_price} "
                f"WHERE id = '{purchase_id}'"
            )
        except:
            return redirect(url_for('main.cart'))
    else:
        execute_query(
            f"DELETE FROM Purchase_Item "
            f"WHERE purchase_id = '{purchase_id}' "
            f"AND beer_upc = {beer_upc}"
        )

    return redirect(url_for('main.cart'))