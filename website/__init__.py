from flask import Flask
from flask_login import LoginManager
import sqlite3
from .views import User


def init_db():
    # Init database
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            userId INTEGER PRIMARY KEY,
            username TEXT NOT NULL,
            passwordHash TEXT NOT NULL,
            userType TEXT NOT NULL
        )
    ''')
    # Topics table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS topics (
            topicId INTEGER PRIMARY KEY,
            topicName TEXT NOT NULL,
            path TEXT NOT NULL
        )
    ''')
    # QuestionSlots table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS questionSlots (
            slotId INTEGER PRIMARY KEY,
            topicId INTEGER,
            FOREIGN KEY(topicId) REFERENCES topics(topicId)
        )
    ''')
    # Questions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS questions (
            questionId INTEGER PRIMARY KEY,
            questionFunction TEXT NOT NULL,
            answer TEXT NOT NULL,
            choices TEXT NOT NULL,
            explanation TEXT NOT NULL,
            slotId INTEGER,
            FOREIGN KEY(slotId) REFERENCES questionSlots(slotId)
        )
    ''')
    # Progress table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS progress (
            completion REAL NOT NULL,
            accuracy REAL NOT NULL,
            userId INTEGER,
            topicId INTEGER,
            FOREIGN KEY(userId) REFERENCES users(userId),
            FOREIGN KEY(topicId) REFERENCES topics(topicId),
            PRIMARY KEY(userId, topicId)
        )
    ''')
    # Responses table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS responses (
            submittedAnswer TEXT NOT NULL,
            userId INTEGER,
            questionId INTEGER,
            FOREIGN KEY(userId) REFERENCES users(userId),
            FOREIGN KEY(questionId) REFERENCES questions(questionId),
            PRIMARY KEY(userId, questionId)
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
