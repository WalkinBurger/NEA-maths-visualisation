from flask import Blueprint, render_template, request, flash, redirect, url_for, session, abort
from flask_login import login_user, login_required, logout_user, current_user, UserMixin
from functools import wraps
import sqlite3
import datetime
import sys
import os
import pprint
import json
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
    conn.close()
    # Format topics into a flatten 2D array
    topics_flatten = []
    for topicId, topicName, path in topics:
        for i,category in enumerate(path.split('/')):
            if category[-5:] == ".html":
                topics_flatten.append([topicName, i, topicId])
            elif not [category.replace('-', ' '), i] in topics_flatten:
                topics_flatten.append([category.replace('-', ' '), i])
    # Tutorial
    tutorial = 1 if request.args.get("tutorial") == "true" else request.args.get("tutorial")
    return render_template("index.html", user=current_user, session=session, user_type=user_type, topics=topics_flatten, tutorial=tutorial)

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
    return render_template("login.html", user=current_user, session=session)
    

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
                return redirect(url_for("views.home", tutorial="ask"))
    return render_template("signup.html", user=current_user, session=session)

@views.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You've logged out.", "success")
    return redirect(url_for("views.login"))

@views.route("topic/<int:topicId>", methods=["GET", "POST"])
@login_required
def topic(topicId):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    # POST request for updating the tables
    if request.method == "POST":
        response = json.loads(request.data)
        completion = cursor.execute("SELECT completion FROM progress WHERE userId=? AND topicId=?",
         (current_user.id, topicId,)).fetchone()
        completion = [0] if completion == None else completion
        cursor.execute("INSERT OR REPLACE INTO progress (completion, accuracy, userId, topicId) VALUES (?, ?, ?, ?)",
         (max(response["completion"],float(completion[0])), response["accuracy"], current_user.id, topicId,))
        if response["question"] != [None, None]:
            cursor.execute("INSERT OR REPLACE INTO responses (submittedAnswer, userId, questionId) VALUES (?, ?, ?)",
            (response["question"][1], current_user.id, response["question"][0],))
        conn.commit()
    # Directing to the topic resource page
    path = cursor.execute("SELECT path FROM topics WHERE topicId=?", (topicId,)).fetchone()[0]
    slots = cursor.execute("SELECT slotId FROM questionSlots WHERE topicId=?", (topicId,)).fetchall()
    questions = []
    for slotId in slots:
        for question in cursor.execute("SELECT * FROM questions WHERE slotId=?", (slotId[0],)).fetchall():
            questions.append(question)
    conn.close()
    questionsPath = os.path.relpath("website/static/questions.js", f"website/templates/resources/path")
    tutorial = 2 if request.args.get("tutorial") == "true" else None
    return render_template(f"resources/{path}", user=current_user, session=session, resource=True, questions=questions, questionsPath=questionsPath, tutorial=tutorial)

@views.route("/dashboard")
@login_required
@role_required("admin")
def dashboard():
    return render_template("dashboard.html", user=current_user, session=session)

@views.errorhandler(403)
def error403(error):
    return render_template("errors/403.html", user=current_user, session=session), 403

@views.errorhandler(404)
def error404(error):
    return render_template("errors/404.html", user=current_user, session=session), 404

@views.route("/help")
def helppage():
    return render_template("help.html", user=current_user, session=session)

@views.route("/settings", methods=["GET", "POST"])
def settings():
    if not hasattr(current_user, "role"):
        current_user.role = "anon"
    # Update settings
    if request.method == "POST":
        username = request.form.get("username")
        # Account settings updates
        if username:
            usertype = request.form.get("usertype")
            questions = request.form.get("questions")
            # Update questions-toggle
            if questions == "off":
                session["questionsDisabled"] = True
            elif session.get("questionsDisabled"):
                session.pop("questionsDisabled")
            conn = sqlite3.connect("database.db")
            cursor = conn.cursor()
            # User type change
            if current_user.username == username:
                cursor.execute("UPDATE users SET usertype=? WHERE username=?",(usertype,username))
                conn.commit()
                conn.close()
                current_user.role = usertype
                flash("Account settings updated successfully", "success")
            # Username change
            elif cursor.execute("SELECT username FROM users WHERE username=?",(username,)).fetchone():
                conn.close()
                flash("This username already exists, failed to update account.", category="error")
            else:
                cursor.execute("UPDATE users SET username=?, usertype=? WHERE userId=?",(username,usertype,current_user.id,))
                conn.commit()
                conn.close()
                current_user.username = username
                current_user.role = usertype
                flash("Account settings updated successfully", "success")
        # Appearance settings updates
        else:
            if request.form.get("theme") == "dark":
                session["darkTheme"] = True
            elif session.get("darkTheme"):
                session.pop("darkTheme")
            if request.form.get("contrast") == "on":
                session["highContrast"] = True
            elif session.get("highContrast"):
                session.pop("highContrast")
            flash("Appearance settings updated successfully", "success")
    tutorial = 4 if request.args.get("tutorial") == "true" else None
    return render_template("settings.html", user=current_user, session=session, tutorial=tutorial)

@views.route("/progress")
@login_required
@role_required("student")
def progress():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    progress = cursor.execute("SELECT completion, accuracy, topicId FROM progress WHERE userId=?",(current_user.id,)).fetchall()
    for i in range(len(progress)):
        progress[i] = list(progress[i])
        topic = cursor.execute("SELECT topicName FROM topics WHERE topicId=?", (progress[i][2],)).fetchone()
        for j in topic:
            progress[i].append(j)
    conn.close()
    tutorial = 3 if request.args.get("tutorial") == "true" else None
    return render_template("progress.html", user=current_user, session=session, progress=progress, tutorial=tutorial)
