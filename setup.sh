#!/bin/bash

# PaperFlow CMS Quick Setup Script
# This script helps you set up the PaperFlow CMS development environment

echo "🚀 PaperFlow CMS Quick Setup"
echo "=============================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

echo "✅ Python 3 found"

# Check Python version
python_version=$(python3 -c "import sys; print('.'.join(map(str, sys.version_info[:2])))")
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" = "$required_version" ]; then
    echo "✅ Python version $python_version is supported"
else
    echo "❌ Python version $python_version is not supported. Please install Python 3.8 or higher."
    exit 1
fi

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔧 Activating virtual environment..."
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
    # Windows (Git Bash)
    source venv/Scripts/activate
else
    # macOS/Linux
    source venv/bin/activate
fi

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Create .env file from template
if [ ! -f .env ]; then
    echo "⚙️  Creating .env file from template..."
    cp .env.example .env
    echo "📝 Please edit the .env file with your configuration before running the application"
else
    echo "✅ .env file already exists"
fi

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p app/static/uploads
mkdir -p logs

# Database setup instructions
echo ""
echo "🗄️  Database Setup Instructions:"
echo "================================="
echo "1. Install MySQL 8.0 or higher"
echo "2. Create a database and user:"
echo "   mysql -u root -p"
echo "   CREATE DATABASE paperflow_cms CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
echo "   CREATE USER 'paperflow_user'@'localhost' IDENTIFIED BY 'your_password';"
echo "   GRANT ALL PRIVILEGES ON paperflow_cms.* TO 'paperflow_user'@'localhost';"
echo "   FLUSH PRIVILEGES;"
echo "   EXIT;"
echo ""
echo "3. Import the database schema:"
echo "   mysql -u paperflow_user -p paperflow_cms < schema.sql"
echo ""
echo "4. Update the DATABASE_URL in your .env file"
echo ""

# Final instructions
echo "🎉 Setup Complete!"
echo "=================="
echo ""
echo "Next steps:"
echo "1. Configure your .env file with proper database credentials"
echo "2. Set up your MySQL database using the instructions above"
echo "3. Initialize the application:"
echo "   flask deploy"
echo ""
echo "4. Run the application:"
echo "   python run.py"
echo ""
echo "5. Open your browser and go to http://localhost:5000"
echo ""
echo "Default admin credentials:"
echo "Email: admin@paperflow.com"
echo "Password: admin123"
echo ""
echo "📖 For detailed instructions, see the README.md file"
echo ""

# Check if MySQL is installed
if command -v mysql &> /dev/null; then
    echo "✅ MySQL found on system"
else
    echo "⚠️  MySQL not found. Please install MySQL 8.0 or higher"
    echo "   Download from: https://dev.mysql.com/downloads/mysql/"
fi

echo "🎊 Happy coding with PaperFlow CMS!"