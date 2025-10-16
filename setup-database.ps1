# Automated Supabase Database Setup for Windows
# This script connects to your Supabase database and runs the setup SQL

Write-Host "🗄️  Setting up Paper-CMS database in Supabase..." -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Green

# Your Supabase connection details
$DB_URL = "postgresql://postgres:Admin@123#Admin@db.xssqhifnabymmsvvybgx.supabase.co:5432/postgres"

# Check if psql is available
try {
    psql --version | Out-Null
    Write-Host "✅ PostgreSQL client found" -ForegroundColor Green
    
    Write-Host "🔗 Connecting to Supabase database..." -ForegroundColor Yellow
    psql $DB_URL -f supabase_setup_simple.sql
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "✅ Database setup complete!" -ForegroundColor Green
        Write-Host "🎉 Your Paper-CMS database is ready!" -ForegroundColor Green
        Write-Host ""
        Write-Host "Default admin login:" -ForegroundColor Yellow
        Write-Host "Email: admin@paper-cms.com" -ForegroundColor White
        Write-Host "Password: admin123" -ForegroundColor White
        Write-Host ""
        Write-Host "⚠️  Remember to change the admin password after first login!" -ForegroundColor Red
    } else {
        Write-Host ""
        Write-Host "❌ Database setup failed. Please run the SQL manually:" -ForegroundColor Red
        Write-Host "   1. Go to https://supabase.com/dashboard/project/xssqhifnabymmsvvybgx/sql" -ForegroundColor Yellow
        Write-Host "   2. Copy and paste the contents of supabase_setup_simple.sql" -ForegroundColor Yellow
        Write-Host "   3. Click 'Run'" -ForegroundColor Yellow
    }
} catch {
    Write-Host "❌ PostgreSQL client (psql) is not installed." -ForegroundColor Red
    Write-Host "Please install PostgreSQL client or run the SQL manually in Supabase SQL Editor" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "📋 Copy and paste the contents of supabase_setup_simple.sql" -ForegroundColor Cyan
    Write-Host "   into your Supabase SQL Editor at:" -ForegroundColor Cyan
    Write-Host "   https://supabase.com/dashboard/project/xssqhifnabymmsvvybgx/sql" -ForegroundColor White
}