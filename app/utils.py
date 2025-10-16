import os
import secrets
from datetime import datetime, timedelta
from flask import current_app, render_template
from flask_mail import Message
from app import mail, db
from app.models import User
import jwt  # PyJWT
from werkzeug.utils import secure_filename

def send_email(to, subject, template, **kwargs):
    """Send email using Flask-Mail"""
    msg = Message(
        subject=subject,
        recipients=[to],
        html=render_template(f'{template}.html', **kwargs),
        sender=current_app.config['MAIL_DEFAULT_SENDER']
    )
    mail.send(msg)

def generate_reset_token(user, expires_in=600):
    """Generate password reset token"""
    payload = {
        'user_id': user.id,
        'exp': datetime.utcnow() + timedelta(seconds=expires_in)
    }
    return jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')

def verify_reset_token(token):
    """Verify password reset token"""
    try:
        payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
        user_id = payload['user_id']
    except:
        return None
    return User.query.get(user_id)

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

def save_file(file, folder_path):
    """Save uploaded file using Supabase Storage or local storage"""
    if file and allowed_file(file.filename):
        try:
            # Import here to avoid circular imports
            from app.supabase_utils import supabase_client
            
            # Add timestamp to prevent conflicts
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
            original_filename = secure_filename(file.filename)
            filename = timestamp + original_filename
            
            # Create a new file object with the updated filename
            file.filename = filename
            
            # Upload to Supabase Storage
            file_url = supabase_client.upload_file(file, folder_path)
            
            if file_url:
                # Return the file URL or path for database storage
                return file_url
            else:
                current_app.logger.error("Failed to upload file")
                return None
                
        except Exception as e:
            current_app.logger.error(f"Error saving file: {e}")
            return None
    return None

def get_file_path(relative_path):
    """Get file URL from Supabase or absolute path for local files"""
    try:
        from app.supabase_utils import supabase_client
        
        # If it's already a URL, return as is
        if relative_path.startswith('http'):
            return relative_path
        
        # Try to get URL from Supabase
        return supabase_client.get_file_url(relative_path)
    except:
        # Fallback to local file path
        if not relative_path.startswith('http'):
            return os.path.join(current_app.config['UPLOAD_FOLDER'], relative_path)
        return relative_path

def delete_file(file_path):
    """Delete file from Supabase Storage or local storage"""
    try:
        from app.supabase_utils import supabase_client
        return supabase_client.delete_file(file_path)
    except Exception as e:
        current_app.logger.error(f"Error deleting file: {e}")
        return False

def format_datetime(value, format='%Y-%m-%d %H:%M'):
    """Format datetime for display"""
    if value is None:
        return ""
    return value.strftime(format)

def get_status_badge_class(status):
    """Get Bootstrap badge class for paper status"""
    status_classes = {
        'SUBMITTED': 'badge-primary',
        'UNDER_REVIEW': 'badge-warning',
        'REVIEWED': 'badge-info',
        'ACCEPTED': 'badge-success',
        'REJECTED': 'badge-danger',
        'REVISION_REQUIRED': 'badge-secondary'
    }
    return status_classes.get(status, 'badge-secondary')

def get_role_badge_class(role):
    """Get Bootstrap badge class for user role"""
    role_classes = {
        'AUTHOR': 'badge-primary',
        'REVIEWER': 'badge-info',
        'ADMIN': 'badge-danger'
    }
    return role_classes.get(role, 'badge-secondary')

def calculate_days_until(target_date):
    """Calculate days until target date"""
    if not target_date:
        return None
    
    today = datetime.now().date()
    target = target_date.date() if hasattr(target_date, 'date') else target_date
    delta = target - today
    return delta.days

def is_deadline_approaching(target_date, days_threshold=7):
    """Check if deadline is approaching within threshold"""
    days_until = calculate_days_until(target_date)
    return days_until is not None and 0 <= days_until <= days_threshold

def paginate_query(query, page, per_page=10):
    """Paginate SQLAlchemy query"""
    return query.paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )

def generate_filename(original_filename, prefix=''):
    """Generate unique filename"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    random_str = secrets.token_hex(8)
    name, ext = os.path.splitext(secure_filename(original_filename))
    return f"{prefix}{timestamp}_{random_str}{ext}"

# Template filters
def register_template_filters(app):
    """Register custom template filters"""
    app.jinja_env.filters['datetime'] = format_datetime
    app.jinja_env.filters['status_badge'] = get_status_badge_class
    app.jinja_env.filters['role_badge'] = get_role_badge_class
    app.jinja_env.filters['days_until'] = calculate_days_until

def format_datetime(value, format='%Y-%m-%d %H:%M'):
    """Format datetime for display"""
    if value is None:
        return ""
    return value.strftime(format)

def get_status_badge_class(status):
    """Get Bootstrap badge class for paper status"""
    status_classes = {
        'SUBMITTED': 'badge-primary',
        'UNDER_REVIEW': 'badge-warning',
        'REVIEWED': 'badge-info',
        'ACCEPTED': 'badge-success',
        'REJECTED': 'badge-danger',
        'REVISION_REQUIRED': 'badge-secondary'
    }
    return status_classes.get(status, 'badge-secondary')

def get_role_badge_class(role):
    """Get Bootstrap badge class for user role"""
    role_classes = {
        'AUTHOR': 'badge-primary',
        'REVIEWER': 'badge-info',
        'ADMIN': 'badge-danger'
    }
    return role_classes.get(role, 'badge-secondary')

def calculate_days_until(target_date):
    """Calculate days until target date"""
    if not target_date:
        return None
    
    today = datetime.now().date()
    target = target_date.date() if hasattr(target_date, 'date') else target_date
    delta = target - today
    return delta.days

def is_deadline_approaching(target_date, days_threshold=7):
    """Check if deadline is approaching within threshold"""
    days_until = calculate_days_until(target_date)
    return days_until is not None and 0 <= days_until <= days_threshold

def paginate_query(query, page, per_page=10):
    """Paginate SQLAlchemy query"""
    return query.paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )

def generate_filename(original_filename, prefix=''):
    """Generate unique filename"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    random_str = secrets.token_hex(8)
    name, ext = os.path.splitext(secure_filename(original_filename))
    return f"{prefix}{timestamp}_{random_str}{ext}"

# Template filters
def register_template_filters(app):
    """Register custom template filters"""
    app.jinja_env.filters['datetime'] = format_datetime
    app.jinja_env.filters['status_badge'] = get_status_badge_class
    app.jinja_env.filters['role_badge'] = get_role_badge_class
    app.jinja_env.filters['days_until'] = calculate_days_until