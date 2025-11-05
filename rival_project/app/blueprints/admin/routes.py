from flask import Blueprint, render_template

bp = Blueprint('admin', __name__)

@bp.route('/admin')
def admin_dashboard():
    return render_template('admin/dashboard.html')

@bp.route('/admin/users')
def manage_users():
    return render_template('admin/manage_users.html')

@bp.route('/admin/settings')
def admin_settings():
    return render_template('admin/settings.html')

def init_app(app):
    app.register_blueprint(bp)