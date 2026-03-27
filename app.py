from flask import Flask, redirect, render_template, request, session
from helpers import apology, login_required, get_db, close_db
# Helper functions "apology, login_required" from CS50 Problem Set 9 (Finance)
import os
import random
import sqlite3
from werkzeug.security import check_password_hash, generate_password_hash


app = Flask(__name__)

# get secret key for sessions
app.secret_key = os.environ.get("SECRET_KEY")


# Create teardown function to ensure db shuts down properly after each request


@app.teardown_appcontext
def teardown_db(exception=None):
    close_db()


@app.after_request
def after_request(response):
    """Prevent the caching of dynamic HTML pages"""
    if response.content_type.startswith("text/html"):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Expires"] = 0
        response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """Homepage"""
    return render_template("index.html")


@app.route("/login", methods=["POST", "GET"])
def login():
    """Login page"""

    # Forget any user_id
    session.clear()

    # if form submitted
    if request.method == "POST":

        # verify both password and username are submitted
        if not request.form.get("username"):
            return apology("please provide username")

        elif not request.form.get("password"):
            return apology("please provide password")

        # get username from database
        db = get_db()
        cur = db.cursor()
        cur.execute("SELECT * FROM users WHERE username = ?", (request.form.get("username"),))
        db_user = cur.fetchone()
        cur.close()
        # ensure login is valid
        if db_user is None or not check_password_hash(
                db_user["hash"], request.form.get("password")
        ):
            return apology("invalid username or password")

        # remember login
        session["user_id"] = db_user["id"]

        # redirect back to homepage
        return redirect("/")

    else:  # if accessed through clicking a link or redirect
        return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    db = get_db()
    cur = db.cursor()
    if request.method == "POST":
        # check username exists
        if not request.form.get("username"):

            return apology("Username Required")
        # check password exists
        elif not request.form.get("password"):
            return apology("Password Required")
        # check Confirm_passoword exists:
        elif not request.form.get("confirmation"):
            return apology("confirm Password Required")
        # ensure password and confirmation match
        if request.form.get("password") != request.form.get("confirmation"):
            return apology("Passwords do not match")

        # check if username already in database otherwise add user to database and log them in
        try:
            cur.execute("INSERT INTO users (username,hash) VALUES (?,?)", (request.form.get(
                'username'), generate_password_hash(request.form.get('password'))))
            db.commit()
            cur.execute(
                "SELECT id FROM users WHERE username = ?", (request.form.get("username"),))
            session["user_id"] = cur.fetchone()["id"]
            cur.close()
            return redirect("/")

        except sqlite3.IntegrityError:
            return apology("Username already exists")
    else:
        return render_template("register.html")


@app.route("/logout")
def logout():
    """log the user out"""
    # remove user id
    session.clear()
    # redirect user
    return redirect("/")


@app.route("/test", methods=["POST", "GET"])
@login_required
def test():
    """typing test"""
    if request.method == "POST":
        db = get_db()
        cur = db.cursor()
        typed_text = request.form.get("typed_text")
        if not typed_text:
            return apology("You didn't type anything!")

        characters_typed = len(typed_text)
        original_chars = session["test_text"]
        wpm = (characters_typed/5)*2

        correct = 0
        for orig, typed in zip(original_chars, typed_text):
            if orig == typed:
                correct += 1

        accuracy = round(correct / len(typed_text) * 100, 2)
        adjusted_wpm = round(wpm * (accuracy / 100), 2)
        # add test results to database
        cur.execute(
            "INSERT INTO results (user_id, wpm, accuracy, adjusted_wpm, date_of_entry) VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)",
            (session["user_id"], wpm, accuracy, adjusted_wpm)
        )

        db.commit()
        cur.close()


        session["last_results"] = {
        "wpm": wpm,
        "accuracy": accuracy,
        "adjusted_wpm": adjusted_wpm
        }
        session.pop("test_text", None)

        return redirect("/results")

    else:
        with open("static/words.txt") as f:
            words = [line.strip() for line in f]
            # choose 75 random words from file
            test_words = random.sample(words, 75)
            text_string = " ".join(test_words)
            session["test_text"] = text_string
        return render_template("test.html", text=text_string)

@app.route("/results")
@login_required
def results():
    """ show user test results"""
    last = session.get("last_results")
    if not last:
        return redirect("/test")
    return render_template("results.html",**last)
#third party ai tool chatgpt used to help debug errors in code

@app.route("/top10")
@login_required
def top10():
    """display user's top 10 best test results"""
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT * FROM results JOIN users ON results.user_id=users.id WHERE user_id = ? ORDER BY adjusted_wpm DESC LIMIT 10",(session["user_id"],)) # grab users 10 best results
    user_results = cur.fetchall()
    cur.close()
    return render_template("top10.html",user_results=user_results)

@app.route("/leaderboard")
def leaderboard():
    """display the global top 10 best test results"""
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT * FROM results JOIN users ON results.user_id=users.id ORDER BY adjusted_wpm DESC LIMIT 10") # grab users 10 best results
    query_results = cur.fetchall()
    cur.close()
    return render_template("leaderboard.html",query_results=query_results)


@app.route("/change", methods=["GET", "POST"])
@login_required
def change():
    """change the password of user"""
    db = get_db()
    cur = db.cursor()
    if request.method == "GET":
        return render_template("change.html")
    else:
        if not request.form.get("old_password") or not request.form.get("new_password") or not request.form.get("confirmation"):
            return apology("Must fill out all fields")
        # ensure old_password is correct
        cur.execute("SELECT hash FROM users WHERE id = ?",(session["user_id"],))
        old = cur.fetchone()["hash"]
        if not check_password_hash(old, request.form.get("old_password")):
            return apology("incorrect password")
         # ensure new_password and confirmation match
        if request.form.get("new_password") != request.form.get("confirmation"):
            return apology("Passwords do not match")
        cur.execute("UPDATE users SET hash = ? WHERE ID = ?", (generate_password_hash(
                        request.form.get("new_password")), session["user_id"]))
        db.commit()
        cur.close()
    return redirect("/")

if __name__ == "__main__":
    app.run()