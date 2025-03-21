from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify, current_app
from functools import wraps
from werkzeug.security import check_password_hash
from models import Category, Article
from extensions import db
import bleach

admin = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin' not in session:
            return redirect(url_for('admin.login'))
        return f(*args, **kwargs)
    return decorated_function

@admin.route('/')
@admin_required
def index():
    total_categories = Category.query.count()
    total_articles = Article.query.count()
    recent_articles = Article.query.order_by(Article.created_at.desc()).limit(5).all()
    return render_template('admin/index.html', 
                         total_categories=total_categories,
                         total_articles=total_articles,
                         recent_articles=recent_articles)

@admin.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            flash('Please provide both username and password', 'danger')
            return redirect(url_for('admin.login'))
            
        if (username == current_app.config['ADMIN_USERNAME'] and 
            check_password_hash(current_app.config['ADMIN_PASSWORD_HASH'], password)):
            session['admin'] = True
            return redirect(url_for('admin.index'))
        else:
            flash('Invalid credentials', 'danger')
            
    return render_template('admin/login.html')

@admin.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect(url_for('admin.login'))

@admin.route('/categories')
@admin_required
def categories():
    categories = Category.query.order_by(Category.order).all()
    return render_template('admin/categories.html', categories=categories)

@admin.route('/categories/add', methods=['POST'])
@admin_required
def add_category():
    name = request.form.get('name', '').strip()
    description = request.form.get('description', '').strip()
    
    if not name:
        flash('Category name is required', 'danger')
        return redirect(url_for('admin.categories'))
        
    if len(name) > 100:
        flash('Category name must be less than 100 characters', 'danger')
        return redirect(url_for('admin.categories'))
        
    if len(description) > 500:
        flash('Description must be less than 500 characters', 'danger')
        return redirect(url_for('admin.categories'))
    
    # Sanitize input
    name = bleach.clean(name, tags=[], strip=True)
    description = bleach.clean(description, tags=[], strip=True)
    
    # Get the highest order value
    max_order = db.session.query(db.func.max(Category.order)).scalar() or -1
    
    category = Category(name=name, description=description, order=max_order + 1)
    db.session.add(category)
    
    try:
        db.session.commit()
        flash('Category added successfully', 'success')
    except:
        db.session.rollback()
        flash('An error occurred while adding the category', 'danger')
    
    return redirect(url_for('admin.categories'))

@admin.route('/categories/<int:id>/edit', methods=['POST'])
@admin_required
def edit_category(id):
    category = Category.query.get_or_404(id)
    name = request.form.get('name', '').strip()
    description = request.form.get('description', '').strip()
    
    if not name:
        flash('Category name is required', 'danger')
        return redirect(url_for('admin.categories'))
        
    if len(name) > 100:
        flash('Category name must be less than 100 characters', 'danger')
        return redirect(url_for('admin.categories'))
        
    if len(description) > 500:
        flash('Description must be less than 500 characters', 'danger')
        return redirect(url_for('admin.categories'))
    
    # Sanitize input
    name = bleach.clean(name, tags=[], strip=True)
    description = bleach.clean(description, tags=[], strip=True)
    
    category.name = name
    category.description = description
    
    try:
        db.session.commit()
        flash('Category updated successfully', 'success')
    except:
        db.session.rollback()
        flash('An error occurred while updating the category', 'danger')
    
    return redirect(url_for('admin.categories'))

@admin.route('/categories/<int:id>/delete', methods=['POST'])
@admin_required
def delete_category(id):
    category = Category.query.get_or_404(id)
    
    if category.articles:
        return jsonify({'error': 'Cannot delete category with existing articles'}), 400
    
    try:
        db.session.delete(category)
        db.session.commit()
        return jsonify({'message': 'Category deleted successfully'})
    except:
        db.session.rollback()
        return jsonify({'error': 'An error occurred while deleting the category'}), 500

@admin.route('/categories/reorder', methods=['POST'])
@admin_required
def reorder_categories():
    try:
        data = request.get_json()
        if not data or 'categories' not in data:
            return jsonify({'error': 'Invalid data'}), 400
            
        category_ids = data['categories']
        
        # Verify all categories exist
        categories = Category.query.filter(Category.id.in_(category_ids)).all()
        if len(categories) != len(category_ids):
            return jsonify({'error': 'Invalid category IDs'}), 400
            
        # Update order for each category
        for index, cat_id in enumerate(category_ids):
            category = next(cat for cat in categories if cat.id == cat_id)
            category.order = index
            
        db.session.commit()
        return jsonify({'message': 'Categories reordered successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin.route('/articles')
@admin_required
def articles():
    articles = Article.query.order_by(Article.created_at.desc()).all()
    categories = Category.query.order_by(Category.name).all()
    return render_template('admin/articles.html', articles=articles, categories=categories)
