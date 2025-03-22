from datetime import datetime
from extensions import db
import bleach
import re
import html
from sqlalchemy import func

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500))
    order = db.Column(db.Integer, default=0)  # New field for ordering
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    articles = db.relationship('Article', backref='category', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': bleach.clean(self.name),
            'description': bleach.clean(self.description) if self.description else '',
            'order': self.order,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    views = db.Column(db.Integer, default=0)
    upvotes = db.Column(db.Integer, nullable=False, default=0)
    downvotes = db.Column(db.Integer, nullable=False, default=0)
    
    def get_preview(self, length=100):
        # Remove HTML tags for the preview
        text = re.sub(r'<[^>]+>', '', self.content)
        # Decode HTML entities
        text = html.unescape(text)
        # Remove extra whitespace
        text = ' '.join(text.split())
        # Truncate to length and add ellipsis if needed
        if len(text) > length:
            return text[:length].rsplit(' ', 1)[0] + '...'
        return text
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': bleach.clean(self.title),
            'content': bleach.clean(self.content),
            'preview': self.get_preview(100),
            'category_id': self.category_id,
            'category_name': bleach.clean(self.category.name),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'views': self.views,
            'upvotes': self.upvotes or 0,
            'downvotes': self.downvotes or 0,
            'rating_percentage': self.get_rating_percentage()
        }
    
    def increment_views(self):
        self.views += 1
        db.session.commit()
        
    def get_rating_percentage(self):
        total_votes = (self.upvotes or 0) + (self.downvotes or 0)
        if total_votes == 0:
            return 0
        return round(((self.upvotes or 0) * 100.0) / total_votes)

class SearchLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    term = db.Column(db.String(100), nullable=False)
    results_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    ip_address = db.Column(db.String(45))  # To accommodate IPv6 addresses
    
    def to_dict(self):
        return {
            'id': self.id,
            'term': bleach.clean(self.term),
            'results_count': self.results_count,
            'created_at': self.created_at.isoformat()
        }
    
    @staticmethod
    def get_popular_searches(limit=10):
        # Use func.count() to count occurrences
        # Use func.max() to get the most recent search time
        return db.session.query(
            SearchLog.term,  # Keep original term for display
            func.count(SearchLog.id).label('count'),
            func.max(SearchLog.created_at).label('last_searched')
        ).group_by(
            func.lower(SearchLog.term)  # Group by lowercase term
        ).order_by(
            func.desc('count'),  # Order by count first
            func.desc('last_searched')  # Then by most recent search
        ).limit(limit).all()
