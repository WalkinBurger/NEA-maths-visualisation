from flask import Flask
import sqlite3

def init_db():
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
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'MathsVis'
    
    from .views import views

    app.register_blueprint(views, url_prefix="/")

    return app