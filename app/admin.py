from flask import Blueprint, render_template, redirect, url_for, flash, request, abort, jsonify
from flask_login import login_required, current_user
from sqlalchemy import func, desc
from app import db
from app.models import User, Paper, Review, Conference, Category, UserRole, PaperStatus, ReviewRecommendation
from app.forms import UserManagementForm, ConferenceForm, CategoryForm, ReviewerAssignmentForm
from datetime import datetime, timedelta
import calendar
from functools import wraps

admin = Blueprint('admin', __name__)

def admin_required(f):
    """Decorator to require admin role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.role != UserRole.ADMIN:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

@admin.route('/dashboard')
@login_required
@admin_required
@admin_required
def dashboard():
    """Admin dashboard with system overview"""
    
    # Basic statistics
    total_users = User.query.count()
    total_papers = Paper.query.count()
    total_reviews = Review.query.filter_by(is_completed=True).count()
    active_conferences = Conference.query.filter_by(status='ACTIVE').count()
    
    # User statistics by role
    user_stats = db.session.query(
        User.role,
        func.count(User.id).label('count')
    ).group_by(User.role).all()
    
    # Paper statistics by status
    paper_stats = db.session.query(
        Paper.status,
        func.count(Paper.id).label('count')
    ).group_by(Paper.status).all()
    
    # Monthly submission trends (last 12 months)
    twelve_months_ago = datetime.now() - timedelta(days=365)
    monthly_submissions = db.session.query(
        func.year(Paper.submission_date).label('year'),
        func.month(Paper.submission_date).label('month'),
        func.count(Paper.id).label('count')
    ).filter(
        Paper.submission_date >= twelve_months_ago
    ).group_by(
        func.year(Paper.submission_date),
        func.month(Paper.submission_date)
    ).order_by(
        func.year(Paper.submission_date),
        func.month(Paper.submission_date)
    ).all()
    
    # Recent activity
    recent_papers = Paper.query.order_by(desc(Paper.submission_date)).limit(5).all()
    recent_reviews = Review.query.filter_by(is_completed=True).order_by(desc(Review.review_date)).limit(5).all()
    
    # Pending reviews
    pending_reviews = Review.query.filter_by(is_completed=False).count()
    overdue_reviews = Review.query.filter(
        Review.deadline < datetime.now(),
        Review.is_completed == False
    ).count()
    
    return render_template('admin/dashboard.html',
                         title='Admin Dashboard',
                         total_users=total_users,
                         total_papers=total_papers,
                         total_reviews=total_reviews,
                         active_conferences=active_conferences,
                         user_stats=user_stats,
                         paper_stats=paper_stats,
                         monthly_submissions=monthly_submissions,
                         recent_papers=recent_papers,
                         recent_reviews=recent_reviews,
                         pending_reviews=pending_reviews,
                         overdue_reviews=overdue_reviews)

@admin.route('/users')
@login_required
@admin_required
def manage_users():
    """User management interface"""
    page = request.args.get('page', 1, type=int)
    role_filter = request.args.get('role')
    search = request.args.get('search', '')
    
    query = User.query
    
    # Apply filters
    if role_filter:
        query = query.filter_by(role=UserRole[role_filter])
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            db.or_(
                User.name.like(search_term),
                User.email.like(search_term)
            )
        )
    
    query = query.order_by(User.name)
    pagination = query.paginate(page=page, per_page=20, error_out=False)
    users = pagination.items
    
    return render_template('admin/users.html',
                         title='Manage Users',
                         users=users,
                         pagination=pagination,
                         role_filter=role_filter,
                         search=search)

@admin.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(user_id):
    """Edit user details"""
    user = User.query.get_or_404(user_id)
    form = UserManagementForm(obj=user)
    
    if form.validate_on_submit():
        user.name = form.name.data
        user.email = form.email.data
        user.role = UserRole[form.role.data]
        user.is_active = form.is_active.data
        
        db.session.commit()
        flash(f'User {user.name} updated successfully!', 'success')
        return redirect(url_for('admin.manage_users'))
    
    return render_template('admin/edit_user.html',
                         title=f'Edit User: {user.name}',
                         form=form,
                         user=user)

@admin.route('/users/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    """Delete user (soft delete by deactivating)"""
    user = User.query.get_or_404(user_id)
    
    if user.id == current_user.id:
        flash('You cannot delete your own account!', 'error')
        return redirect(url_for('admin.manage_users'))
    
    user.is_active = False
    db.session.commit()
    
    flash(f'User {user.name} has been deactivated.', 'success')
    return redirect(url_for('admin.manage_users'))

@admin.route('/papers')
@login_required
@admin_required
def manage_papers():
    """Paper management interface"""
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status')
    conference_filter = request.args.get('conference', type=int)
    search = request.args.get('search', '')
    
    query = Paper.query
    
    # Apply filters
    if status_filter:
        query = query.filter_by(status=PaperStatus[status_filter])
    
    if conference_filter:
        query = query.filter_by(conference_id=conference_filter)
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            db.or_(
                Paper.title.like(search_term),
                Paper.abstract.like(search_term)
            )
        )
    
    query = query.order_by(desc(Paper.submission_date))
    pagination = query.paginate(page=page, per_page=20, error_out=False)
    papers = pagination.items
    
    # Get conferences for filter dropdown
    conferences = Conference.query.all()
    
    return render_template('admin/papers.html',
                         title='Manage Papers',
                         papers=papers,
                         pagination=pagination,
                         conferences=conferences,
                         status_filter=status_filter,
                         conference_filter=conference_filter,
                         search=search)

@admin.route('/papers/<int:paper_id>/update-status', methods=['POST'])
@login_required
@admin_required
def update_paper_status(paper_id):
    """Update paper status"""
    paper = Paper.query.get_or_404(paper_id)
    new_status = request.form.get('status')
    
    if new_status in [s.value for s in PaperStatus]:
        paper.status = PaperStatus[new_status]
        paper.last_updated = datetime.utcnow()
        db.session.commit()
        
        flash(f'Paper status updated to {new_status.replace("_", " ").title()}', 'success')
    else:
        flash('Invalid status provided!', 'error')
    
    return redirect(url_for('admin.manage_papers'))

@admin.route('/assign-reviewers')
@login_required
@admin_required
def assign_reviewers():
    """Reviewer assignment interface"""
    # Get papers that need reviewers
    papers_needing_reviewers = []
    
    for paper in Paper.query.filter(Paper.status.in_([PaperStatus.SUBMITTED, PaperStatus.UNDER_REVIEW])).all():
        assigned_reviewers = Review.query.filter_by(paper_id=paper.id).count()
        if assigned_reviewers < paper.conference.reviews_per_paper:
            papers_needing_reviewers.append({
                'paper': paper,
                'assigned_reviewers': assigned_reviewers,
                'needed_reviewers': paper.conference.reviews_per_paper - assigned_reviewers
            })
    
    return render_template('admin/assign_reviewers.html',
                         title='Assign Reviewers',
                         papers_needing_reviewers=papers_needing_reviewers)

@admin.route('/papers/<int:paper_id>/assign-reviewer', methods=['GET', 'POST'])
@login_required
@admin_required
def assign_reviewer_to_paper(paper_id):
    """Assign specific reviewer to paper"""
    paper = Paper.query.get_or_404(paper_id)
    form = ReviewerAssignmentForm()
    
    # Get reviewers not already assigned to this paper
    assigned_reviewer_ids = [r.reviewer_id for r in Review.query.filter_by(paper_id=paper_id).all()]
    available_reviewers = User.query.filter(
        User.role == UserRole.REVIEWER,
        User.is_active == True,
        ~User.id.in_(assigned_reviewer_ids)
    ).all()
    
    form.reviewer_id.choices = [(r.id, f"{r.name} ({r.email})") for r in available_reviewers]
    
    if form.validate_on_submit():
        # Check if reviewer is already assigned
        existing_review = Review.query.filter_by(
            paper_id=paper_id,
            reviewer_id=form.reviewer_id.data
        ).first()
        
        if existing_review:
            flash('This reviewer is already assigned to this paper!', 'error')
        else:
            review = Review(
                paper_id=paper_id,
                reviewer_id=form.reviewer_id.data,
                deadline=form.deadline.data
            )
            
            db.session.add(review)
            
            # Update paper status if this is the first reviewer
            if paper.status == PaperStatus.SUBMITTED:
                paper.status = PaperStatus.UNDER_REVIEW
            
            db.session.commit()
            
            reviewer = User.query.get(form.reviewer_id.data)
            flash(f'Reviewer {reviewer.name} assigned to paper "{paper.title}"', 'success')
            return redirect(url_for('admin.assign_reviewers'))
    
    return render_template('admin/assign_reviewer.html',
                         title=f'Assign Reviewer to: {paper.title}',
                         paper=paper,
                         form=form)

@admin.route('/conferences')
@login_required
@admin_required
def manage_conferences():
    """Conference management interface"""
    conferences = Conference.query.order_by(desc(Conference.year), Conference.name).all()
    return render_template('admin/conferences.html',
                         title='Manage Conferences',
                         conferences=conferences)

@admin.route('/conferences/new', methods=['GET', 'POST'])
@login_required
@admin_required
def add_conference():
    """Add new conference"""
    form = ConferenceForm()
    
    if form.validate_on_submit():
        conference = Conference(
            name=form.name.data,
            year=form.year.data,
            submission_deadline=form.submission_deadline.data,
            review_deadline=form.review_deadline.data,
            notification_date=form.notification_date.data,
            description=form.description.data,
            website=form.website.data,
            reviews_per_paper=form.reviews_per_paper.data
        )
        
        db.session.add(conference)
        db.session.commit()
        
        flash(f'Conference "{conference.name} {conference.year}" created successfully!', 'success')
        return redirect(url_for('admin.manage_conferences'))
    
    return render_template('admin/conference_form.html',
                         title='Add Conference',
                         form=form)

@admin.route('/conferences/<int:conference_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_conference(conference_id):
    """Edit conference"""
    conference = Conference.query.get_or_404(conference_id)
    form = ConferenceForm(obj=conference)
    
    if form.validate_on_submit():
        form.populate_obj(conference)
        db.session.commit()
        
        flash(f'Conference "{conference.name} {conference.year}" updated successfully!', 'success')
        return redirect(url_for('admin.manage_conferences'))
    
    return render_template('admin/conference_form.html',
                         title=f'Edit Conference: {conference.name} {conference.year}',
                         form=form,
                         conference=conference)

@admin.route('/categories')
@login_required
@admin_required
def manage_categories():
    """Category management interface"""
    categories = Category.query.order_by(Category.name).all()
    return render_template('admin/categories.html',
                         title='Manage Categories',
                         categories=categories)

@admin.route('/categories/new', methods=['GET', 'POST'])
@login_required
@admin_required
def add_category():
    """Add new category"""
    form = CategoryForm()
    
    if form.validate_on_submit():
        category = Category(
            name=form.name.data,
            description=form.description.data,
            color=form.color.data
        )
        
        db.session.add(category)
        db.session.commit()
        
        flash(f'Category "{category.name}" created successfully!', 'success')
        return redirect(url_for('admin.manage_categories'))
    
    return render_template('admin/category_form.html',
                         title='Add Category',
                         form=form)

@admin.route('/api/dashboard-stats')
@login_required
@admin_required
def dashboard_stats():
    """API endpoint for dashboard statistics"""
    
    # Monthly submission data for chart
    twelve_months_ago = datetime.now() - timedelta(days=365)
    monthly_data = db.session.query(
        func.year(Paper.submission_date).label('year'),
        func.month(Paper.submission_date).label('month'),
        func.count(Paper.id).label('submissions')
    ).filter(
        Paper.submission_date >= twelve_months_ago
    ).group_by(
        func.year(Paper.submission_date),
        func.month(Paper.submission_date)
    ).all()
    
    # Format data for charts
    chart_data = []
    for item in monthly_data:
        month_name = calendar.month_abbr[item.month]
        chart_data.append({
            'month': f"{month_name} {item.year}",
            'submissions': item.submissions
        })
    
    # Status distribution
    status_data = db.session.query(
        Paper.status,
        func.count(Paper.id).label('count')
    ).group_by(Paper.status).all()
    
    status_distribution = [
        {'status': status.value.replace('_', ' ').title(), 'count': count}
        for status, count in status_data
    ]
    
    return jsonify({
        'monthly_submissions': chart_data,
        'status_distribution': status_distribution
    })