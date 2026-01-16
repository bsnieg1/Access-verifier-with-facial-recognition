from functools import wraps
from flask import session, redirect, url_for

def admin_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if "admin_logged_in" not in session:
            return redirect(url_for("login"))
        return func(*args, **kwargs)
    return wrapper
