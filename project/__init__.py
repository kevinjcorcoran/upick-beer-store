from flask import Flask
from flask_mysqldb import MySQL
import os

# Primary Directories
basePath = os.path.abspath(os.path.dirname(__file__))
template_dir = os.path.join(basePath, 'templates')

mysql = MySQL()

def create_app():
    app = Flask(__name__, template_folder=template_dir)

    # PythonAnywhere Settings
    #app.config['MYSQL_USER'] = 'kevinjcorcoran'
    #app.config['MYSQL_PASSWORD'] = 'upick-beer-store'
    #app.config['MYSQL_HOST'] = 'kevinjcorcoran.mysql.pythonanywhere-services.com'
    #app.config['MYSQL_DB'] = 'kevinjcorcoran$beer_db'

    # Local Settings
    app.config['MYSQL_USER'] = 'root'
    app.config['MYSQL_PASSWORD'] = ''
    app.config['MYSQL_HOST'] = 'localhost'
    app.config['MYSQL_DB'] = 'beer_db'

    app.config['SECRET_KEY'] = 'upick'
    app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

    mysql.init_app(app)
    # blueprint for auth routes in our app
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    # blueprint for non-auth parts of app
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app
