from datetime import datetime
from app.extensions import db


class Company(db.Model):
    __tablename__ = 'company'

    # Map to existing 'company' table columns while keeping property names stable
    id = db.Column('company_id', db.BigInteger, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    # our property 'url' stores in legacy column 'website_url'
    url = db.Column('website_url', db.Text, nullable=True)
    # our property 'location' maps to 'headquarters'
    location = db.Column('headquarters', db.Text, nullable=True)
    # optional fields present in 'company' table
    team_size = db.Column(db.Integer, nullable=True)
    funding = db.Column(db.Numeric, nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())

    # Drop fields not present in 'company' table (industry, description) to avoid schema mismatches

    def __repr__(self):
        return f"<Company {self.name}>"