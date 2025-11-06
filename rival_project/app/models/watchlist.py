from app.extensions import db


class Watchlist(db.Model):
    __tablename__ = 'watchlist'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)

    user = db.relationship('User', backref=db.backref('watchlist_items', cascade='all, delete-orphan'))
    company = db.relationship('Company')

    __table_args__ = (db.UniqueConstraint('user_id', 'company_id', name='uq_user_company'),)