from flask import Blueprint, render_template, redirect, url_for, flash, request
from app.blueprints.auth.forms import LoginForm, RegistrationForm

bp = Blueprint('auth', __name__)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        # Implement login logic here
        flash('Login successful!', 'success')
        return redirect(url_for('main.index'))
    return render_template('auth/login.html', form=form)

@bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        # Implement registration logic here
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)

def init_app(app):
    app.register_blueprint(bp)