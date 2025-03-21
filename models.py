from datetime import datetime
from extensions import db
import bleach

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    articles = db.relationship('Article', backref='category', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': bleach.clean(self.name),
            'description': bleach.clean(self.description) if self.description else '',
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
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': bleach.clean(self.title),
            'content': bleach.clean(self.content),
            'category_id': self.category_id,
            'category_name': bleach.clean(self.category.name),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'views': self.views
        }
    
    def increment_views(self):
        self.views += 1
        db.session.commit()
