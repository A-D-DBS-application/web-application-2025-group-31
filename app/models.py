from app import db

# ======================================
# TABLE: Company
# ======================================
class Company(db.Model):
    __tablename__ = 'company'

    company_id = db.Column(db.BigInteger, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    website_url = db.Column(db.Text)

    # Klassieke scrapingvelden
    headquarters = db.Column(db.Text)
    team_size = db.Column(db.Integer)
    funding = db.Column(db.Text)
    office_locations = db.Column(db.Text)
    traction_signals = db.Column(db.Text)
    funding_history = db.Column(db.Text)

    # AI-baseline velden
    ai_summary = db.Column(db.Text)
    value_proposition = db.Column(db.Text)
    product_description = db.Column(db.Text)
    target_segment = db.Column(db.Text)
    pricing = db.Column(db.Text)
    key_features = db.Column(db.JSON)   # JSONB in database
    competitors = db.Column(db.JSON)    # JSONB in database

    # Link naar de sectors tabel (FK → sectors.sector_id)
    sector_id = db.Column(
        db.Integer,
        db.ForeignKey('sectors.sector_id'),
        nullable=True
    )

    created_at = db.Column(
        db.DateTime(timezone=True),
        server_default=db.func.now()
    )

    # Relaties
    metrics = db.relationship('Metric', back_populates='company', cascade="all, delete")
    audit_logs = db.relationship('AuditLog', back_populates='company', cascade="all, delete")
    change_events = db.relationship('ChangeEvent', back_populates='company', cascade="all, delete")

    # Sector-relatie (inverse van Sector.companies)
    sector = db.relationship('Sector', back_populates='companies')

    def __repr__(self):
        return f"<Company {self.name}>"


# ======================================
# TABLE: AppUser
# ======================================
class AppUser(db.Model):
    __tablename__ = 'app_user'

    user_id = db.Column(db.BigInteger, primary_key=True)
    username = db.Column(db.Text, nullable=False, unique=True)
    email = db.Column(db.Text, nullable=False, unique=True)
    password_hash = db.Column(db.Text, nullable=False)

    weekly_digest = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    digest_frequency = db.Column(db.Text, default="weekly")
    digest_signals = db.Column(db.JSON, default=list)

    def __repr__(self):
        return f"<AppUser {self.username}>"


# ======================================
# TABLE: Metric
# ======================================
class Metric(db.Model):
    __tablename__ = 'metric'

    metric_id = db.Column(db.BigInteger, primary_key=True)
    company_id = db.Column(
        db.BigInteger,
        db.ForeignKey('company.company_id', ondelete="CASCADE")
    )

    name = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text)
    tracking_frequency = db.Column(db.Text)
    value = db.Column(db.Numeric)
    active = db.Column(db.Boolean, default=True)
    last_updated = db.Column(db.DateTime(timezone=True), server_default=db.func.now())

    company = db.relationship('Company', back_populates='metrics')

    def __repr__(self):
        return f"<Metric {self.name} ({self.company_id})>"


# ======================================
# TABLE: AuditLog
# ======================================
class AuditLog(db.Model):
    __tablename__ = 'audit_log'

    log_id = db.Column(db.BigInteger, primary_key=True)
    source_name = db.Column(db.Text)
    source_url = db.Column(db.Text)
    retrieved_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())

    company_id = db.Column(
        db.BigInteger,
        db.ForeignKey('company.company_id', ondelete="CASCADE")
    )
    company = db.relationship('Company', back_populates='audit_logs')

    def __repr__(self):
        return f"<AuditLog {self.source_name}>"


# ======================================
# TABLE: ChangeEvent
# ======================================
class ChangeEvent(db.Model):
    __tablename__ = 'change_event'

    event_id = db.Column(db.BigInteger, primary_key=True)
    event_type = db.Column(db.Text)
    description = db.Column(db.Text)
    detected_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())

    company_id = db.Column(
        db.BigInteger,
        db.ForeignKey('company.company_id', ondelete="CASCADE")
    )
    company = db.relationship('Company', back_populates='change_events')

    def __repr__(self):
        return f"<ChangeEvent {self.event_type}>"


# ======================================
# TABLE: MetricHistory
# ======================================
class MetricHistory(db.Model):
    __tablename__ = 'metric_history'

    id = db.Column(db.BigInteger, primary_key=True)

    company_id = db.Column(
        db.BigInteger,
        db.ForeignKey('company.company_id', ondelete="CASCADE"),
        nullable=False
    )

    name = db.Column(db.Text, nullable=False)
    value = db.Column(db.Numeric)

    recorded_at = db.Column(
        db.DateTime(timezone=True),
        server_default=db.func.now(),
        index=True
    )

    # "snapshot" (live scrape) of "inferred" (AI backfill)
    source = db.Column(db.Text, default="snapshot")

    company = db.relationship(
        'Company',
        backref=db.backref('metric_history', cascade="all, delete", lazy=True)
    )

    def __repr__(self):
        return f"<MetricHistory {self.name} ({self.company_id}) [{self.source}]>"


# ======================================
# TABLE: Sector
# ======================================
class Sector(db.Model):
    __tablename__ = 'sectors'

    # ⬅️ Primaire sleutel (belangrijk voor SQLAlchemy)
    sector_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)

    # Inverse relatie naar Company.sector
    companies = db.relationship('Company', back_populates='sector', lazy=True)

    def __repr__(self):
        return f"<Sector {self.name}>"
