from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, send_file, abort, jsonify
from flask_login import login_required, current_user
from sqlalchemy import or_, and_
from app import db
from app.models import Paper, Review, Conference, Category, User, PaperStatus, UserRole, ReviewRecommendation
from app.forms import PaperSubmissionForm, ReviewForm, SearchForm, AffiliationForm
from app.utils import save_file, get_file_path, paginate_query, is_deadline_approaching
from datetime import datetime
import os

main = Blueprint('main', __name__)

@main.route('/favicon.ico')
def favicon():
    """Serve a simple emoji favicon"""
    return '📄', 200, {'Content-Type': 'text/plain; charset=utf-8'}

@main.route('/health')
def health_check():
    """Simple health check endpoint"""
    try:
        return {
            'status': 'ok',
            'message': 'Paper-CMS is running',
            'config': current_app.config.get('FLASK_CONFIG', 'unknown'),
            'has_db_env': 'DATABASE_URL' in os.environ,
            'vercel_env': 'VERCEL' in os.environ
        }, 200
    except Exception as e:
        return {'status': 'error', 'message': str(e)}, 500

@main.route('/test-db')
def test_db():
    """Test database connection"""
    try:
        from app.models import User
        # Show the database URL being used (without password)
        db_url = current_app.config.get('SQLALCHEMY_DATABASE_URI', 'Not set')
        # Hide password for security
        safe_db_url = db_url.split('@')[1] if '@' in db_url else 'Invalid URL format'
        
        # Try to query the database
        user_count = User.query.count()
        return {
            'status': 'ok', 
            'message': 'Database connection successful',
            'user_count': user_count,
            'db_host': safe_db_url
        }, 200
    except Exception as e:
        db_url = current_app.config.get('SQLALCHEMY_DATABASE_URI', 'Not set')
        safe_db_url = db_url.split('@')[1] if '@' in db_url else 'Invalid URL format'
        return {
            'status': 'error', 
            'message': f'Database error: {str(e)}',
            'db_host': safe_db_url
        }, 500

@main.route('/debug-config')
def debug_config():
    """Debug configuration - REMOVE IN PRODUCTION"""
    try:
        from urllib.parse import quote_plus
        
        # Test URL construction
        db_password = 'Admin@123#Admin'
        encoded_password = quote_plus(db_password)
        test_url = f'postgresql://postgres:{encoded_password}@db.xssqhifnabymmsvvybgx.supabase.co:5432/postgres'
        
        db_url = current_app.config.get('SQLALCHEMY_DATABASE_URI', 'Not set')
        
        # Parse the actual URL being used
        if '@' in db_url:
            parts = db_url.split('@')
            if len(parts) >= 2:
                auth_part = parts[0]  # postgresql://postgres:password
                host_part = parts[1]  # host:port/db
                actual_host = host_part.split(':')[0] if ':' in host_part else host_part.split('/')[0]
            else:
                actual_host = 'Parse failed'
        else:
            actual_host = 'No @ found in URL'
        
        return {
            'status': 'ok',
            'original_password': db_password,
            'encoded_password': encoded_password,
            'test_constructed_url': test_url,
            'actual_db_url_host': actual_host,
            'has_env_db_url': 'DATABASE_URL' in os.environ,
            'env_db_url': os.environ.get('DATABASE_URL', 'Not set')[:50] + '...' if os.environ.get('DATABASE_URL') else 'Not set'
        }, 200
    except Exception as e:
        return {'status': 'error', 'message': str(e)}, 500

@main.route('/init-db')
def init_db():
    """Initialize database tables - USE ONLY ONCE"""
    try:
        # Import all models to ensure they're registered
        from app.models import User, Paper, Review, Conference, Category, Affiliation
        
        # Create all tables
        db.create_all()
        
        return {
            'status': 'ok',
            'message': 'Database tables created successfully'
        }, 200
    except Exception as e:
        return {
            'status': 'error',
            'message': f'Database initialization error: {str(e)}'
        }, 500

@main.route('/')
def index():
    """Homepage"""
    try:
        # Get statistics - with error handling for database issues
        total_papers = 0
        total_users = 0
        active_conferences = 0
        recent_papers = []
        
        try:
            total_papers = Paper.query.count()
            total_users = User.query.count()
            active_conferences = Conference.query.filter_by(status='ACTIVE').count()
            recent_papers = Paper.query.order_by(Paper.submission_date.desc()).limit(5).all()
        except Exception as db_error:
            current_app.logger.warning(f'Database query failed: {db_error}')
            # Continue with default values
        
        return render_template('index.html', 
                             title='PaperFlow CMS - Academic Paper Management',
                             total_papers=total_papers,
                             total_users=total_users,
                             active_conferences=active_conferences,
                             recent_papers=recent_papers)
    except Exception as e:
        current_app.logger.error(f'Index route error: {e}')
        return f'Error loading page: {str(e)}', 500

@main.route('/dashboard')
@login_required
def dashboard():
    """Role-based dashboard"""
    if current_user.role == UserRole.ADMIN:
        return redirect(url_for('admin.dashboard'))
    elif current_user.role == UserRole.REVIEWER:
        return redirect(url_for('main.reviewer_dashboard'))
    else:
        return redirect(url_for('main.author_dashboard'))

@main.route('/author/dashboard')
@login_required
def author_dashboard():
    """Author dashboard"""
    if current_user.role not in [UserRole.AUTHOR, UserRole.ADMIN]:
        abort(403)
    
    # Get author's papers
    papers = Paper.query.filter(Paper.authors.contains(current_user)).order_by(Paper.submission_date.desc()).all()
    
    # Get statistics
    stats = {
        'total_papers': len(papers),
        'accepted': len([p for p in papers if p.status == PaperStatus.ACCEPTED]),
        'under_review': len([p for p in papers if p.status == PaperStatus.UNDER_REVIEW]),
        'rejected': len([p for p in papers if p.status == PaperStatus.REJECTED])
    }
    
    return render_template('dashboard/author.html', 
                         title='Author Dashboard',
                         papers=papers,
                         stats=stats)

@main.route('/reviewer/dashboard')
@login_required
def reviewer_dashboard():
    """Reviewer dashboard"""
    if current_user.role not in [UserRole.REVIEWER, UserRole.ADMIN]:
        abort(403)
    
    # Get assigned reviews
    assigned_reviews = Review.query.filter_by(reviewer_id=current_user.id, is_completed=False).all()
    completed_reviews = Review.query.filter_by(reviewer_id=current_user.id, is_completed=True).order_by(Review.review_date.desc()).limit(10).all()
    
    # Get approaching deadlines
    approaching_deadlines = [r for r in assigned_reviews if r.deadline and is_deadline_approaching(r.deadline)]
    
    stats = {
        'pending_reviews': len(assigned_reviews),
        'completed_reviews': Review.query.filter_by(reviewer_id=current_user.id, is_completed=True).count(),
        'approaching_deadlines': len(approaching_deadlines)
    }
    
    return render_template('dashboard/reviewer.html',
                         title='Reviewer Dashboard',
                         assigned_reviews=assigned_reviews,
                         completed_reviews=completed_reviews,
                         approaching_deadlines=approaching_deadlines,
                         stats=stats)

@main.route('/submit-paper', methods=['GET', 'POST'])
@login_required
def submit_paper():
    """Paper submission"""
    if current_user.role not in [UserRole.AUTHOR, UserRole.ADMIN]:
        abort(403)
    
    form = PaperSubmissionForm()
    if form.validate_on_submit():
        # Save uploaded file
        file_path = None
        if form.file.data:
            folder_path = f"papers/{form.conference_name.data.replace(' ', '_')}"
            file_path = save_file(form.file.data, folder_path)
        
        # Create paper
        paper = Paper(
            title=form.title.data,
            abstract=form.abstract.data,
            keywords=form.keywords.data,
            conference_name=form.conference_name.data,
            file_path=file_path,
            submitted_by=current_user.id,
            status=PaperStatus.SUBMITTED
        )
        
        # Add authors (include submitter)
        paper.authors.append(current_user)
        
        # Add categories
        for category_id in form.categories.data:
            category = Category.query.get(category_id)
            if category:
                paper.categories.append(category)
        
        db.session.add(paper)
        db.session.commit()
        
        flash(f'Paper "{paper.title}" submitted successfully!', 'success')
        return redirect(url_for('main.paper_detail', id=paper.id))
    
    return render_template('papers/submit.html', title='Submit Paper', form=form)

@main.route('/paper/<int:id>')
@login_required
def paper_detail(id):
    """Paper detail view"""
    paper = Paper.query.get_or_404(id)
    
    # Check access permissions
    can_view = (
        current_user.role == UserRole.ADMIN or
        current_user in paper.authors or
        Review.query.filter_by(paper_id=paper.id, reviewer_id=current_user.id).first()
    )
    
    if not can_view:
        abort(403)
    
    # Get reviews if user is author or admin
    reviews = []
    if current_user.role == UserRole.ADMIN or current_user in paper.authors:
        reviews = Review.query.filter_by(paper_id=paper.id, is_completed=True).all()
    
    # Check if current user can review this paper
    user_review = Review.query.filter_by(paper_id=paper.id, reviewer_id=current_user.id).first()
    
    return render_template('papers/detail.html',
                         title=paper.title,
                         paper=paper,
                         reviews=reviews,
                         user_review=user_review)

@main.route('/review/<int:paper_id>', methods=['GET', 'POST'])
@login_required
def submit_review(paper_id):
    """Submit paper review"""
    if current_user.role not in [UserRole.REVIEWER, UserRole.ADMIN]:
        abort(403)
    
    paper = Paper.query.get_or_404(paper_id)
    review = Review.query.filter_by(paper_id=paper_id, reviewer_id=current_user.id).first()
    
    if not review:
        abort(404)  # Review assignment not found
    
    if review.is_completed:
        flash('You have already completed this review.', 'info')
        return redirect(url_for('main.paper_detail', id=paper_id))
    
    form = ReviewForm()
    if form.validate_on_submit():
        # Update review
        review.technical_quality = form.technical_quality.data
        review.novelty = form.novelty.data
        review.clarity = form.clarity.data
        review.significance = form.significance.data
        review.score = form.overall_score.data
        review.recommendation = ReviewRecommendation[form.recommendation.data]
        review.comments = form.comments.data
        review.confidential_comments = form.confidential_comments.data
        review.mark_completed()
        
        # Update paper status if all reviews are completed
        total_reviews = Review.query.filter_by(paper_id=paper_id).count()
        completed_reviews = Review.query.filter_by(paper_id=paper_id, is_completed=True).count()
        
        if completed_reviews >= paper.conference.reviews_per_paper:
            paper.status = PaperStatus.REVIEWED
        elif paper.status == PaperStatus.SUBMITTED:
            paper.status = PaperStatus.UNDER_REVIEW
        
        db.session.commit()
        
        flash('Review submitted successfully!', 'success')
        return redirect(url_for('main.reviewer_dashboard'))
    
    return render_template('reviews/submit.html',
                         title=f'Review: {paper.title}',
                         paper=paper,
                         review=review,
                         form=form)

@main.route('/papers')
@login_required
def browse_papers():
    """Browse and search papers"""
    page = request.args.get('page', 1, type=int)
    form = SearchForm()
    
    # Build query
    query = Paper.query
    
    # Apply filters from form
    if request.args.get('query'):
        search_term = f"%{request.args.get('query')}%"
        query = query.filter(or_(
            Paper.title.like(search_term),
            Paper.abstract.like(search_term),
            Paper.keywords.like(search_term)
        ))
    
    if request.args.get('conference_id'):
        query = query.filter_by(conference_id=request.args.get('conference_id', type=int))
    
    if request.args.get('status'):
        query = query.filter_by(status=PaperStatus[request.args.get('status')])
    
    if request.args.get('category_id'):
        category = Category.query.get(request.args.get('category_id', type=int))
        if category:
            query = query.filter(Paper.categories.contains(category))
    
    # Apply role-based filtering
    if current_user.role == UserRole.AUTHOR:
        # Authors see their own papers and public accepted papers
        query = query.filter(or_(
            Paper.authors.contains(current_user),
            Paper.status == PaperStatus.ACCEPTED
        ))
    elif current_user.role == UserRole.REVIEWER:
        # Reviewers see papers they're assigned to review and public accepted papers
        reviewed_paper_ids = [r.paper_id for r in Review.query.filter_by(reviewer_id=current_user.id).all()]
        query = query.filter(or_(
            Paper.id.in_(reviewed_paper_ids),
            Paper.status == PaperStatus.ACCEPTED
        ))
    
    # Order by submission date
    query = query.order_by(Paper.submission_date.desc())
    
    # Paginate
    pagination = paginate_query(query, page, per_page=10)
    papers = pagination.items
    
    return render_template('papers/browse.html',
                         title='Browse Papers',
                         form=form,
                         papers=papers,
                         pagination=pagination)

@main.route('/download/<int:paper_id>')
@login_required
def download_paper(paper_id):
    """Download paper file"""
    paper = Paper.query.get_or_404(paper_id)
    
    # Check access permissions
    can_download = (
        current_user.role == UserRole.ADMIN or
        current_user in paper.authors or
        Review.query.filter_by(paper_id=paper.id, reviewer_id=current_user.id).first() or
        paper.status == PaperStatus.ACCEPTED
    )
    
    if not can_download:
        abort(403)
    
    if not paper.file_path:
        abort(404)
    
    file_path = get_file_path(paper.file_path)
    if not os.path.exists(file_path):
        abort(404)
    
    return send_file(file_path, as_attachment=True, download_name=f"{paper.title}.pdf")

@main.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """User profile management"""
    affiliation_form = AffiliationForm()
    
    if affiliation_form.validate_on_submit():
        from app.models import Affiliation
        
        # If setting as primary, unset other primary affiliations
        if affiliation_form.is_primary.data:
            current_user.affiliations.filter_by(is_primary=True).update({'is_primary': False})
        
        affiliation = Affiliation(
            user_id=current_user.id,
            institution_name=affiliation_form.institution_name.data,
            department=affiliation_form.department.data,
            position=affiliation_form.position.data,
            is_primary=affiliation_form.is_primary.data
        )
        
        db.session.add(affiliation)
        db.session.commit()
        
        flash('Affiliation added successfully!', 'success')
        return redirect(url_for('main.profile'))
    
    return render_template('auth/profile.html',
                         title='Profile',
                         user=current_user,
                         affiliation_form=affiliation_form)

@main.route('/api/paper-stats/<int:paper_id>')
@login_required
def paper_stats(paper_id):
    """API endpoint for paper statistics"""
    paper = Paper.query.get_or_404(paper_id)
    
    # Check access permissions
    if current_user.role != UserRole.ADMIN and current_user not in paper.authors:
        abort(403)
    
    reviews = Review.query.filter_by(paper_id=paper_id, is_completed=True).all()
    
    stats = {
        'total_reviews': len(reviews),
        'average_score': paper.average_score,
        'score_breakdown': {
            'technical_quality': sum(r.technical_quality for r in reviews) / len(reviews) if reviews else 0,
            'novelty': sum(r.novelty for r in reviews) / len(reviews) if reviews else 0,
            'clarity': sum(r.clarity for r in reviews) / len(reviews) if reviews else 0,
            'significance': sum(r.significance for r in reviews) / len(reviews) if reviews else 0,
        },
        'recommendations': {
            rec.value: len([r for r in reviews if r.recommendation == rec])
            for rec in ReviewRecommendation
        }
    }
    
    return jsonify(stats)