from flask import Blueprint, render_template, request, redirect, url_for, session, Response, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from app.models import AppUser, Company, Metric, AuditLog
import csv
import io
from app.scraper import scrape_website

bp = Blueprint('main', __name__)

METRIC_OPTIONS = ["Pricing", "Features", "Reviews", "Funding", "Hiring"]

@bp.route('/')
def index():
    return render_template('index.html')

# ============================
# REGISTER
# ============================
@bp.route('/register', methods=['GET', 'POST'])
def register():
    message = ""

    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        email_exists = AppUser.query.filter_by(email=email).first()
        if email_exists:
            return render_template('register.html', message="Dit e-mailadres is al in gebruik.")

        user_exists = AppUser.query.filter_by(username=username).first()
        if user_exists:
            return render_template('register.html', message="Gebruikersnaam bestaat al.")

        new_user = AppUser(
            username=username,
            email=email,
            password_hash=generate_password_hash(password)
        )

        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('main.login'))

    return render_template('register.html', message=message)

# ============================
# LOGIN
# ============================
@bp.route('/login', methods=['GET', 'POST'])
def login():
    message = ""

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = AppUser.query.filter_by(email=email).first()

        if not user or not check_password_hash(user.password_hash, password):
            return render_template('login.html', message="Ongeldig e-mailadres of wachtwoord")

        session['user_id'] = user.user_id
        session['username'] = user.username

        return redirect(url_for('main.dashboard'))

    return render_template('login.html', message=message)

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('main.login'))

# ============================
# DASHBOARD
# ============================
@bp.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('main.login'))

    scrape_result = None

    if request.method == 'POST':
        form_type = request.form.get('form_type')

        if form_type == 'watchlist_config':
            selected_company_ids = request.form.getlist('companies')
            selected_metrics = request.form.getlist('metrics')
            session['watchlist_companies'] = [int(cid) for cid in selected_company_ids]
            session['watchlist_metrics'] = [m for m in selected_metrics if m in METRIC_OPTIONS]

        elif form_type == 'scrape':
            url = request.form.get('scrape_url')
            scrape_result = scrape_website(url)

            if scrape_result and not scrape_result.get('error'):
                existing_company = Company.query.filter_by(website_url=url).first()

                if not existing_company:
                    new_company = Company(
                        name=scrape_result['title'] or 'Onbekend bedrijf',
                        website_url=url,
                        headquarters=scrape_result.get('headquarters'),
                        team_size=scrape_result.get('team_size'),
                        funding=scrape_result.get('funding'),

                        office_locations=scrape_result.get('office_locations'),
                        funding_history=scrape_result.get('funding_history'),
                        traction_signals=scrape_result.get('traction_signals')
                    )

                    db.session.add(new_company)
                    db.session.flush()
                    db.session.add(AuditLog(
                        company_id=new_company.company_id,
                        source_name='Scraper',
                        source_url=url
                    ))
                    db.session.commit()

    watchlist_company_ids = session.get('watchlist_companies', [])
    watchlist_metrics = session.get('watchlist_metrics', [])

    companies_in_watchlist = Company.query.filter(Company.company_id.in_(watchlist_company_ids)).all() if watchlist_company_ids else []

    watchlist_names = [c.name for c in companies_in_watchlist]
    all_companies = Company.query.all()

    return render_template(
        'dashboard.html',
        scrape_result=scrape_result,
        watchlist=watchlist_names,
        alerts=[],
        metric_options=METRIC_OPTIONS,
        metrics_selected=watchlist_metrics,
        companies=all_companies
    )

# ============================
# COMPANY DETAIL → BASELINE REPORT
# ============================
@bp.route('/company/<int:company_id>')
def company_detail(company_id):
    if 'user_id' not in session:
        return redirect(url_for('main.login'))

    company = Company.query.get_or_404(company_id)
    return render_template('company_detail.html', company=company)

# ============================
# WATCHLIST
# ============================
@bp.route('/watchlist')
def watchlist():
    if 'user_id' not in session:
        return redirect(url_for('main.login'))

    company_ids = session.get('watchlist_companies', [])
    metrics_selected = session.get('watchlist_metrics', [])

    companies = Company.query.filter(Company.company_id.in_(company_ids)).all() if company_ids else []

    comparison_rows = []
    for c in companies:
        metric_values = {}
        for m in metrics_selected:
            metric_obj = Metric.query.filter(
                Metric.company_id == c.company_id,
                db.func.lower(Metric.name) == m.lower()
            ).first()
            metric_values[m] = metric_obj.value if metric_obj else '–'
        comparison_rows.append({'company': c, 'metrics': metric_values})

    try:
        logs_by_company = {
            c.company_id: AuditLog.query.filter_by(company_id=c.company_id)
            .order_by(AuditLog.retrieved_at.desc()).all()
            for c in companies
        }
    except Exception:
        logs_by_company = {c.company_id: [] for c in companies}

    return render_template(
        'watchlist.html',
        metrics=metrics_selected,
        rows=comparison_rows,
        companies=companies,
        logs_by_company=logs_by_company
    )

# ============================
# COMPANIES OVERVIEW
# ============================
@bp.route('/companies', methods=['GET', 'POST'])
def companies():
    if 'user_id' not in session:
        return redirect(url_for('main.login'))

    message = ""

    if request.method == 'POST':
        form_type = request.form.get('form_type')

        if form_type == 'add_company':
            try:
                name = request.form.get('name')
                website_url = request.form.get('website_url')
                headquarters = request.form.get('headquarters')
                team_size = request.form.get('team_size')
                funding = request.form.get('funding')

                new_company = Company(
                    name=name,
                    website_url=website_url,
                    headquarters=headquarters,
                    team_size=team_size,
                    funding=funding
                )

                db.session.add(new_company)
                db.session.flush()
                db.session.add(AuditLog(
                    company_id=new_company.company_id,
                    source_name='Manual Entry',
                    source_url=website_url or '—'
                ))
                db.session.commit()
                message = f"✅ {name} toegevoegd!"

            except Exception as e:
                message = f"❌ Fout bij toevoegen: {e}"

        elif form_type == 'add_to_watchlist':
            cid = int(request.form.get('company_id'))
            existing_ids = session.get('watchlist_companies', [])

            if cid not in existing_ids:
                existing_ids.append(cid)

            session['watchlist_companies'] = existing_ids
            message = "✔ Toegevoegd aan watchlist"

    companies = Company.query.all()
    return render_template('companies.html', companies=companies, message=message)


