from flask import render_template, Blueprint, request, redirect, url_for, flash

bp = Blueprint('auth', __name__)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Here you would handle the login logic
        username = request.form['username']
        password = request.form['password']
        # Validate credentials (this is just a placeholder)
        if username == 'admin' and password == 'password':
            flash('Login successful!', 'success')
            return redirect(url_for('main.index'))
        else:
            flash('Invalid credentials. Please try again.', 'danger')
    return render_template('auth/login.html')

@bp.route('/logout')
def logout():
    # Here you would handle the logout logic
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Here you would handle the registration logic
        username = request.form['username']
        password = request.form['password']
        # Save the new user (this is just a placeholder)
        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html')

def init_app(app):
    app.register_blueprint(bp)