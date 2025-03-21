from flask import Flask, render_template, request, jsonify
from werkzeug.security import generate_password_hash
import os
import bleach
from extensions import db
from models import Category, Article
from datetime import datetime

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

    # Import and register blueprints
    from admin import admin
    app.register_blueprint(admin)

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

    @app.route('/search')
    def search():
        query = request.args.get('q', '')
        if not query or len(query) > 100:  # Limit query length for security
            return jsonify([])
        
        # Sanitize input
        sanitized_query = bleach.clean(query, tags=[], strip=True)
        
        # Search in both title and content
        articles = Article.query.filter(
            Article.title.ilike(f'%{sanitized_query}%') |
            Article.content.ilike(f'%{sanitized_query}%')
        ).limit(10).all()
        
        return jsonify([article.to_dict() for article in articles])

    return app

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        
        # Add some initial categories if none exist
        if not Category.query.first():
            categories = [
                Category(name='Getting Started', description='Basic guides and tutorials', order=0),
                Category(name='Features', description='Detailed feature documentation', order=1),
                Category(name='Troubleshooting', description='Common issues and solutions', order=2),
                Category(name='API Reference', description='API documentation and examples', order=3),
                Category(name='Best Practices', description='Guidelines and recommendations', order=4)
            ]
            db.session.add_all(categories)
            db.session.commit()
            
            # Log the changes
            with open('changes.log', 'a') as f:
                f.write('\n[{}] Added category ordering\n'.format(
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                ))
                f.write('- Added order field to Category model\n')
                f.write('- Added drag-and-drop reordering in admin panel\n')
                f.write('- Updated category display to respect order\n')
                f.write('- Added responsive design for mobile and tablet\n')
    
    app.run(debug=True, extra_files=[
        os.path.join(app.root_path, 'templates', '**', '*.html'),
        os.path.join(app.root_path, 'static', 'css', '*.css'),
        os.path.join(app.root_path, 'static', 'js', '*.js')
    ])
