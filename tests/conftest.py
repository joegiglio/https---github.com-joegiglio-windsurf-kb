import pytest
import os
import tempfile
import time
import logging
from werkzeug.security import generate_password_hash

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@pytest.fixture(scope='session')
def app():
    """Create and configure a new app instance for each test."""
    from app import app  # Import the actual app instance
    
    # Create a temporary file to use as the test database
    db_fd, db_path = tempfile.mkstemp()
    logger.info(f'Created temporary database at {db_path}')
    
    # Generate a real password hash for 'admin123'
    password_hash = generate_password_hash('admin123')
    
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': f'sqlite:///{db_path}',
        'WTF_CSRF_ENABLED': False,
        'ADMIN_USERNAME': 'admin',
        'ADMIN_PASSWORD_HASH': password_hash,
        'SERVER_NAME': 'localhost:5000'  # Required for url_for to work
    })
    
    yield app
    
    # Clean up the temporary database
    os.close(db_fd)
    os.unlink(db_path)
    logger.info('Cleaned up temporary database')

@pytest.fixture
def client(app):
    """Create a test client for the app."""
    return app.test_client()

@pytest.fixture(autouse=True)
def setup_db(app):
    """Setup test database before each test"""
    with app.app_context():
        from extensions import db
        db.create_all()
        
        # Create a test category for tests that need it
        from models import Category, Article
        category = Category(name='Test Category', description='Test Description')
        db.session.add(category)
        
        # Create a test article for tests that need it
        article = Article(
            title='Test Article',
            content='Test Content',
            category_id=1
        )
        db.session.add(article)
        
        db.session.commit()
        logger.info('Test database initialized with sample data')
        
        yield
        
        db.drop_all()
        logger.info('Test database cleaned up')
