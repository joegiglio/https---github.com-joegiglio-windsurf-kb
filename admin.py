from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify, current_app
from werkzeug.security import check_password_hash
import bleach
import re
from datetime import datetime
from extensions import db
from models import Category, Article

admin = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin' not in session:
            flash('Please log in first.', 'warning')
            return redirect(url_for('admin.login'))
        return f(*args, **kwargs)
    return decorated_function

def sanitize_input(text, max_length=None):
    """Sanitize user input by removing HTML tags and limiting length"""
    if not text:
        return ""
    
    # Remove HTML tags
    clean_text = bleach.clean(text, tags=[], strip=True)
    
    # Limit length if specified
    if max_length and len(clean_text) > max_length:
        clean_text = clean_text[:max_length]
    
    return clean_text

def validate_category_name(name):
    """Validate category name format"""
    if not name or not isinstance(name, str):
        return False
    
    # Check length (1-100 characters)
    if len(name) < 1 or len(name) > 100:
        return False
    
    # Only allow letters, numbers, spaces, hyphens, and underscores
    if not re.match(r'^[A-Za-z0-9\s\-_]+$', name):
        return False
    
    return True

@admin.route('/')
@admin_required
def index():
    categories = Category.query.all()
    articles = Article.query.all()
    recent_articles = Article.query.order_by(Article.created_at.desc()).limit(5).all()
    
    # In a real application, these would come from a proper analytics system
    total_views = 0
    total_searches = 0
    popular_searches = []
    
    for article in articles:
        total_views += getattr(article, 'views', 0)
    
    return render_template('admin/index.html',
                         categories=categories,
                         articles=articles,
                         recent_articles=recent_articles,
                         total_views=total_views,
                         total_searches=total_searches,
                         popular_searches=popular_searches)

@admin.route('/dashboard-data')
@admin_required
def dashboard_data():
    """AJAX endpoint for dashboard data"""
    categories = Category.query.all()
    articles = Article.query.all()
    recent_articles = Article.query.order_by(Article.created_at.desc()).limit(5).all()
    
    # In a real application, these would come from a proper analytics system
    total_views = sum(getattr(article, 'views', 0) for article in articles)
    total_searches = 0
    
    return jsonify({
        'categories_count': len(categories),
        'articles_count': len(articles),
        'total_views': total_views,
        'total_searches': total_searches,
        'recent_articles': [{
            'id': article.id,
            'title': article.title,
            'category_name': article.category.name,
            'created_at': article.created_at.strftime('%Y-%m-%d')
        } for article in recent_articles],
        'popular_searches': []  # Would be populated from analytics in a real application
    })

@admin.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = sanitize_input(request.form.get('username', ''), max_length=50)
        password = request.form.get('password', '')
        
        # Validate username format
        if not username or not re.match(r'^[A-Za-z0-9\-_]+$', username):
            flash('Invalid username format.', 'danger')
            return redirect(url_for('admin.login'))
        
        # Get admin credentials from app config
        admin_username = current_app.config.get('ADMIN_USERNAME')
        admin_password_hash = current_app.config.get('ADMIN_PASSWORD_HASH')
        
        if username == admin_username and check_password_hash(admin_password_hash, password):
            session['admin'] = True
            flash('Welcome back!', 'success')
            return redirect(url_for('admin.index'))
        
        flash('Invalid credentials.', 'danger')
    return render_template('admin/login.html')

@admin.route('/logout')
def logout():
    session.pop('admin', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('admin.login'))

@admin.route('/categories')
@admin_required
def categories():
    categories = Category.query.all()
    return render_template('admin/categories.html', categories=categories)

@admin.route('/categories/add', methods=['POST'])
@admin_required
def add_category():
    name = request.form.get('name', '').strip()
    description = request.form.get('description', '').strip()
    
    # Validate and sanitize input
    if not validate_category_name(name):
        flash('Invalid category name. Use only letters, numbers, spaces, hyphens, and underscores.', 'danger')
        return redirect(url_for('admin.categories'))
    
    name = sanitize_input(name, max_length=100)
    description = sanitize_input(description, max_length=500)
    
    # Check if category already exists
    if Category.query.filter_by(name=name).first():
        flash('A category with this name already exists.', 'danger')
        return redirect(url_for('admin.categories'))
    
    try:
        category = Category(name=name, description=description)
        db.session.add(category)
        db.session.commit()
        flash('Category added successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('An error occurred while adding the category.', 'danger')
    
    return redirect(url_for('admin.categories'))

@admin.route('/categories/<int:category_id>/edit', methods=['POST'])
@admin_required
def edit_category(category_id):
    category = Category.query.get_or_404(category_id)
    name = request.form.get('name', '').strip()
    description = request.form.get('description', '').strip()
    
    # Validate and sanitize input
    if not validate_category_name(name):
        flash('Invalid category name. Use only letters, numbers, spaces, hyphens, and underscores.', 'danger')
        return redirect(url_for('admin.categories'))
    
    name = sanitize_input(name, max_length=100)
    description = sanitize_input(description, max_length=500)
    
    # Check if new name conflicts with existing category
    existing = Category.query.filter_by(name=name).first()
    if existing and existing.id != category_id:
        flash('A category with this name already exists.', 'danger')
        return redirect(url_for('admin.categories'))
    
    try:
        category.name = name
        category.description = description
        category.updated_at = datetime.utcnow()
        db.session.commit()
        flash('Category updated successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('An error occurred while updating the category.', 'danger')
    
    return redirect(url_for('admin.categories'))

@admin.route('/categories/<int:category_id>/delete', methods=['POST'])
@admin_required
def delete_category(category_id):
    category = Category.query.get_or_404(category_id)
    
    try:
        # Check if category has articles
        if category.articles:
            flash('Cannot delete category with existing articles.', 'danger')
            return redirect(url_for('admin.categories'))
        
        db.session.delete(category)
        db.session.commit()
        flash('Category deleted successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('An error occurred while deleting the category.', 'danger')
    
    return redirect(url_for('admin.categories'))

@admin.route('/articles')
@admin_required
def articles():
    # This will be implemented in the next phase
    return "Article management coming soon!"
