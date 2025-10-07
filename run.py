import os
import sys
from app import create_app, db
from flask.cli import with_appcontext
import click

app = create_app(os.getenv('FLASK_CONFIG') or 'default')

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
    from app.models import User
    
    # Create database tables
    db.create_all()
    
    # Create default admin user
    admin = User.query.filter_by(email='admin@paperflow.com').first()
    if admin is None:
        from werkzeug.security import generate_password_hash
        admin = User(
            name='System Administrator',
            email='admin@paperflow.com',
            password_hash=generate_password_hash('admin123'),
            role='ADMIN'
        )
        db.session.add(admin)
        db.session.commit()
        print('Created default admin user')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)