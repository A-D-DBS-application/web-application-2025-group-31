from functools import wraps
from flask import session, redirect, url_for, request, abort 
from app.models import AppUser

def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("main.login", next=request.url))
        return view(*args, **kwargs)
    return wrapped_view

def admin_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("main.login"))

        user = AppUser.query.get(session["user_id"])
        if not user:
            return redirect(url_for("main.login"))

        # Werkt met user.is_admin OF user.role == "admin"
        is_admin = bool(getattr(user, "is_admin", False)) or (getattr(user, "role", "") == "admin")
        if not is_admin:
            abort(403)

        return view(*args, **kwargs)
    return wrapped_view