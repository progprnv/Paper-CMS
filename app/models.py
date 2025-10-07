from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import enum

from app import db

# Enums for better data integrity
class UserRole(enum.Enum):
    AUTHOR = "AUTHOR"
    REVIEWER = "REVIEWER"
    ADMIN = "ADMIN"

class PaperStatus(enum.Enum):
    SUBMITTED = "SUBMITTED"
    UNDER_REVIEW = "UNDER_REVIEW"
    REVIEWED = "REVIEWED"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    REVISION_REQUIRED = "REVISION_REQUIRED"

class ReviewRecommendation(enum.Enum):
    ACCEPT = "ACCEPT"
    MINOR_REVISION = "MINOR_REVISION"
    MAJOR_REVISION = "MAJOR_REVISION"
    REJECT = "REJECT"

class ConferenceStatus(enum.Enum):
    ACTIVE = "ACTIVE"
    CLOSED = "CLOSED"
    UPCOMING = "UPCOMING"

# Association tables for many-to-many relationships
paper_authors = db.Table('paper_authors',
    db.Column('paper_id', db.Integer, db.ForeignKey('papers.id'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True)
)

paper_categories = db.Table('paper_categories',
    db.Column('paper_id', db.Integer, db.ForeignKey('papers.id'), primary_key=True),
    db.Column('category_id', db.Integer, db.ForeignKey('categories.id'), primary_key=True)
)

class User(UserMixin, db.Model):
    """User model for authors, reviewers, and administrators"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum(UserRole), nullable=False, default=UserRole.AUTHOR)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    authored_papers = db.relationship('Paper', secondary=paper_authors, backref='authors')
    reviews = db.relationship('Review', backref='reviewer', lazy='dynamic')
    affiliations = db.relationship('Affiliation', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if provided password matches hash"""
        return check_password_hash(self.password_hash, password)
    
    def has_role(self, role):
        """Check if user has specific role"""
        return self.role == role
    
    def __repr__(self):
        return f'<User {self.email}>'

class Paper(db.Model):
    """Research paper model"""
    __tablename__ = 'papers'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(500), nullable=False)
    abstract = db.Column(db.Text, nullable=False)
    status = db.Column(db.Enum(PaperStatus), nullable=False, default=PaperStatus.SUBMITTED)
    submission_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    file_path = db.Column(db.String(500))
    conference_id = db.Column(db.Integer, db.ForeignKey('conferences.id'), nullable=False)
    
    # Metadata
    keywords = db.Column(db.String(500))
    submitted_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    conference = db.relationship('Conference', backref='papers')
    reviews = db.relationship('Review', backref='paper', lazy='dynamic', cascade='all, delete-orphan')
    categories = db.relationship('Category', secondary=paper_categories, backref='papers')
    submitter = db.relationship('User', foreign_keys=[submitted_by])
    
    @property
    def average_score(self):
        """Calculate average review score"""
        completed_reviews = self.reviews.filter(Review.score.isnot(None)).all()
        if not completed_reviews:
            return None
        return sum(review.score for review in completed_reviews) / len(completed_reviews)
    
    @property
    def review_count(self):
        """Get number of completed reviews"""
        return self.reviews.filter(Review.score.isnot(None)).count()
    
    def __repr__(self):
        return f'<Paper {self.title}>'

class Review(db.Model):
    """Peer review model"""
    __tablename__ = 'reviews'
    
    id = db.Column(db.Integer, primary_key=True)
    paper_id = db.Column(db.Integer, db.ForeignKey('papers.id'), nullable=False)
    reviewer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    score = db.Column(db.Integer)  # 1-10 scale
    comments = db.Column(db.Text)
    recommendation = db.Column(db.Enum(ReviewRecommendation))
    review_date = db.Column(db.DateTime)
    assigned_date = db.Column(db.DateTime, default=datetime.utcnow)
    deadline = db.Column(db.DateTime)
    is_completed = db.Column(db.Boolean, default=False)
    
    # Detailed scoring
    technical_quality = db.Column(db.Integer)  # 1-10
    novelty = db.Column(db.Integer)  # 1-10
    clarity = db.Column(db.Integer)  # 1-10
    significance = db.Column(db.Integer)  # 1-10
    
    def mark_completed(self):
        """Mark review as completed"""
        self.is_completed = True
        self.review_date = datetime.utcnow
    
    def __repr__(self):
        return f'<Review {self.id} for Paper {self.paper_id}>'

class Conference(db.Model):
    """Conference/venue model"""
    __tablename__ = 'conferences'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    submission_deadline = db.Column(db.DateTime, nullable=False)
    review_deadline = db.Column(db.DateTime)
    notification_date = db.Column(db.DateTime)
    status = db.Column(db.Enum(ConferenceStatus), nullable=False, default=ConferenceStatus.UPCOMING)
    description = db.Column(db.Text)
    website = db.Column(db.String(500))
    
    # Review settings
    reviews_per_paper = db.Column(db.Integer, default=3)
    
    def __repr__(self):
        return f'<Conference {self.name} {self.year}>'

class Category(db.Model):
    """Research category/topic model"""
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)
    color = db.Column(db.String(7), default='#007bff')  # Hex color for UI
    
    def __repr__(self):
        return f'<Category {self.name}>'

class Affiliation(db.Model):
    """User affiliation/institution model"""
    __tablename__ = 'affiliations'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    institution_name = db.Column(db.String(200), nullable=False)
    department = db.Column(db.String(200))
    position = db.Column(db.String(100))
    is_primary = db.Column(db.Boolean, default=False)
    
    def __repr__(self):
        return f'<Affiliation {self.institution_name}>'

# Indexes for better performance
db.Index('idx_users_email', User.email)
db.Index('idx_papers_status', Paper.status)
db.Index('idx_papers_conference', Paper.conference_id)
db.Index('idx_reviews_paper', Review.paper_id)
db.Index('idx_reviews_reviewer', Review.reviewer_id)