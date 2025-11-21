from flask import Blueprint, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from app.models import AppUser, Company
from app.scraper import scrape_website

bp = Blueprint('main', __name__)

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

    username = session.get('username')
    scrape_result = None

    if request.method == 'POST':
        url = request.form.get('scrape_url')

        if url:
            scrape_result = scrape_website(url)

            if scrape_result and not scrape_result.get('error'):
                existing_company = Company.query.filter_by(website_url=url).first()

                if not existing_company:
                    new_company = Company(
                        name=scrape_result['title'] or 'Onbekend bedrijf',
                        website_url=url,
                        headquarters='Onbekend'
                    )
                    db.session.add(new_company)
                    db.session.commit()

    return render_template('dashboard.html', scrape_result=scrape_result, watchlist=[], alerts=[])


# ============================
# COMPANIES
# ============================
@bp.route('/companies', methods=['GET', 'POST'])
def companies():
    if 'user_id' not in session:
        return redirect(url_for('main.login'))

    message = ""

    if request.method == 'POST':
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
            db.session.commit()
            message = f"✅ {name} toegevoegd!"
        except Exception as e:
            message = f"❌ Fout bij toevoegen: {e}"

    companies = Company.query.all()
    return render_template('companies.html', companies=companies, message=message)


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






























