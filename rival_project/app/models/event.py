from datetime import datetime
from app.extensions import db

class Event(db.Model):
    __tablename__ = 'events'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    location = db.Column(db.String(200), nullable=True)

    def __repr__(self):
        return f'<Event {self.name}>'