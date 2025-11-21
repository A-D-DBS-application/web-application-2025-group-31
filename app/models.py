from app import db

# ======================================
# TABLE: Company
# ======================================
class Company(db.Model):
    __tablename__ = 'company'

    company_id = db.Column(db.BigInteger, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    website_url = db.Column(db.Text)
    headquarters = db.Column(db.Text)
    team_size = db.Column(db.Integer)
    funding = db.Column(db.Numeric)
    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())

    # Relaties
    metrics = db.relationship('Metric', back_populates='company', cascade="all, delete")
    reports = db.relationship('Report', back_populates='company', cascade="all, delete")
    audit_logs = db.relationship('AuditLog', back_populates='company', cascade="all, delete")
    change_events = db.relationship('ChangeEvent', back_populates='company', cascade="all, delete")

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

    # 🔥 Enige toegevoegde regel voor database-auth:
    password_hash = db.Column(db.Text, nullable=False)

    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())

    reports = db.relationship('Report', back_populates='user')

    def __repr__(self):
        return f"<AppUser {self.username}>"


# ======================================
# TABLE: Metric
# ======================================
class Metric(db.Model):
    __tablename__ = 'metric'

    metric_id = db.Column(db.BigInteger, primary_key=True)
    company_id = db.Column(db.BigInteger, db.ForeignKey('company.company_id', ondelete="CASCADE"))
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
# TABLE: Report
# ======================================
class Report(db.Model):
    __tablename__ = 'report'

    report_id = db.Column(db.BigInteger, primary_key=True)
    generated_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    summary = db.Column(db.Text)
    user_id = db.Column(db.BigInteger, db.ForeignKey('app_user.user_id', ondelete="SET NULL"))
    company_id = db.Column(db.BigInteger, db.ForeignKey('company.company_id', ondelete="CASCADE"))

    user = db.relationship('AppUser', back_populates='reports')
    company = db.relationship('Company', back_populates='reports')

    def __repr__(self):
        return f"<Report {self.report_id} - Company {self.company_id}>"


# ======================================
# TABLE: AuditLog
# ======================================
class AuditLog(db.Model):
    __tablename__ = 'audit_log'

    log_id = db.Column(db.BigInteger, primary_key=True)
    source_name = db.Column(db.Text)
    source_url = db.Column(db.Text)
    retrieved_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    company_id = db.Column(db.BigInteger, db.ForeignKey('company.company_id', ondelete="CASCADE"))

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
    company_id = db.Column(db.BigInteger, db.ForeignKey('company.company_id', ondelete="CASCADE"))

    company = db.relationship('Company', back_populates='change_events')

    def __repr__(self):
        return f"<ChangeEvent {self.event_type}>"







    