from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
from werkzeug.security import generate_password_hash, check_password_hash
import bleach

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///kb.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['TEMPLATES_AUTO_RELOAD'] = True

# Ensure the instance folder exists
os.makedirs(app.instance_path, exist_ok=True)

db = SQLAlchemy(app)

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500))
    articles = db.relationship('Article', backref='category', lazy=True)

class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'title': bleach.clean(self.title),
            'content': bleach.clean(self.content),
            'category_id': self.category_id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

@app.route('/')
def index():
    categories = Category.query.all()
    recent_articles = Article.query.order_by(Article.created_at.desc()).limit(5).all()
    return render_template('index.html', categories=categories, recent_articles=recent_articles)

@app.route('/category/<int:category_id>')
def category(category_id):
    category = Category.query.get_or_404(category_id)
    return render_template('category.html', category=category)

@app.route('/article/<int:article_id>')
def article(article_id):
    article = Article.query.get_or_404(article_id)
    return render_template('article.html', article=article)

@app.route('/search')
def search():
    query = request.args.get('q', '')
    if not query or len(query) > 100:  # Limit query length for security
        return jsonify([])
    
    sanitized_query = bleach.clean(query)
    articles = Article.query.filter(
        Article.title.ilike(f'%{sanitized_query}%') |
        Article.content.ilike(f'%{sanitized_query}%')
    ).limit(10).all()
    
    return jsonify([article.to_dict() for article in articles])

def init_db():
    with app.app_context():
        db.create_all()
        
        # Add some initial categories if none exist
        if not Category.query.first():
            categories = [
                Category(name='Getting Started', description='Basic guides and tutorials'),
                Category(name='Features', description='Detailed feature documentation'),
                Category(name='Troubleshooting', description='Common issues and solutions'),
                Category(name='API Reference', description='API documentation and examples'),
                Category(name='Best Practices', description='Guidelines and recommendations')
            ]
            db.session.add_all(categories)
            db.session.commit()

if __name__ == '__main__':
    init_db()
    app.run(debug=True, extra_files=[
        os.path.join(app.root_path, 'templates', '**', '*.html'),
        os.path.join(app.root_path, 'static', 'css', '*.css'),
        os.path.join(app.root_path, 'static', 'js', '*.js')
    ])
