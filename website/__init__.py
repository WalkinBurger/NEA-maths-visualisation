from flask import Flask
from flask_login import LoginManager
import sqlite3
from .views import User


def init_db():
    # Init database
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            userId INTEGER PRIMARY KEY,
            username TEXT NOT NULL,
            passwordHash TEXT NOT NULL,
            userType TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def create_app():
    # Init app
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'MathsVis'
    app.config["SESSION_PERMANENT"] = False
    app.config["SESSION_TYPE"] = "filesystem"
    from .views import views
    app.register_blueprint(views, url_prefix="/")

    # Manage login
    login_manager = LoginManager()
    login_manager.login_view = "views.login"
    login_manager.init_app(app)
    @login_manager.user_loader
    def load_user(id):
        return User(id)

    return app