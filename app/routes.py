from flask import Blueprint, render_template, request, redirect, url_for, session, Response, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from app.models import AppUser, Company, Metric, AuditLog, ChangeEvent
import csv
import io
from app.scraper import scrape_website

bp = Blueprint('main', __name__)

METRIC_OPTIONS = ["Pricing", "Features", "Reviews", "Funding", "Hiring"]

# ======================================================
# TEKST NORMALISATIE EN VERGELIJKING
# ======================================================

import difflib
import re

def normalize_text(s: str):
    if not s:
        return ""
    s = s.lower().strip()
    s = re.sub(r"\s+", " ", s)
    return s

def texts_similar(a: str, b: str, threshold=0.90):
    """Return True if texts are almost the same (ignore small AI noise)."""
    a_norm = normalize_text(a)
    b_norm = normalize_text(b)
    if not a_norm and not b_norm:
        return True
    similarity = difflib.SequenceMatcher(None, a_norm, b_norm).ratio()
    return similarity >= threshold

def normalize_list(lst):
    if not lst:
        return []
    return sorted([normalize_text(x) for x in lst if x and str(x).strip() != ""])


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

    companies_watchlist = (
        Company.query.filter(Company.company_id.in_(watchlist_ids)).all()
        if watchlist_ids else []
    )

    all_companies = Company.query.all()

    # ----------------------------------------------------
    # CHANGE EVENTS → MAX 3 + MEER-LINK
    # ----------------------------------------------------
    recent_events_raw = ChangeEvent.query.order_by(
        ChangeEvent.detected_at.desc()
    ).limit(3).all()

    alerts = []
    for e in recent_events_raw:
        company = Company.query.get(e.company_id)
        alerts.append({
            "id": e.event_id,
            "company_id": e.company_id,
            "company": company.name if company else "Onbekend bedrijf",
            "type": e.event_type,
            "description": e.description,
            "time": e.detected_at
        })

    return render_template(
        'dashboard.html',
        user=user,
        scrape_result=scrape_result,
        watchlist=[c.name for c in companies_watchlist],
        alerts=alerts,
        metric_options=METRIC_OPTIONS,
        metrics_selected=metrics_selected,
        companies=all_companies,
        more_alerts_count=max(0, ChangeEvent.query.count() - 3)
    )
  

# =====================================================
# COMPANY DETAIL
# =====================================================

@bp.route('/company/<int:company_id>')
def company_detail(company_id):
    if 'user_id' not in session:
        return redirect(url_for('main.login'))

    company = Company.query.get_or_404(company_id)

    # Alle wijzigingen voor dit bedrijf (nieuw → oud)
    events = ChangeEvent.query.filter_by(company_id=company_id)\
        .order_by(ChangeEvent.detected_at.desc())\
        .all()

    return render_template('company_detail.html', company=company, events=events)

@bp.route('/company/<int:company_id>/alerts')
def company_alerts(company_id):
    if 'user_id' not in session:
        return redirect(url_for('main.login'))

    company = Company.query.get_or_404(company_id)

    events = ChangeEvent.query.filter_by(company_id=company_id) \
        .order_by(ChangeEvent.detected_at.desc()) \
        .all()

    return render_template(
        'all_alerts.html',
        company=company,
        events=events
    )


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
# EXPORT WATCHLIST AUDIT (CSV / JSON)
# =====================================================

@bp.route('/export-watchlist-audit')
def export_watchlist_audit():
    if 'user_id' not in session:
        return redirect(url_for('main.login'))

    fmt = request.args.get("format", "csv").lower()

    ids = session.get('watchlist_companies', [])
    if not ids:
        return "Geen bedrijven in watchlist.", 400

    ids = [int(cid) for cid in ids]

    logs = (
        AuditLog.query
        .filter(AuditLog.company_id.in_(ids))
        .order_by(AuditLog.retrieved_at.desc())
        .all()
    )

    # ---------------------- JSON EXPORT ----------------------
    if fmt == "json":
        out = []
        for log in logs:
            company = Company.query.get(log.company_id)
            out.append({
                "company": company.name if company else "Onbekend",
                "source_name": log.source_name,
                "source_url": log.source_url,
                "retrieved_at": log.retrieved_at.isoformat() if log.retrieved_at else None
            })
        return jsonify(out)

    # ---------------------- CSV EXPORT ----------------------
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Company", "Source Name", "Source URL", "Retrieved At"])

    for log in logs:
        company = Company.query.get(log.company_id)
        writer.writerow([
            company.name if company else "Onbekend",
            log.source_name,
            log.source_url,
            log.retrieved_at
        ])

    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=audit_export.csv"}
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
# EXPORT: One-click company profile (VC analyst)
# =====================================================

@bp.route('/company/<int:company_id>/export')
def export_company(company_id):
    if 'user_id' not in session:
        return redirect(url_for('main.login'))

    c = Company.query.get_or_404(company_id)
    format = request.args.get("format", "json").lower()

    profile = {
        "company_name": c.name,
        "website": c.website_url,
        "headquarters": c.headquarters,
        "office_locations": c.office_locations,
        "team_size": c.team_size,
        "funding": c.funding,
        "funding_history": c.funding_history,
        "value_proposition": c.value_proposition,
        "product_description": c.product_description,
        "target_segment": c.target_segment,
        "pricing": c.pricing,
        "key_features": c.key_features,
        "competitors": c.competitors,
        "traction_signals": c.traction_signals,
        "ai_summary": c.ai_summary,
        "created_at": c.created_at
    }

    # JSON export
    if format == "json":
        return jsonify(profile)

    # CSV export (flat)
    if format == "csv":
        import csv, io
        output = io.StringIO()
        writer = csv.writer(output)
        for k, v in profile.items():
            writer.writerow([k, v])
        output.seek(0)
        return Response(
            output.getvalue(),
            mimetype="text/csv",
            headers={"Content-Disposition": f"attachment; filename={c.name}_profile.csv"}
        )

    # Plain-text due-diligence memo
    if format == "txt":
        memo = []
        memo.append(f"=== DUE DILIGENCE PROFILE: {c.name} ===\n")
        memo.append(f"Website: {c.website_url}\n")
        memo.append(f"HQ: {c.headquarters}\n")
        memo.append(f"Office locations: {c.office_locations}\n")
        memo.append(f"Team size: {c.team_size}\n")
        memo.append(f"Funding: {c.funding}\n")
        memo.append(f"Funding history: {c.funding_history}\n")
        memo.append("\n--- PRODUCT & MARKET ---\n")
        memo.append(f"Value proposition: {c.value_proposition}\n")
        memo.append(f"Product description: {c.product_description}\n")
        memo.append(f"Target segment: {c.target_segment}\n")
        memo.append(f"Pricing: {c.pricing}\n")
        memo.append("\nKey Features:\n")
        memo.extend([f" - {k}" for k in (c.key_features or [])])
        memo.append("\nCompetitors:\n")
        memo.extend([f" - {k}" for k in (c.competitors or [])])
        memo.append("\nTraction signals:\n")
        memo.append(c.traction_signals or "Geen signalen")
        memo.append("\nAI summary:\n")
        memo.append(c.ai_summary or "")

        return Response(
            "\n".join(memo),
            mimetype="text/plain",
            headers={"Content-Disposition": f"attachment; filename={c.name}_memo.txt"}
        )

    return "Unsupported format", 400


# =====================================================
# SCRAPE PAGE (AI + AUTO SAVE + CHANGE DETECTION)
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

    # --- SCRAPEN ---
    result = scrape_website(url)
    if result.get("error"):
        return render_template('scrape.html', result=result)

    # --- CHECK OF BEDRIJF BESTAAT ---
    existing = Company.query.filter_by(website_url=url).first()

    # ============================================
    # UPDATE BESTAAND BEDRIJF
    # ============================================
    if existing:

        # ----------------------------------------
        # 1) STRATEGIC MOVE DETECTION
        # ----------------------------------------
        change_events = []

        # ===== FEATURES =====
        old_features = normalize_list(existing.key_features)
        new_features = normalize_list(result.get("key_features"))

        added_features = [f for f in new_features if f not in old_features]
        removed_features = [f for f in old_features if f not in new_features]

        for f in added_features:
            change_events.append({
                "event_type": "new_feature",
                "description": f"Nieuwe feature toegevoegd: {f}"
            })

        for f in removed_features:
            change_events.append({
                "event_type": "removed_feature",
                "description": f"Feature verwijderd: {f}"
            })

        # ===== PRICING =====
        old_price = existing.pricing or ""
        new_price = result.get("pricing") or ""

        if not texts_similar(old_price, new_price):
            if old_price and new_price:
                change_events.append({
                    "event_type": "pricing_change",
                    "description": f"Pricing gewijzigd van '{old_price}' → '{new_price}'"
                })
            elif new_price:
                change_events.append({
                    "event_type": "pricing_added",
                    "description": f"Pricing toegevoegd: {new_price}"
                })
            elif old_price:
                change_events.append({
                    "event_type": "pricing_removed",
                    "description": "Pricing verwijderd"
                })

        # ===== PRODUCT DESCRIPTION =====
        old_product = existing.product_description or ""
        new_product = result.get("product_description") or ""

        if not texts_similar(old_product, new_product):
            change_events.append({
                "event_type": "product_change",
                "description": "Productbeschrijving gewijzigd (mogelijke nieuwe productlijn)"
            })

        # ===== TARGET SEGMENT =====
        old_segment = existing.target_segment or ""
        new_segment = result.get("target_segment") or ""

        if not texts_similar(old_segment, new_segment):
            change_events.append({
                "event_type": "segment_change",
                "description": "Target segment gewijzigd"
            })

        # Sla alle echte wijzigingen op
        for ev in change_events:
            db.session.add(ChangeEvent(
                company_id=existing.company_id,
                event_type=ev["event_type"],
                description=ev["description"]
            ))


        # ----------------------------------------
        # 2) UPDATE BEDRIJFSGEGEVENS
        # ----------------------------------------
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

    # ============================================
    # NIEUW BEDRIJF
    # ============================================
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
# GLOBAL AUDIT LOG OVERVIEW (Compliance)
# =====================================================

@bp.route('/audit-logs')
def audit_logs():
    if 'user_id' not in session:
        return redirect(url_for('main.login'))

    logs = AuditLog.query.order_by(AuditLog.retrieved_at.desc()).all()

    enriched_logs = []
    for log in logs:
        company = Company.query.get(log.company_id)
        enriched_logs.append({
            "company": company.name if company else "Onbekend",
            "company_id": log.company_id,
            "source_name": log.source_name,
            "source_url": log.source_url,
            "retrieved_at": log.retrieved_at
        })

    return render_template("audit_logs.html", logs=enriched_logs)

@bp.route('/audit-logs/export')
def export_all_audit_logs():
    if "user_id" not in session:
        return redirect(url_for("main.login"))

    fmt = request.args.get("format", "csv").lower()

    logs = AuditLog.query.order_by(AuditLog.retrieved_at.desc()).all()

    # JSON export
    if fmt == "json":
        out = []
        for log in logs:
            company = Company.query.get(log.company_id)
            out.append({
                "company": company.name if company else "Onbekend",
                "source_name": log.source_name,
                "source_url": log.source_url,
                "retrieved_at": log.retrieved_at.isoformat() if log.retrieved_at else None
            })
        return jsonify(out)

    # CSV export
    import csv, io
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Company", "Source Name", "Source URL", "Retrieved At"])

    for log in logs:
        company = Company.query.get(log.company_id)
        writer.writerow([
            company.name if company else "Onbekend",
            log.source_name,
            log.source_url,
            log.retrieved_at
        ])

    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=all_audit_logs.csv"}
    )


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

# =====================================================
# ALL ALERTS PAGE
# =====================================================

@bp.route("/all-alerts")
def all_alerts():
    if "user_id" not in session:
        return redirect(url_for("main.login"))

    # Haal ALLE events op (niet limiteren!)
    events = ChangeEvent.query.order_by(
        ChangeEvent.detected_at.desc()
    ).all()

    alerts = []
    for e in events:
        company = Company.query.get(e.company_id)
        alerts.append({
            "company_id": e.company_id,
            "company": company.name if company else "Onbekend bedrijf",
            "type": e.event_type,
            "description": e.description,
            "time": e.detected_at
        })

    return render_template(
        "all_alerts.html",
        alerts=alerts,
        company=None   # omdat dit GEEN bedrijf-specifiek overzicht is
    )


