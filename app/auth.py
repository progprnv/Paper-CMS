from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash
from app import db, limiter
from app.models import User, UserRole
from app.forms import LoginForm, RegistrationForm, PasswordResetRequestForm, PasswordResetForm
from app.utils import send_email, generate_reset_token, verify_reset_token
from datetime import datetime

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def login():
    """User login route"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        
        if user and user.check_password(form.password.data):
            if not user.is_active:
                flash('Your account has been deactivated. Please contact an administrator.', 'error')
                return redirect(url_for('auth.login'))
            
            login_user(user, remember=True)
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            next_page = request.args.get('next')
            if not next_page or not next_page.startswith('/'):
                next_page = url_for('main.dashboard')
            
            flash(f'Welcome back, {user.name}!', 'success')
            return redirect(next_page)
        else:
            flash('Invalid email or password.', 'error')
    
    return render_template('auth/login.html', title='Sign In', form=form)

@auth.route('/register', methods=['GET', 'POST'])
@limiter.limit("3 per minute")
def register():
    """User registration route"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        try:
            user = User(
                name=form.name.data,
                email=form.email.data,
                role=UserRole[form.role.data]
            )
            user.set_password(form.password.data)
            
            db.session.add(user)
            db.session.commit()
            
            flash('Registration successful! You can now log in.', 'success')
            
            # Send welcome email
            try:
                send_email(
                    user.email,
                    'Welcome to PaperFlow CMS',
                    'auth/email/welcome',
                    user=user
                )
            except Exception as e:
                current_app.logger.error(f"Failed to send welcome email: {e}")
            
            return redirect(url_for('auth.login'))
            
        except Exception as e:
            current_app.logger.error(f"Registration error: {e}")
            db.session.rollback()
            flash(f'Registration failed: {str(e)}', 'error')
            return render_template('auth/register.html', title='Register', form=form)
    
    return render_template('auth/register.html', title='Register', form=form)

@auth.route('/logout')
@login_required
def logout():
    """User logout route"""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))

@auth.route('/reset-password-request', methods=['GET', 'POST'])
@limiter.limit("3 per hour")
def reset_password_request():
    """Password reset request route"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            token = generate_reset_token(user)
            send_email(
                user.email,
                'Reset Your Password - PaperFlow CMS',
                'auth/email/reset_password',
                user=user,
                token=token
            )
        
        flash('Check your email for instructions to reset your password.', 'info')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/reset_password_request.html', title='Reset Password', form=form)

@auth.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """Password reset route"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    user = verify_reset_token(token)
    if not user:
        flash('Invalid or expired reset token.', 'error')
        return redirect(url_for('auth.reset_password_request'))
    
    form = PasswordResetForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset successfully.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/reset_password.html', title='Reset Password', form=form)

@auth.route('/profile')
@login_required
def profile():
    """User profile page"""
    return render_template('auth/profile.html', title='Profile', user=current_user)