from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from config import config
import os

db = SQLAlchemy()
login_manager = LoginManager()
mail = Mail()
limiter = Limiter(key_func=get_remote_address)

def create_app(config_name=None):
    """Application factory pattern"""
    app = Flask(__name__)
    
    # Load configuration
    config_name = config_name or os.getenv('FLASK_CONFIG', 'default')
    if os.getenv('VERCEL'):
        config_name = 'vercel'
    
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    limiter.init_app(app)
    
    # Initialize Supabase
    from app.supabase_utils import supabase_client
    supabase_client.init_app(app)
    
    # Configure Flask-Login
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def load_user(user_id):
        from app.models import User
        return User.query.get(int(user_id))
    
    # Register blueprints after app is created to avoid circular imports
    with app.app_context():
        from app.routes import main
        from app.auth import auth
        from app.admin import admin
        
        app.register_blueprint(main)
        app.register_blueprint(auth, url_prefix='/auth')
        app.register_blueprint(admin, url_prefix='/admin')
    
    # Create upload directory (for local development)
    upload_dir = app.config.get('UPLOAD_FOLDER')
    if upload_dir and not os.path.exists(upload_dir):
        try:
            os.makedirs(upload_dir, exist_ok=True)
        except Exception as e:
            app.logger.warning(f"Could not create upload directory: {e}")
    
    # Register template filters
    from app.utils import register_template_filters
    register_template_filters(app)
    
    # Add context processor for current year
    @app.context_processor
    def inject_current_year():
        from datetime import datetime
        return {'current_year': datetime.now().year}
    
    return app