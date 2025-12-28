from flask import Blueprint, render_template, request, flash, redirect, url_for, session, abort
from flask_login import login_user, login_required, logout_user, current_user, UserMixin
from functools import wraps
import sqlite3
import datetime
import sys
import os
import pprint
from argon2 import PasswordHasher, exceptions
ph = PasswordHasher()

def sprint(msg, colour=0):
    print(f"\033[{colour}m{msg}\033[0m")

# User class model for flask-login
class User(UserMixin):
    def __init__(self, username=None, id=None):
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        if username:
            user = cursor.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()
        if not user:
            if id:
                user = cursor.execute("SELECT * FROM users WHERE userId=?", (id,)).fetchone()
            else:
                user = cursor.execute("SELECT * FROM users WHERE userId=?", (username,)).fetchone()
        conn.close()
        if user:
            # Initialises attributes if the user exists in the database
            self.id = user[0]
            self.username =  user[1]
            self.passwordHash= user[2]
            self.role = user[3]

# Role base access method
def role_required(*role):
    def wrapper(func):
        @wraps(func)
        def decorated_view(*args, **kwargs):
            if not hasattr(current_user, "role"):
                return abort(403)
            elif current_user.role not in role:
                return abort(403)
            return func(*args, **kwargs)
        return decorated_view
    return wrapper

def validation(username, password):
    specialChar = " !\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~"
    if len(username) > 20:
        return "Username must be within than 20 characters."
    elif len(password) > 30 or len(password) < 8:
        return "Password must be within 8 to 30 characters."
    elif not any(ch.isdigit() for ch in password):
        return "Password must contain at least one number."
    elif not any(ch.islower() for ch in password):
        return "Password must contain at least one lowercase letter."
    elif not any(ch.isupper() for ch in password):
        return "Password must contain at least one uppercase letter."
    elif not any(ch in specialChar for ch in password):
        return "Password must contain at least one special character."
    else:
        return True

views = Blueprint("views", __name__)

@views.route("/")
def home():
    # Anonymous user role if user is not logged in
    if hasattr(current_user, "role"):
        user_type = current_user.role
    else:
        user_type = "anon"
    # Query all topics
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    search = request.args.get('q')
    topics = cursor.execute("SELECT * FROM topics ORDER BY path DESC").fetchall()
    # Format topics into a flatten 2D array
    topics_flatten = []
    for topicId, topicName, path in topics:
        for i,category in enumerate(path.split('/')):
            if category[-5:] == ".html":
                topics_flatten.append([topicName, i, topicId])
            elif not [category.replace('-', ' '), i] in topics_flatten:
                topics_flatten.append([category.replace('-', ' '), i])
    return render_template("index.html", user=current_user, user_type=user_type, topics=topics_flatten)

@views.route("/login", methods=["GET", "POST"])
def login():
    # Limit attempts to 3 incorrect attempts
    if session.get("attempt") == None:
            session["attempt"] = 4
    elif session["attempt"] == 1 and not session.get("block"):
        session["block"] = datetime.datetime.now() + datetime.timedelta(minutes=10)
    # 'block' cookie in session to block user who attempted to log in too many times
    if not session.get("block"):
        pass
    elif session["block"].replace(tzinfo=None) <= (datetime.datetime.now()):
        session["attempt"] = 4
        session.pop("block")
    else:
        flash("You have attempted to log in too many times, please try again later.", category="error")
    # POST request to log in
    if request.method == "POST" and not session.get("block"):
        # Get the account details from the form
        username = request.form.get("username")
        password = request.form.get("password")
        # Password & username validation
        if validation(username, password) == True:
            conn = sqlite3.connect("database.db")
            cursor = conn.cursor()
            # Query the account details
            user_query = cursor.execute("SELECT * FROM users WHERE username=?",
            (username,)).fetchone()
            if user_query: # Account with this username exists
                try:# Correct password
                    ph.verify(user_query[2], password)
                    conn.close()
                    user = User(username=username)
                    login_user(user, remember=True)
                    session["attempt"] = 4
                    return redirect(url_for("views.home"))
                except exceptions.VerifyMismatchError:
                    pass
            conn.close()
        session["attempt"] -= 1
        if session["attempt"] != 0:
            flash(f"Incorrect account details, please try again. (attempts remaining: {session["attempt"]-1})", category="error")
    return render_template("login.html", user=current_user)
    

@views.route("/signup", methods=["GET", "POST"])
def signup():
    # POST request to sign up
    if request.method == "POST":
        # Get the account details from the form
        username = request.form.get("username")
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")
        usertype = request.form.get("usertype")

        # Password & username validation
        if validation(username, password1) != True:
            flash(validation(username, password1), category="error")
        elif password1 != password2:
            flash("Passwords do not match.", category="error")
        else: # Valid sign up
            conn = sqlite3.connect("database.db")
            cursor = conn.cursor()
            # Create account if username does not exist
            if cursor.execute("SELECT username FROM users WHERE username=?", (username,)).fetchone():
                flash("This username already exists.", category="error")
                conn.close()
            else:
                cursor.execute("INSERT INTO users (username, passwordHash, userType) VALUES (?, ?, ?)",
                (username, ph.hash(password1), usertype))
                conn.commit()
                conn.close()
                user = User(username=username)
                login_user(user, remember=True)
                flash("Account successfully created", category="success")
                return redirect(url_for("views.home"))
    return render_template("signup.html", user=current_user)

@views.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("views.login"))

@views.route("topic/<int:topicId>")
@login_required
def topic(topicId):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    path = cursor.execute("SELECT path FROM topics WHERE topicId=?", (topicId,)).fetchone()[0]
    return render_template(f"resources/{path}", user=current_user)

@views.route("/dashboard")
@login_required
@role_required("admin")
def dashboard():
    return render_template("dashboard.html", user=current_user)

@views.errorhandler(403)
def error403(error):
    return render_template("errors/403.html", user=current_user), 403