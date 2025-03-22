from flask import Flask, render_template, request, jsonify
from werkzeug.security import generate_password_hash
import os
import bleach
from extensions import db
from models import Category, Article, SearchLog
from datetime import datetime
from flask_migrate import Migrate

def create_app():
    app = Flask(__name__)

    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here')  # Change in production
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///kb.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['TEMPLATES_AUTO_RELOAD'] = True

    # Set up admin credentials (in production, these should come from environment variables)
    app.config['ADMIN_USERNAME'] = 'admin'
    app.config['ADMIN_PASSWORD_HASH'] = generate_password_hash('admin123')

    # Initialize extensions
    db.init_app(app)
    migrate = Migrate(app, db)  # Initialize Flask-Migrate

    # Import and register blueprints
    from admin import admin
    app.register_blueprint(admin)

    # Create database tables
    with app.app_context():
        db.create_all()  # Only create tables if they don't exist
        
        # Add sample data if database is empty
        if Category.query.count() == 0:
            categories = [
                Category(name='General'),
                Category(name='Technology'),
                Category(name='Business')
            ]
            db.session.add_all(categories)
            db.session.commit()
            
            articles = [
                Article(
                    title='Welcome to Knowledge Base',
                    content='Welcome to our knowledge base system. Here you will find helpful articles and guides.',
                    category_id=1
                ),
                Article(
                    title='Getting Started with Technology',
                    content='Learn about the latest technology trends and how to stay up to date.',
                    category_id=2
                ),
                Article(
                    title='Business Best Practices',
                    content='Discover the best practices for running a successful business.',
                    category_id=3
                )
            ]
            db.session.add_all(articles)
            db.session.commit()

    # Define routes
    @app.route('/')
    def index():
        # Get categories ordered by the order field
        categories = Category.query.order_by(Category.order).all()
        recent_articles = Article.query.order_by(Article.created_at.desc()).limit(5).all()
        return render_template('index.html', categories=categories, recent_articles=recent_articles)

    @app.route('/category/<int:category_id>')
    def category(category_id):
        category = Category.query.get_or_404(category_id)
        return render_template('category.html', category=category)

    @app.route('/article/<int:article_id>')
    def article(article_id):
        article = Article.query.get_or_404(article_id)
        article.increment_views()
        return render_template('article.html', article=article)

    @app.route('/article/<int:article_id>/rate', methods=['POST'])
    def rate_article(article_id):
        print(f"Received rating request for article {article_id}")
        article = Article.query.get_or_404(article_id)
        data = request.get_json()
        print(f"Request data: {data}")
        
        if not isinstance(data, dict) or 'vote' not in data:
            print("Invalid request: missing vote data")
            return jsonify({'error': 'Invalid request'}), 400
            
        vote = data['vote']
        if vote not in ['up', 'down']:
            print(f"Invalid vote type: {vote}")
            return jsonify({'error': 'Invalid vote type'}), 400
            
        if vote == 'up':
            article.upvotes = (article.upvotes or 0) + 1
            print(f"Incrementing upvotes to {article.upvotes}")
        else:
            article.downvotes = (article.downvotes or 0) + 1
            print(f"Incrementing downvotes to {article.downvotes}")
            
        try:
            db.session.commit()
            print("Successfully saved vote to database")
        except Exception as e:
            print(f"Error saving vote: {str(e)}")
            db.session.rollback()
            return jsonify({'error': 'Database error'}), 500
        
        response_data = {
            'upvotes': article.upvotes,
            'downvotes': article.downvotes,
            'rating_percentage': article.get_rating_percentage()
        }
        print(f"Sending response: {response_data}")
        return jsonify(response_data)

    @app.route('/search')
    def search():
        query = request.args.get('q', '')
        should_log = request.args.get('log', 'false').lower() == 'true'
        
        if not query or len(query) > 100:  # Limit query length for security
            return jsonify([])
        
        # Sanitize input
        sanitized_query = bleach.clean(query, tags=[], strip=True)
        
        # Search in both title and content
        articles = Article.query.filter(
            Article.title.ilike(f'%{sanitized_query}%') |
            Article.content.ilike(f'%{sanitized_query}%')
        ).limit(10).all()
        
        # Only log completed searches (when form is submitted)
        if should_log:
            search_log = SearchLog(
                term=sanitized_query[:100],  # Ensure max length
                results_count=len(articles),
                ip_address=request.remote_addr
            )
            db.session.add(search_log)
            db.session.commit()
        
        return jsonify([article.to_dict() for article in articles])

    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, extra_files=[
        os.path.join(app.root_path, 'templates', '**', '*.html'),
        os.path.join(app.root_path, 'static', 'css', '*.css'),
        os.path.join(app.root_path, 'static', 'js', '*.js')
    ])
