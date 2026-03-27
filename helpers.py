from flask import redirect, render_template, session,g
from functools import wraps
import sqlite3


def apology(message, code=400):
    """Render message as an apology to user."""

    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [
            ("-", "--"),
            (" ", "-"),
            ("_", "__"),
            ("?", "~q"),
            ("%", "~p"),
            ("#", "~h"),
            ("/", "~s"),
            ('"', "''"),
        ]:
            s = s.replace(old, new)
        return s

    return render_template("apology.html", top=code, bottom=escape(message)), code


def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/latest/patterns/viewdecorators/
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated_function

def get_db():
    """returns sqlite3 connection"""
    if "db" not in g:
        g.db = sqlite3.connect("typing-test.db")
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db():
    """closes sqlite3 connection"""
    db = g.pop("db", None)
    if db is not None:
        db.close()


