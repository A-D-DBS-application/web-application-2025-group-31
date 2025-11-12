from datetime import datetime, timedelta
from app.extensions import db


class CompanyFinance(db.Model):
    __tablename__ = 'company_finance'

    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.BigInteger, db.ForeignKey('company.company_id'), unique=True, nullable=False)
    ticker = db.Column(db.String(20), nullable=True)
    currency = db.Column(db.String(10), nullable=True)
    price = db.Column(db.Float, nullable=True)
    market_cap = db.Column(db.BigInteger, nullable=True)
    pe_ratio = db.Column(db.Float, nullable=True)
    revenue = db.Column(db.BigInteger, nullable=True)
    employees = db.Column(db.Integer, nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    company = db.relationship('Company', backref=db.backref('finance', uselist=False, cascade='all, delete-orphan'))

    @property
    def is_stale(self) -> bool:
        return not self.updated_at or (datetime.utcnow() - self.updated_at) > timedelta(hours=24)
