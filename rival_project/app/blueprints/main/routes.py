from flask import render_template, Blueprint

bp = Blueprint('main', __name__, template_folder='templates')

@bp.route('/')
def index():
    return render_template('index.html')

@bp.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@bp.route('/company/<int:company_id>')
def company_detail(company_id):
    return render_template('company_detail.html', company_id=company_id)

@bp.route('/compare')
def compare():
    return render_template('compare.html')

@bp.route('/trends')
def trends():
    return render_template('trends.html')

@bp.route('/watchlist')
def watchlist():
    return render_template('watchlist.html')

@bp.route('/alerts')
def alerts():
    return render_template('alerts.html')

@bp.route('/settings')
def settings():
    return render_template('settings.html')

@bp.route('/export')
def export():
    return render_template('export.html')

def init_app(app):
    app.register_blueprint(bp)