import os
import sys
from app import create_app, db
from flask.cli import with_appcontext
import click

# Determine config based on environment
config_name = os.getenv('FLASK_CONFIG', 'default')
if os.getenv('VERCEL'):
    config_name = 'vercel'

app = create_app(config_name)

@app.cli.command()
@click.option('--coverage/--no-coverage', default=False, help='Run tests under code coverage.')
def test(coverage):
    """Run the unit tests."""
    if coverage and not os.environ.get('FLASK_COVERAGE'):
        import subprocess
        os.environ['FLASK_COVERAGE'] = '1'
        subprocess.run([sys.executable] + sys.argv)
    
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)

@app.cli.command()
def deploy():
    """Run deployment tasks."""
    # Import models here to avoid circular imports
    from app.models import User, UserRole
    
    # Create database tables
    db.create_all()
    
    # Create default admin user
    admin = User.query.filter_by(email='admin@paper-cms.com').first()
    if admin is None:
        from werkzeug.security import generate_password_hash
        admin = User(
            name='System Administrator',
            email='admin@paper-cms.com',
            password_hash=generate_password_hash('admin123'),
            role=UserRole.ADMIN
        )
        db.session.add(admin)
        db.session.commit()
        print('Created default admin user')

@app.cli.command()
def init_db():
    """Initialize database with tables and default data."""
    with app.app_context():
        db.create_all()
        
        # Import models
        from app.models import User, UserRole, Category
        from werkzeug.security import generate_password_hash
        
        # Create admin user if not exists
        admin = User.query.filter_by(email='admin@paper-cms.com').first()
        if not admin:
            admin = User(
                name='Administrator',
                email='admin@paper-cms.com',
                role=UserRole.ADMIN,
                password_hash=generate_password_hash('admin123')
            )
            db.session.add(admin)
        
        # Create default categories
        default_categories = [
            ('Computer Science', 'General CS research', '#007bff'),
            ('Machine Learning', 'AI and ML papers', '#28a745'),
            ('Data Science', 'Data analysis research', '#ffc107'),
            ('Software Engineering', 'Software development research', '#dc3545'),
            ('Cybersecurity', 'Security and privacy research', '#6f42c1')
        ]
        
        for name, desc, color in default_categories:
            if not Category.query.filter_by(name=name).first():
                category = Category(name=name, description=desc, color=color)
                db.session.add(category)
        
        db.session.commit()
        print('Database initialized successfully!')

# For Vercel serverless deployment
def handler(request):
    """Vercel serverless handler"""
    return app(request.environ, lambda status, headers: None)

if __name__ == '__main__':
    # Local development
    if os.getenv('VERCEL'):
        # Don't run if in Vercel environment
        pass
    else:
        app.run(debug=True, host='0.0.0.0', port=5000)