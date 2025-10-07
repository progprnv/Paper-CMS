# PaperFlow CMS Quick Setup Script for Windows PowerShell
# This script helps you set up the PaperFlow CMS development environment on Windows

Write-Host "🚀 PaperFlow CMS Quick Setup" -ForegroundColor Green
Write-Host "==============================" -ForegroundColor Green

# Check if Python is installed
try {
    $pythonVersion = python --version 2>&1
    if ($pythonVersion -match "Python (\d+\.\d+)") {
        $version = [version]$Matches[1]
        if ($version -ge [version]"3.8") {
            Write-Host "✅ Python $($Matches[1]) found and supported" -ForegroundColor Green
        } else {
            Write-Host "❌ Python $($Matches[1]) found but version 3.8+ required" -ForegroundColor Red
            exit 1
        }
    }
} catch {
    Write-Host "❌ Python not found. Please install Python 3.8 or higher." -ForegroundColor Red
    Write-Host "Download from: https://www.python.org/downloads/" -ForegroundColor Yellow
    exit 1
}

# Create virtual environment
Write-Host "📦 Creating virtual environment..." -ForegroundColor Blue
python -m venv venv

# Activate virtual environment
Write-Host "🔧 Activating virtual environment..." -ForegroundColor Blue
& ".\venv\Scripts\Activate.ps1"

# Upgrade pip
Write-Host "⬆️  Upgrading pip..." -ForegroundColor Blue
python -m pip install --upgrade pip

# Install dependencies
Write-Host "📚 Installing dependencies..." -ForegroundColor Blue
pip install -r requirements.txt

# Create .env file from template
if (-not (Test-Path ".env")) {
    Write-Host "⚙️  Creating .env file from template..." -ForegroundColor Blue
    Copy-Item ".env.example" ".env"
    Write-Host "📝 Please edit the .env file with your configuration before running the application" -ForegroundColor Yellow
} else {
    Write-Host "✅ .env file already exists" -ForegroundColor Green
}

# Create necessary directories
Write-Host "📁 Creating necessary directories..." -ForegroundColor Blue
New-Item -ItemType Directory -Force -Path "app\static\uploads" | Out-Null
New-Item -ItemType Directory -Force -Path "logs" | Out-Null

# Database setup instructions
Write-Host ""
Write-Host "🗄️  Database Setup Instructions:" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan
Write-Host "1. Install MySQL 8.0 or higher" -ForegroundColor White
Write-Host "   Download from: https://dev.mysql.com/downloads/mysql/" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Create a database and user:" -ForegroundColor White
Write-Host "   mysql -u root -p" -ForegroundColor Gray
Write-Host "   CREATE DATABASE paperflow_cms CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;" -ForegroundColor Gray
Write-Host "   CREATE USER 'paperflow_user'@'localhost' IDENTIFIED BY 'your_password';" -ForegroundColor Gray
Write-Host "   GRANT ALL PRIVILEGES ON paperflow_cms.* TO 'paperflow_user'@'localhost';" -ForegroundColor Gray
Write-Host "   FLUSH PRIVILEGES;" -ForegroundColor Gray
Write-Host "   EXIT;" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Import the database schema:" -ForegroundColor White
Write-Host "   mysql -u paperflow_user -p paperflow_cms < schema.sql" -ForegroundColor Gray
Write-Host ""
Write-Host "4. Update the DATABASE_URL in your .env file" -ForegroundColor White
Write-Host ""

# Final instructions
Write-Host "🎉 Setup Complete!" -ForegroundColor Green
Write-Host "=================="
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Configure your .env file with proper database credentials" -ForegroundColor White
Write-Host "2. Set up your MySQL database using the instructions above" -ForegroundColor White
Write-Host "3. Initialize the application:" -ForegroundColor White
Write-Host "   flask deploy" -ForegroundColor Gray
Write-Host ""
Write-Host "4. Run the application:" -ForegroundColor White
Write-Host "   python run.py" -ForegroundColor Gray
Write-Host ""
Write-Host "5. Open your browser and go to http://localhost:5000" -ForegroundColor White
Write-Host ""
Write-Host "Default admin credentials:" -ForegroundColor Yellow
Write-Host "Email: admin@paperflow.com" -ForegroundColor White
Write-Host "Password: admin123" -ForegroundColor White
Write-Host ""
Write-Host "📖 For detailed instructions, see the README.md file" -ForegroundColor Cyan
Write-Host ""

# Check if MySQL is installed
try {
    $mysqlVersion = mysql --version 2>&1
    if ($mysqlVersion -match "mysql") {
        Write-Host "✅ MySQL found on system" -ForegroundColor Green
    }
} catch {
    Write-Host "⚠️  MySQL not found. Please install MySQL 8.0 or higher" -ForegroundColor Yellow
    Write-Host "   Download from: https://dev.mysql.com/downloads/mysql/" -ForegroundColor Gray
}

Write-Host ""
Write-Host "🎊 Happy coding with PaperFlow CMS!" -ForegroundColor Green

# Pause to let user read the output
Write-Host ""
Write-Host "Press any key to continue..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")