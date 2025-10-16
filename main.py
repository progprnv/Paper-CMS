"""
Flask application entry point for Vercel deployment.
This file serves as the main entry point that Vercel recognizes.
"""

import os
from app import create_app

# Determine config based on environment
config_name = os.getenv('FLASK_CONFIG', 'default')
if os.getenv('VERCEL'):
    config_name = 'vercel'

# Create the Flask application instance at module level (required for Vercel)
app = create_app(config_name)

if __name__ == '__main__':
    # This won't run in Vercel, but useful for local testing
    app.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))