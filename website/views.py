from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from flask_login import login_user, login_required, logout_user, current_user, UserMixin
import sqlite3
import datetime
from argon2 import PasswordHasher, exceptions
ph = PasswordHasher()

# User class model for flask-login
class User(UserMixin):
    def __init__(self, username=None, id=None):
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        if username:
            user = cursor.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()
        else:
            user = cursor.execute("SELECT * FROM users WHERE userId=?", (id,)).fetchone()
        conn.close()
        if user:
            # Initialises attributes if the user exists in the database
            self.id = user[0]
            self.username =  user[1]
            self.passwordHash= user[2]
            self.userType = user[3]

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
    return render_template("index.html", user=current_user)

@views.route("/login", methods=["GET", "POST"])
def login():
    # 'block' cookie in session to block user who attempted to log in too many times
    if not session.get("block"):
        pass
    elif session["block"] <= (datetime.datetime.now()).timestamp():
        session["attempt"] = 4
        session.pop("block")
    else:
        flash("You have attempted to log in too many times, please try again later.", category="error")
    # POST request to log in
    if request.method == "POST" and not session.get("block"):
        if not session.get("attempt"):
            session["attempt"] = 4
        elif session["attempt"] <= 1:
            session["block"] = (datetime.datetime.now() + datetime.timedelta(seconds=10)).timestamp()
            flash("You have attempted to log in too many times, please try again later.", category="error")
            return render_template("login.html", user=current_user)
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
                    user = User(username)
                    login_user(user, remember=True)
                    return redirect(url_for("views.home"))
                except exceptions.VerifyMismatchError:
                    pass
            conn.close()
        flash(f"Incorrect account details, please try again. (attempts remaining: {session["attempt"]-1})", category="error")
        session["attempt"] -= 1
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
            # Create account if username does not existD
            if cursor.execute("SELECT username FROM users WHERE username=?", (username,)).fetchone():
                flash("This username already exists.", category="error")
                conn.close()
            else:
                cursor.execute("INSERT INTO users (username, passwordHash, userType) VALUES (?, ?, ?)",
                (username, ph.hash(password1), usertype))
                conn.commit()
                conn.close()
                user = User(username)
                login_user(user, remember=True)
                flash("Account successfully created", category="success")
                return redirect(url_for("views.home"))
    return render_template("signup.html", user=current_user)

@views.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("views.login"))