from flask import Blueprint, render_template, request, flash
import sqlite3

views = Blueprint("views", __name__)

@views.route("/login", methods=["GET", "POST"])
def login():
    return render_template("login.html")

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
        specialChar = " !\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~"
        if len(username) > 20:
            flash("Username must be within than 20 characters.")
        elif len(password1) > 30 or len(password1) < 8:
            flash("Password must be within 8 to 30 characters.")
        elif not any(ch.isdigit() for ch in password1):
            flash("Password must contain at least one number.")
        elif not any(ch.islower() for ch in password1):
            flash("Password must contain at least one lowercase letter.")
        elif not any(ch.isupper() for ch in password1):
            flash("Password must contain at least one uppercase letter.")
        elif not any(ch in specialChar for ch in password1):
            flash("Password must contain at least one special character.")
        elif password1 != password2:
            flash("Passwords do not match.")
        else: # Valid sign up
            conn = sqlite3.connect("database.db")
            cursor = conn.cursor()
            # Create account if username does not existD
            if cursor.execute("SELECT username FROM users WHERE username=?", (username,)).fetchone():
                flash("This username already exists.")
                conn.close()
            else:
                cursor.execute("INSERT INTO users (username, passwordHash, userType) VALUES (?, ?, ?)",
                (username, password1, usertype))
                conn.commit()
                conn.close()
                return render_template("login.html")

    return render_template("signup.html")