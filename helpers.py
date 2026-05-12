from flask import redirect, session
from functools import wraps

# CODE BELOW WAS PROVIDED BY THE CS50 PROBLEM SET 9 - FINANCE - helpers.py

# THE PURPOSE OF THIS CODE IS FOR WHEN A USER ACCESSES DIFFERENT PAGES ON THE WEBSITE,
# THIS FUNCTION RUNS A CHECK TO SEE IF THE USER IS LOGGED IN FIRST BEFORE DISPLAYING THE PAGE

# THE ORIGINAL DECORATOR WAS PROVIDED BY THE FLASK DOCUMENTATION SITE: https://flask.palletsprojects.com/en/latest/
# THROUGH THE LOGIN REQUIRED DECORATOR: https://flask.palletsprojects.com/en/latest/patterns/viewdecorators/

# CITED CODE BEGINS HERE

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

# CITED CODE ENDS HERE
