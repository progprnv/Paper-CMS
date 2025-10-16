# Paper-CMS Vercel Deployment Script for Windows
# This script sets up your environment variables and deploys to Vercel

Write-Host "🚀 Paper-CMS Vercel Deployment Setup" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Green

# Check if Vercel CLI is installed
try {
    vercel --version | Out-Null
    Write-Host "✅ Vercel CLI is already installed" -ForegroundColor Green
} catch {
    Write-Host "❌ Vercel CLI is not installed. Installing now..." -ForegroundColor Red
    npm install -g vercel
}

# Login to Vercel
Write-Host "🔑 Logging in to Vercel..." -ForegroundColor Yellow
vercel login

# Set environment variables
Write-Host "⚙️  Setting up environment variables..." -ForegroundColor Yellow

$secretKey = "paper-cms-super-secret-key-2025-$(Get-Date -Format 'yyyyMMddHHmmss')"

# Add environment variables to Vercel
Write-Host "Adding FLASK_CONFIG..." -ForegroundColor Cyan
echo "vercel" | vercel env add FLASK_CONFIG

Write-Host "Adding SECRET_KEY..." -ForegroundColor Cyan
echo $secretKey | vercel env add SECRET_KEY

Write-Host "Adding SUPABASE_URL..." -ForegroundColor Cyan
echo "https://xssqhifnabymmsvvybgx.supabase.co" | vercel env add SUPABASE_URL

Write-Host "Adding SUPABASE_ANON_KEY..." -ForegroundColor Cyan
echo "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inhzc3FoaWZuYWJ5bW1zdnZ5Ymd4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjA2MDYxOTIsImV4cCI6MjA3NjE4MjE5Mn0.daGDzFRgFgBEpiadzqGF1orCZdYgDJVxljAmmWEY9oI" | vercel env add SUPABASE_ANON_KEY

Write-Host "Adding SUPABASE_SERVICE_ROLE_KEY..." -ForegroundColor Cyan
echo "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inhzc3FoaWZuYWJ5bW1zdnZ5Ymd4Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MDYwNjE5MiwiZXhwIjoyMDc2MTgyMTkyfQ.NkI_tmJy-UnQmdz0CCAmqO7ioZhYO04ecVEhPQV2Ckc" | vercel env add SUPABASE_SERVICE_ROLE_KEY

Write-Host "Adding DATABASE_URL..." -ForegroundColor Cyan
echo "postgresql://postgres:Admin@123#Admin@db.xssqhifnabymmsvvybgx.supabase.co:5432/postgres" | vercel env add DATABASE_URL

Write-Host "Adding SUPABASE_STORAGE_BUCKET..." -ForegroundColor Cyan
echo "papers" | vercel env add SUPABASE_STORAGE_BUCKET

Write-Host "Adding VERCEL flag..." -ForegroundColor Cyan
echo "1" | vercel env add VERCEL

Write-Host ""
Write-Host "✅ All environment variables configured!" -ForegroundColor Green
Write-Host ""

# Deploy to Vercel
Write-Host "🚀 Deploying to Vercel..." -ForegroundColor Green
vercel --prod

Write-Host ""
Write-Host "✅ Deployment complete!" -ForegroundColor Green
Write-Host "🔗 Your app should be live on Vercel" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Add your Supabase API keys to Vercel environment variables" -ForegroundColor White
Write-Host "2. Run the database setup SQL in Supabase" -ForegroundColor White
Write-Host "3. Create the 'papers' storage bucket in Supabase" -ForegroundColor White
Write-Host "4. Test your deployment!" -ForegroundColor White