from app import db
from app.models.company import Company
from app.models.user import User

def load_sample_data():
    # Create sample companies
    company1 = Company(name='Company A', description='Description for Company A')
    company2 = Company(name='Company B', description='Description for Company B')
    
    # Create sample users
    user1 = User(username='user1', email='user1@example.com')
    user2 = User(username='user2', email='user2@example.com')
    
    # Add to session
    db.session.add(company1)
    db.session.add(company2)
    db.session.add(user1)
    db.session.add(user2)
    
    # Commit the session
    db.session.commit()
    print("Sample data loaded successfully.")

if __name__ == '__main__':
    load_sample_data()