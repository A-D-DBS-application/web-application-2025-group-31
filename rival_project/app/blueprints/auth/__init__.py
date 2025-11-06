from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from app.blueprints.auth.forms import LoginForm, RegistrationForm
from app.extensions import db
from app.models.user import User

bp = Blueprint('auth', __name__)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.strip().lower()).first()
        if user and user.check_password(form.password.data):
            session['user_id'] = user.id
            flash('Login successful!', 'success')
            return redirect(url_for('main.dashboard'))
        flash('Invalid email or password.', 'danger')
    return render_template('auth/login.html', form=form)

@bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        username = form.username.data.strip()
        email = form.email.data.strip().lower()

        # Uniqueness checks
        if User.query.filter((User.username == username) | (User.email == email)).first():
            flash('Username or email already in use.', 'warning')
            return render_template('auth/register.html', form=form)

        user = User(username=username, email=email)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)

def init_app(app):
    app.register_blueprint(bp)

@bp.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))