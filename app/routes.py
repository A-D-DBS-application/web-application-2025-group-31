from flask import Blueprint, render_template, request, redirect, url_for, session, Response, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from app.models import AppUser, Company, Metric, AuditLog
import csv
import io
from app.scraper import scrape_website

bp = Blueprint('main', __name__)

METRIC_OPTIONS = ["Pricing", "Features", "Reviews", "Funding", "Hiring"]


# =====================================================
# HELPER FUNCTIES (belangrijk voor correcte Supabase types)
# =====================================================

def safe_int(x):
    """Zet string of AI-output om naar integer of None."""
    try:
        return int(str(x).replace(",", "").strip())
    except:
        return None


def safe_float(x):
    """Zet currency/tekst om naar float (Supabase NUMERIC)."""
    if x is None:
        return None
    try:
        cleaned = (
            str(x)
            .replace("€", "")
            .replace("$", "")
            .replace(",", "")
            .replace("m", "000000")
            .replace("M", "000000")
            .strip()
        )
        return float(cleaned)
    except:
        return None


# =====================================================
# INDEX
# =====================================================

@bp.route('/')
def index():
    return render_template('index.html')


# =====================================================
# REGISTER
# =====================================================

@bp.route('/register', methods=['GET', 'POST'])
def register():
    message = ""

    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        if AppUser.query.filter_by(email=email).first():
            return render_template('register.html', message="Dit e-mailadres is al in gebruik.")

        if AppUser.query.filter_by(username=username).first():
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


# =====================================================
# LOGIN
# =====================================================

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


# =====================================================
# DASHBOARD
# =====================================================

@bp.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('main.login'))

    user = AppUser.query.get(session["user_id"])
    scrape_result = None

    if request.method == 'POST':
        form_type = request.form.get('form_type')

        if form_type == 'watchlist_config':
            session['watchlist_companies'] = [int(cid) for cid in request.form.getlist('companies')]
            session['watchlist_metrics'] = [
                m for m in request.form.getlist('metrics') if m in METRIC_OPTIONS
            ]

        elif form_type == 'scrape':
            url = request.form.get('scrape_url')
            return redirect(url_for('main.scrape') + f"?url={url}")

    watchlist_ids = session.get('watchlist_companies', [])
    metrics_selected = session.get('watchlist_metrics', [])

    companies_watchlist = Company.query.filter(
        Company.company_id.in_(watchlist_ids)
    ).all() if watchlist_ids else []

    all_companies = Company.query.all()

    return render_template(
        'dashboard.html',
        user=user,
        scrape_result=scrape_result,
        watchlist=[c.name for c in companies_watchlist],
        alerts=[],
        metric_options=METRIC_OPTIONS,
        metrics_selected=metrics_selected,
        companies=all_companies
    )


# =====================================================
# COMPANY DETAIL
# =====================================================

@bp.route('/company/<int:company_id>')
def company_detail(company_id):
    if 'user_id' not in session:
        return redirect(url_for('main.login'))

    company = Company.query.get_or_404(company_id)
    return render_template('company_detail.html', company=company)


# =====================================================
# WATCHLIST
# =====================================================

@bp.route('/watchlist')
def watchlist():
    if 'user_id' not in session:
        return redirect(url_for('main.login'))

    ids = session.get('watchlist_companies', [])
    try:
        ids = [int(cid) for cid in ids]
    except:
        ids = []

    metrics_selected = session.get('watchlist_metrics', [])
    companies = Company.query.filter(Company.company_id.in_(ids)).all() if ids else []

    comparison_rows = []
    for c in companies:
        metric_values = {
            m: (
                Metric.query.filter(
                    Metric.company_id == c.company_id,
                    db.func.lower(Metric.name) == m.lower()
                ).first().value
                if Metric.query.filter(
                    Metric.company_id == c.company_id,
                    db.func.lower(Metric.name) == m.lower()
                ).first()
                else "–"
            )
            for m in metrics_selected
        }
        comparison_rows.append({'company': c, 'metrics': metric_values})

    logs_by_company = {
        c.company_id: AuditLog.query.filter_by(company_id=c.company_id)
        .order_by(AuditLog.retrieved_at.desc()).all()
        for c in companies
    }

    return render_template(
        'watchlist.html',
        metrics=metrics_selected,
        rows=comparison_rows,
        companies=companies,
        logs_by_company=logs_by_company
    )


# =====================================================
# COMPANIES OVERVIEW
# =====================================================

@bp.route('/companies', methods=['GET', 'POST'])
def companies():
    if 'user_id' not in session:
        return redirect(url_for('main.login'))

    message = ""

    if request.method == 'POST':
        form_type = request.form.get('form_type')

        if form_type == 'add_company':
            try:
                new_company = Company(
                    name=request.form.get('name'),
                    website_url=request.form.get('website_url'),
                    headquarters=request.form.get('headquarters'),
                    team_size=safe_int(request.form.get('team_size')),
                    funding=safe_float(request.form.get('funding'))
                )

                db.session.add(new_company)
                db.session.flush()
                db.session.add(AuditLog(
                    company_id=new_company.company_id,
                    source_name="Manual entry",
                    source_url=new_company.website_url or "—"
                ))
                db.session.commit()
                message = "✔ Bedrijf toegevoegd!"

            except Exception as e:
                message = f"❌ Fout: {e}"

        elif form_type == 'add_to_watchlist':
            cid = int(request.form.get('company_id'))
            wl = session.get('watchlist_companies', [])
            if cid not in wl:
                wl.append(cid)
            session['watchlist_companies'] = wl
            message = "✔ Toegevoegd aan watchlist"

    all_companies = Company.query.all()
    return render_template('companies.html', companies=all_companies, message=message)


# =====================================================
# SCRAPE PAGE (AI + AUTO SAVE → Supabase)
# =====================================================

@bp.route('/scrape', methods=['GET', 'POST'])
def scrape():
    if 'user_id' not in session:
        return redirect(url_for('main.login'))

    url_from_query = request.args.get("url")

    if request.method == 'GET' and not url_from_query:
        return render_template('scrape.html', result=None)

    url = url_from_query or request.form.get('url')
    if not url:
        return render_template('scrape.html', result={'error': "Geen URL opgegeven."})

    result = scrape_website(url)
    if result.get("error"):
        return render_template('scrape.html', result=result)

    existing = Company.query.filter_by(website_url=url).first()

    # -----------------------------
    # UPDATE bestaand bedrijf
    # -----------------------------
    if existing:
        existing.name = result.get("title") or existing.name

        existing.headquarters = result.get("headquarters")
        existing.office_locations = result.get("office_locations")
        existing.team_size = safe_int(result.get("team_size"))
        existing.funding = safe_float(result.get("funding"))
        existing.funding_history = result.get("funding_history")
        existing.traction_signals = result.get("traction_signals")

        existing.ai_summary = result.get("ai_summary")
        existing.value_proposition = result.get("value_proposition")
        existing.product_description = result.get("product_description")
        existing.target_segment = result.get("target_segment")
        existing.pricing = result.get("pricing")
        existing.key_features = result.get("key_features")
        existing.competitors = result.get("competitors")

        db.session.commit()
        return redirect(url_for('main.company_detail', company_id=existing.company_id))

    # -----------------------------
    # NIEUW bedrijf
    # -----------------------------
    new_company = Company(
        name=result.get("title") or "Onbekend bedrijf",
        website_url=url,

        headquarters=result.get("headquarters"),
        office_locations=result.get("office_locations"),
        team_size=safe_int(result.get("team_size")),
        funding=safe_float(result.get("funding")),
        funding_history=result.get("funding_history"),
        traction_signals=result.get("traction_signals"),

        ai_summary=result.get("ai_summary"),
        value_proposition=result.get("value_proposition"),
        product_description=result.get("product_description"),
        target_segment=result.get("target_segment"),
        pricing=result.get("pricing"),
        key_features=result.get("key_features"),
        competitors=result.get("competitors")
    )

    db.session.add(new_company)
    db.session.flush()

    db.session.add(AuditLog(
        company_id=new_company.company_id,
        source_name="Scraper + AI",
        source_url=url
    ))
    db.session.commit()

    return redirect(url_for('main.company_detail', company_id=new_company.company_id))


# =====================================================
# WEEKLY MAIL SETTINGS
# =====================================================

@bp.route("/weekly-mail-settings")
def weekly_mail_settings():
    if "user_id" not in session:
        return redirect(url_for("main.login"))

    user = AppUser.query.get(session["user_id"])
    return render_template("weekly_mail.html", user=user)


@bp.route("/update-weekly-mail", methods=["POST"])
def update_weekly_mail():
    if "user_id" not in session:
        return redirect(url_for("main.login"))

    user = AppUser.query.get(session["user_id"])
    user.weekly_digest = request.form.get("digest") == "on"
    db.session.commit()

    return redirect(url_for("main.weekly_mail_settings"))

































