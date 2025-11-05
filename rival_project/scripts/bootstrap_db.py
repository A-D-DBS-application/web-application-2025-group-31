from app import create_app
from app.extensions import db

app = create_app()

def bootstrap_database():
    with app.app_context():
        db.create_all()
        print("Database initialized!")

if __name__ == "__main__":
    bootstrap_database()