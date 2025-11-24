from flask import Blueprint, render_template, request, redirect, url_for, session, Response, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from app.models import AppUser, Company, Metric, AuditLog
import csv
import io
from app.scraper import scrape_website

bp = Blueprint('main', __name__)

# Eenvoudige, statische metrische opties (niet-destructief toegevoegd)
METRIC_OPTIONS = ["Pricing", "Features", "Reviews", "Funding", "Hiring"]

# ============================
# INDEX
# ============================
@bp.route('/')
def index():
    return render_template('index.html')


# ============================
# REGISTER (database)
# ============================
@bp.route('/register', methods=['GET', 'POST'])
def register():
    message = ""

    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        # bestaat e-mailadres al?
        email_exists = AppUser.query.filter_by(email=email).first()
        if email_exists:
            message = "Dit e-mailadres is al in gebruik."
            return render_template('register.html', message=message)

        # bestaat gebruikersnaam al?
        user_exists = AppUser.query.filter_by(username=username).first()
        if user_exists:
            message = "Gebruikersnaam bestaat al."
            return render_template('register.html', message=message)

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
# LOGIN (database)
# ============================
@bp.route('/login', methods=['GET', 'POST'])
def login():
    message = ""

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = AppUser.query.filter_by(email=email).first()

        if not user or not check_password_hash(user.password_hash, password):
            message = "Ongeldig e-mailadres of wachtwoord"
            return render_template('login.html', message=message)

        session['user_id'] = user.user_id
        session['username'] = user.username

        return redirect(url_for('main.dashboard'))

    return render_template('login.html', message=message)

# ============================
# LOGOUT
# ============================
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

    # Bepaal welke actie de POST is (scrape vs configuratie watchlist)
    if request.method == 'POST':
        form_type = request.form.get('form_type')

        if form_type == 'watchlist_config':
            # Opslaan geselecteerde companies & metrics in de sessie (lichtgewicht)
            selected_company_ids = request.form.getlist('companies')
            selected_metrics = request.form.getlist('metrics')
            try:
                session['watchlist_companies'] = [int(cid) for cid in selected_company_ids]
            except ValueError:
                session['watchlist_companies'] = []
            # Alleen metrische opties opslaan die bestaan
            session['watchlist_metrics'] = [m for m in selected_metrics if m in METRIC_OPTIONS]
        else:
            # Originele scrape functionaliteit onaangeroerd behoud
            url = request.form.get('scrape_url')
            if url:
                scrape_result = scrape_website(url)
                if scrape_result and not scrape_result.get('error'):
                    existing_company = Company.query.filter_by(website_url=url).first()
                    if not existing_company:
                        new_company = Company(
                            name=scrape_result['title'] or 'Onbekend bedrijf',
                            website_url=url,
                            headquarters=scrape_result.get('headquarters') or 'Onbekend',
                            team_size=scrape_result.get('team_size'),
                            funding=scrape_result.get('funding')
                        )
                        db.session.add(new_company)
                        db.session.flush()
                        db.session.add(AuditLog(
                            company_id=new_company.company_id,
                            source_name='Scraper',
                            source_url=url
                        ))
                        db.session.commit()

    # Ophalen watchlist vanuit sessie
    watchlist_company_ids = session.get('watchlist_companies', [])
    watchlist_metrics = session.get('watchlist_metrics', [])
    companies_in_watchlist = []
    if watchlist_company_ids:
        companies_in_watchlist = Company.query.filter(Company.company_id.in_(watchlist_company_ids)).all()

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
# WATCHLIST OVERZICHT
# ============================
@bp.route('/watchlist')
def watchlist():
    if 'user_id' not in session:
        return redirect(url_for('main.login'))

    company_ids = session.get('watchlist_companies', [])
    metrics_selected = session.get('watchlist_metrics', [])

    companies = []
    if company_ids:
        companies = Company.query.filter(Company.company_id.in_(company_ids)).all()

    # Simpele metric lookup per company (eerste match, case-insensitive)
    comparison_rows = []
    for c in companies:
        metric_values = {}
        for m in metrics_selected:
            metric_obj = Metric.query.filter(
                Metric.company_id == c.company_id,
                db.func.lower(Metric.name) == m.lower()
            ).first()
            metric_values[m] = metric_obj.value if metric_obj and metric_obj.value is not None else '–'
        comparison_rows.append({'company': c, 'metrics': metric_values})

    # Audit logs per company
    logs_by_company = {}
    if companies:
        for c in companies:
            logs_by_company[c.company_id] = AuditLog.query.filter_by(company_id=c.company_id).order_by(AuditLog.retrieved_at.desc()).all()

    return render_template('watchlist.html', metrics=metrics_selected, rows=comparison_rows, companies=companies, logs_by_company=logs_by_company)


# ============================
# COMPANIES
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
                    team_size=team_size or None,
                    funding=funding or None
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
            company_id = request.form.get('company_id')
            try:
                cid = int(company_id)
                existing_ids = session.get('watchlist_companies', [])
                if cid not in existing_ids:
                    existing_ids.append(cid)
                    session['watchlist_companies'] = existing_ids
                message = "✅ Bedrijf toegevoegd aan watchlist"
            except (TypeError, ValueError):
                message = "❌ Ongeldig company_id"

    companies = Company.query.all()
    return render_template('companies.html', companies=companies, message=message)


# ============================
# EXPORT AUDIT LOGS (Watchlist)
# ============================
@bp.route('/watchlist/audit/export')
def export_watchlist_audit():
    if 'user_id' not in session:
        return redirect(url_for('main.login'))

    fmt = request.args.get('format', 'csv').lower()
    company_ids = session.get('watchlist_companies', [])
    if not company_ids:
        if fmt == 'json':
            return jsonify([])
        return Response('', mimetype='text/csv', headers={'Content-Disposition': 'attachment; filename=audit_logs.csv'})

    logs = AuditLog.query.filter(AuditLog.company_id.in_(company_ids)).order_by(AuditLog.retrieved_at.desc()).all()
    company_map = {c.company_id: c.name for c in Company.query.filter(Company.company_id.in_(company_ids)).all()}

    if fmt == 'json':
        payload = [
            {
                'company_id': l.company_id,
                'company_name': company_map.get(l.company_id, ''),
                'source_name': l.source_name,
                'source_url': l.source_url,
                'retrieved_at': l.retrieved_at.isoformat() if l.retrieved_at else None
            }
            for l in logs
        ]
        return jsonify(payload)

    # CSV export
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['company_id', 'company_name', 'source_name', 'source_url', 'retrieved_at'])
    for l in logs:
        writer.writerow([
            l.company_id,
            company_map.get(l.company_id, ''),
            l.source_name,
            l.source_url,
            l.retrieved_at.isoformat() if l.retrieved_at else ''
        ])
    csv_data = output.getvalue()
    output.close()
    return Response(csv_data, mimetype='text/csv', headers={'Content-Disposition': 'attachment; filename=audit_logs.csv'})


# ============================
# SCRAPE PAGE
# ============================
@bp.route('/scrape', methods=['GET', 'POST'])
def scrape():
    if 'user_id' not in session:
        return redirect(url_for('main.login'))

    result = None
    if request.method == 'POST':
        url = request.form.get('url')
        if url:
            result = scrape_website(url)

    return render_template('scrape.html', result=result)






























