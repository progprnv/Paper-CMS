# Simple Vercel Deployment for Paper-CMS
Write-Host "Deploying Paper-CMS to Vercel..." -ForegroundColor Green

# Check if Vercel CLI is installed
try {
    vercel --version | Out-Null
    Write-Host "Vercel CLI found" -ForegroundColor Green
} catch {
    Write-Host "Installing Vercel CLI..." -ForegroundColor Yellow
    npm install -g vercel
}

# Deploy to Vercel
Write-Host "Starting deployment..." -ForegroundColor Yellow
vercel --prod

Write-Host "Deployment complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Remember to add these environment variables in Vercel dashboard:" -ForegroundColor Yellow
Write-Host "FLASK_CONFIG=vercel"
Write-Host "SECRET_KEY=paper-cms-super-secret-key-2025"
Write-Host "SUPABASE_URL=https://xssqhifnabymmsvvybgx.supabase.co"
Write-Host "SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inhzc3FoaWZuYWJ5bW1zdnZ5Ymd4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjA2MDYxOTIsImV4cCI6MjA3NjE4MjE5Mn0.daGDzFRgFgBEpiadzqGF1orCZdYgDJVxljAmmWEY9oI"
Write-Host "SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inhzc3FoaWZuYWJ5bW1zdnZ5Ymd4Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MDYwNjE5MiwiZXhwIjoyMDc2MTgyMTkyfQ.NkI_tmJy-UnQmdz0CCAmqO7ioZhYO04ecVEhPQV2Ckc"
Write-Host "DATABASE_URL=postgresql://postgres:Admin@123#Admin@db.xssqhifnabymmsvvybgx.supabase.co:5432/postgres"
Write-Host "SUPABASE_STORAGE_BUCKET=papers"
Write-Host "VERCEL=1"