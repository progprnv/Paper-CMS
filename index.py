"""
Alternative Flask entry point for Vercel (index.py)
"""

from main import app

# This is required for Vercel to detect the Flask app
if __name__ == "__main__":
    app.run()