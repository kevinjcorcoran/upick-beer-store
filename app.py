from flask import Flask, render_template
from flask_mysqldb import MySQL
import os

basePath = os.path.abspath(os.path.dirname(__file__))
template_dir = os.path.join(basePath, 'templates')
ddl_file = os.path.join(basePath, 'static/create_beer_db.sql')

# need to specify the template directory if it is not in the base directory
app = Flask(__name__, template_folder=template_dir)
app.config.from_object('config')  # load config information
mysql = MySQL(app)


@app.route('/')
@app.route('/index.html') 
def root():
    cursor = mysql.connection.cursor()
    # Create all the tables if they don't already exist
    with open(ddl_file, encoding='utf-8') as ddl_statements:
        cursor.execute(ddl_statements.read())
    
    cursor.execute('''SELECT * FROM Brewery''')
    brewery_data = cursor.fetchall()

    return render_template('index.html', page_title='UPick Beer Store', brewery_data=brewery_data)


@app.route('/beers.html')
def beers():
    cursor = mysql.connection.cursor()

    cursor.execute('''
        SELECT Beer.*, Brewery.brewery_name
        FROM Beer, Brewery
        WHERE Beer.brewery_id = Brewery.id
    ''')
    beer_data = cursor.fetchall()

    return render_template('beers.html', page_title='UPick Beer Store: Beers', beer_data=beer_data)


@app.route('/breweries.html')
def breweries():
    cursor = mysql.connection.cursor()

    cursor.execute('''SELECT * FROM Brewery''')
    brewery_data = cursor.fetchall()

    return render_template('breweries.html', page_title='UPick Beer Store: Breweries', brewery_data=brewery_data)


@app.route('/styles.html')
def styles():
    cursor = mysql.connection.cursor()

    cursor.execute('''SELECT * FROM Style''')
    style_data = cursor.fetchall()

    return render_template('styles.html', page_title='UPick Beer Store: Styles', style_data=style_data)


@app.route('/account.html')
def account():
    return render_template('account.html', page_title='UPick Beer Store: Account')


@app.route('/cart.html')
def cart():
    return render_template('cart.html', page_title='UPick Beer Store: Cart')


if __name__ == '__main__':
    app.run(debug=True)
