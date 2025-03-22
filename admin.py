from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from functools import wraps
from flask import current_app, session
from werkzeug.security import check_password_hash
import bleach
from models import db, Category, Article, SearchLog
from datetime import datetime
import os
from werkzeug.utils import secure_filename
from sqlalchemy import func

admin = Blueprint('admin', __name__, url_prefix='/admin')

# Add ALLOWED_EXTENSIONS and upload folder configuration at the top
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
UPLOAD_FOLDER = 'static/uploads'

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return redirect(url_for('admin.login'))
        return f(*args, **kwargs)
    return decorated_function

def clean_content(content):
    """Clean and sanitize HTML content while preserving safe styles"""
    allowed_tags = [
        'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'strong', 'em', 'u', 'ol', 'ul', 'li', 
        'br', 'hr', 'a', 'img', 'blockquote', 'code', 'pre', 'div', 'span', 'table', 
        'thead', 'tbody', 'tr', 'th', 'td'
    ]
    
    allowed_attributes = {
        '*': ['class', 'style', 'id'],
        'a': ['href', 'title', 'target'],
        'img': ['src', 'alt', 'title', 'width', 'height'],
        'td': ['colspan', 'rowspan'],
        'th': ['colspan', 'rowspan', 'scope']
    }
    
    allowed_protocols = ['http', 'https', 'mailto']
    
    # First pass: clean the HTML
    cleaned = bleach.clean(
        content,
        tags=allowed_tags,
        attributes=allowed_attributes,
        protocols=allowed_protocols,
        strip=True,
        strip_comments=True
    )
    
    # Second pass: clean styles using bleach-allowlist
    from bleach.css_sanitizer import CSSSanitizer
    
    css_sanitizer = CSSSanitizer(
        allowed_css_properties=[
            'text-align', 'margin', 'padding', 'width', 'height', 'border',
            'background-color', 'color', 'font-size', 'font-weight', 'font-style',
            'text-decoration', 'vertical-align', 'margin-left', 'margin-right',
            'float', 'display'
        ]
    )
    
    final_cleaned = bleach.clean(
        cleaned,
        tags=allowed_tags,
        attributes=allowed_attributes,
        protocols=allowed_protocols,
        css_sanitizer=css_sanitizer,
        strip=True,
        strip_comments=True
    )
    
    return final_cleaned

@admin.route('/')
@admin_required
def index():
    # Get all data
    categories = Category.query.all()
    articles = Article.query.all()
    total_views = sum(article.views for article in articles)
    total_searches = db.session.query(db.func.count(SearchLog.id)).scalar() or 0
    recent_articles = Article.query.order_by(Article.created_at.desc()).limit(5).all()
    popular_searches = SearchLog.get_popular_searches(10)
    
    # Get search metrics for the pie chart
    searches_with_results = db.session.query(func.count(SearchLog.id)).filter(SearchLog.results_count > 0).scalar() or 0
    searches_no_results = total_searches - searches_with_results
    
    # Calculate statistics
    stats = {
        'total_articles': len(articles),
        'total_views': total_views,
        'total_categories': len(categories),
        'average_rating': sum(article.get_rating_percentage() for article in articles) / len(articles) if articles else 0,
        'search_metrics': {
            'with_results': searches_with_results,
            'no_results': searches_no_results
        }
    }
    
    return render_template('admin/index.html', 
                         stats=stats,
                         categories=categories,
                         articles=articles,
                         total_views=total_views,
                         total_searches=total_searches,
                         recent_articles=recent_articles,
                         popular_searches=popular_searches)

@admin.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if (username == current_app.config['ADMIN_USERNAME'] and 
            check_password_hash(current_app.config['ADMIN_PASSWORD_HASH'], password)):
            session['admin_logged_in'] = True
            return redirect(url_for('admin.index'))
        
        flash('Invalid credentials', 'danger')
    return render_template('admin/login.html')

@admin.route('/logout')
def logout():
    session.pop('admin_logged_in', None)
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
    max_order = db.session.query(db.func.max(Category.order)).scalar() or 0
    
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
    
    category = Category.query.get_or_404(id)
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
        flash('Cannot delete category that has articles', 'danger')
        return redirect(url_for('admin.categories'))
    
    try:
        db.session.delete(category)
        db.session.commit()
        flash('Category deleted successfully', 'success')
    except:
        db.session.rollback()
        flash('An error occurred while deleting the category', 'danger')
    
    return redirect(url_for('admin.categories'))

@admin.route('/articles')
@admin_required
def articles():
    articles = Article.query.order_by(Article.created_at.desc()).all()
    categories = Category.query.order_by(Category.name).all()
    return render_template('admin/articles.html', articles=articles, categories=categories)

@admin.route('/articles/add', methods=['POST'])
@admin_required
def add_article():
    title = request.form.get('title', '').strip()
    content = request.form.get('content', '').strip()
    keywords = request.form.get('keywords', '').strip()
    category_id = request.form.get('category_id')
    
    if not title or not content or not category_id:
        flash('Title, content, and category are required', 'danger')
        return redirect(url_for('admin.articles'))
        
    if len(title) > 200:
        flash('Title must be less than 200 characters', 'danger')
        return redirect(url_for('admin.articles'))
    
    # Sanitize input
    title = bleach.clean(title, tags=[], strip=True)
    content = clean_content(content)
    keywords = bleach.clean(keywords, tags=[], strip=True)
    
    article = Article(
        title=title,
        content=content,
        category_id=category_id
    )
    
    # Set keywords if provided
    if keywords:
        article.set_keywords(keywords.split(','))
    
    db.session.add(article)
    
    try:
        db.session.commit()
        flash('Article added successfully', 'success')
    except:
        db.session.rollback()
        flash('An error occurred while adding the article', 'danger')
    
    return redirect(url_for('admin.articles'))

@admin.route('/articles/<int:id>/edit', methods=['POST'])
@admin_required
def edit_article(id):
    title = request.form.get('title', '').strip()
    content = request.form.get('content', '').strip()
    keywords = request.form.get('keywords', '').strip()
    category_id = request.form.get('category_id')
    
    if not title or not content or not category_id:
        flash('Title, content, and category are required', 'danger')
        return redirect(url_for('admin.articles'))
        
    if len(title) > 200:
        flash('Title must be less than 200 characters', 'danger')
        return redirect(url_for('admin.articles'))
    
    # Sanitize input
    title = bleach.clean(title, tags=[], strip=True)
    content = clean_content(content)
    keywords = bleach.clean(keywords, tags=[], strip=True)
    
    article = Article.query.get_or_404(id)
    article.title = title
    article.content = content
    article.category_id = category_id
    
    # Update keywords
    article.set_keywords(keywords.split(',') if keywords else [])
    
    article.updated_at = datetime.utcnow()
    
    try:
        db.session.commit()
        flash('Article updated successfully', 'success')
    except:
        db.session.rollback()
        flash('An error occurred while updating the article', 'danger')
    
    return redirect(url_for('admin.articles'))

@admin.route('/articles/<int:id>/delete', methods=['POST'])
@admin_required
def delete_article(id):
    article = Article.query.get_or_404(id)
    
    try:
        db.session.delete(article)
        db.session.commit()
        flash('Article deleted successfully', 'success')
    except:
        db.session.rollback()
        flash('An error occurred while deleting the article', 'danger')
    
    return redirect(url_for('admin.articles'))

@admin.route('/categories/reorder', methods=['POST'])
@admin_required
def reorder_categories():
    categories = request.json.get('categories', [])
    
    try:
        for index, category_id in enumerate(categories):
            category = Category.query.get(category_id)
            if category:
                category.order = index
        
        db.session.commit()
        return jsonify({'message': 'Categories reordered successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin.route('/upload', methods=['POST'])
@admin_required
def upload_image():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if file and allowed_file(file.filename):
        # Secure the filename and create upload directory if it doesn't exist
        filename = secure_filename(file.filename)
        upload_path = os.path.join(current_app.root_path, UPLOAD_FOLDER)
        os.makedirs(upload_path, exist_ok=True)
        
        # Save the file
        file_path = os.path.join(upload_path, filename)
        file.save(file_path)
        
        # Return the URL for TinyMCE
        url = url_for('static', filename=f'uploads/{filename}')
        return jsonify({
            'location': url
        })
    
    return jsonify({'error': 'Invalid file type'}), 400

@admin.route('/search-report')
@admin_required
def search_report():
    total_searches = db.session.query(db.func.count(SearchLog.id)).scalar() or 0
    avg_results = db.session.query(db.func.avg(SearchLog.results_count)).scalar() or 0
    no_results_count = db.session.query(db.func.count(SearchLog.id))\
        .filter(SearchLog.results_count == 0).scalar() or 0
    no_results_rate = (no_results_count / total_searches * 100) if total_searches > 0 else 0
    
    # Get the most recent 100 searches for initial display
    searches = SearchLog.query.order_by(SearchLog.created_at.desc()).limit(100).all()
    
    return render_template('admin/search_report.html',
                         total_searches=total_searches,
                         avg_results=avg_results,
                         no_results_rate=no_results_rate,
                         searches=searches)

@admin.route('/api/search-logs')
@admin_required
def get_search_logs():
    searches = SearchLog.query.order_by(SearchLog.created_at.desc()).all()
    return jsonify([{
        'term': search.term,
        'results_count': search.results_count,
        'created_at': search.created_at.isoformat(),
        'ip_address': search.ip_address
    } for search in searches])

@admin.route('/dashboard-data')
@admin_required
def dashboard_data():
    # Get search metrics for the pie chart
    total_searches = db.session.query(func.count(SearchLog.id)).scalar() or 0
    searches_with_results = db.session.query(func.count(SearchLog.id)).filter(SearchLog.results_count > 0).scalar() or 0
    searches_no_results = total_searches - searches_with_results
    
    return jsonify({
        'search_metrics': {
            'with_results': searches_with_results,
            'no_results': searches_no_results
        }
    })

# Log changes
with open('changes.log', 'a') as f:
    f.write('\n[{}] Added rich text article support\n'.format(
        datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    ))
    f.write('- Added TinyMCE rich text editor\n')
    f.write('- Added article management (CRUD operations)\n')
    f.write('- Added proper HTML sanitization for articles\n')
    f.write('- Added responsive article management interface\n')
