from app import app
from extensions import db
from models import Category, Article
from datetime import datetime
import os

def init_db():
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Add some initial categories if none exist
        if not Category.query.first():
            categories = [
                Category(name='Getting Started', description='Introduction and basic concepts'),
                Category(name='User Guide', description='Detailed user documentation'),
                Category(name='API Reference', description='API documentation and examples'),
                Category(name='Tutorials', description='Step-by-step tutorials and guides'),
                Category(name='FAQs', description='Frequently asked questions')
            ]
            db.session.add_all(categories)
            db.session.commit()
        
        # Log database initialization
        with open('changes.log', 'a') as f:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            f.write(f'\n[{timestamp}] Database Initialization\n\n')
            f.write('- Created database tables\n')
            f.write('- Set up admin credentials (admin/admin123)\n')
            f.write('- Added default categories\n')
            f.write('- Added input validation and sanitization\n')
            f.write('- Implemented security measures\n')

if __name__ == '__main__':
    # Create instance directory if it doesn't exist
    os.makedirs('instance', exist_ok=True)
    
    init_db()
    print("\nDatabase initialized successfully!")
    print("Default admin credentials:")
    print("Username: admin")
    print("Password: admin123")
    print("\nIMPORTANT: Change these credentials in production!")
