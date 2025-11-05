from flask import Blueprint, render_template

bp = Blueprint('admin', __name__)

@bp.route('/admin')
def admin_dashboard():
    return render_template('admin/dashboard.html')

def init_app(app):
    app.register_blueprint(bp)