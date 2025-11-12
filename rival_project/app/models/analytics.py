from app.extensions import db


class AppUser(db.Model):
    __tablename__ = 'app_user'

    user_id = db.Column(db.BigInteger, primary_key=True)
    username = db.Column(db.Text, nullable=False, unique=True)
    email = db.Column(db.Text, nullable=False, unique=True)
    role = db.Column(db.Text, db.CheckConstraint("role IN ('admin', 'analyst', 'viewer')"))
    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())

    reports = db.relationship('Report', back_populates='user')

    def __repr__(self):
        return f"<AppUser {self.username}>"


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

    company = db.relationship('Company')

    def __repr__(self):
        return f"<Metric {self.name} ({self.company_id})>"


class Report(db.Model):
    __tablename__ = 'report'

    report_id = db.Column(db.BigInteger, primary_key=True)
    generated_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    summary = db.Column(db.Text)
    user_id = db.Column(db.BigInteger, db.ForeignKey('app_user.user_id', ondelete="SET NULL"))
    company_id = db.Column(db.BigInteger, db.ForeignKey('company.company_id', ondelete="CASCADE"))

    user = db.relationship('AppUser', back_populates='reports')
    company = db.relationship('Company')

    def __repr__(self):
        return f"<Report {self.report_id} - Company {self.company_id}>"


class AuditLog(db.Model):
    __tablename__ = 'audit_log'

    log_id = db.Column(db.BigInteger, primary_key=True)
    source_name = db.Column(db.Text)
    source_url = db.Column(db.Text)
    retrieved_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    company_id = db.Column(db.BigInteger, db.ForeignKey('company.company_id', ondelete="CASCADE"))

    company = db.relationship('Company')

    def __repr__(self):
        return f"<AuditLog {self.source_name}>"


class ChangeEvent(db.Model):
    __tablename__ = 'change_event'

    event_id = db.Column(db.BigInteger, primary_key=True)
    event_type = db.Column(db.Text)
    description = db.Column(db.Text)
    detected_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    company_id = db.Column(db.BigInteger, db.ForeignKey('company.company_id', ondelete="CASCADE"))

    company = db.relationship('Company')

    def __repr__(self):
        return f"<ChangeEvent {self.event_type}>"
