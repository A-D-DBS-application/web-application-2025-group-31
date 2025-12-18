from functools import wraps
from flask import session, redirect, url_for, request

def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("main.login", next=request.url))
        return view(*args, **kwargs)
    return wrapped_view
