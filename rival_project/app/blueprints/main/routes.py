from flask import render_template, Blueprint, request, redirect, url_for, flash, session
from app.extensions import db
from app.models.company import Company
from app.models.watchlist import Watchlist
from .forms import CompanyForm

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
    user_id = session.get('user_id')
    if not user_id:
        flash('Log in om je watchlist te bekijken.', 'info')
        return redirect(url_for('auth.login'))
    items = (db.session.query(Watchlist)
             .filter_by(user_id=user_id)
             .join(Company, Watchlist.company_id == Company.id)
             .all())
    return render_template('watchlist.html', items=items)

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

@bp.route('/companies', methods=['GET', 'POST'])
def companies():
    form = CompanyForm()
    if form.validate_on_submit():
        c = Company(name=form.name.data.strip(), url=(form.url.data or '').strip() or None)
        db.session.add(c)
        db.session.commit()
        flash('Company added.', 'success')
        return redirect(url_for('main.companies'))
    companies = Company.query.order_by(Company.created_at.desc()).all()
    return render_template('companies.html', form=form, companies=companies)

@bp.route('/watchlist/add/<int:company_id>', methods=['POST'])
def watchlist_add(company_id):
    user_id = session.get('user_id')
    if not user_id:
        flash('Log in om je watchlist te gebruiken.', 'info')
        return redirect(url_for('auth.login'))
    # Ensure company exists
    company = Company.query.get_or_404(company_id)
    # Upsert-like: ignore if exists
    existing = Watchlist.query.filter_by(user_id=user_id, company_id=company.id).first()
    if existing:
        flash('Staat al in je watchlist.', 'info')
    else:
        db.session.add(Watchlist(user_id=user_id, company_id=company.id))
        db.session.commit()
        flash('Toegevoegd aan je watchlist.', 'success')
    return redirect(request.referrer or url_for('main.companies'))

@bp.route('/watchlist/remove/<int:item_id>', methods=['POST'])
def watchlist_remove(item_id):
    user_id = session.get('user_id')
    if not user_id:
        flash('Log in om je watchlist te gebruiken.', 'info')
        return redirect(url_for('auth.login'))
    item = Watchlist.query.get_or_404(item_id)
    if item.user_id != user_id:
        flash('Niet toegestaan.', 'danger')
        return redirect(url_for('main.watchlist'))
    db.session.delete(item)
    db.session.commit()
    flash('Verwijderd uit je watchlist.', 'success')
    return redirect(url_for('main.watchlist'))