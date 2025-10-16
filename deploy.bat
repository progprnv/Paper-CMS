@echo off
REM Paper-CMS Supabase & Vercel Deployment Script for Windows

echo 🚀 Paper-CMS Deployment Setup
echo ================================

REM Check if npm is installed
npm --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ npm is not installed. Please install Node.js first.
    pause
    exit /b 1
)
echo ✅ npm is installed

REM Check if git is installed
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ git is not installed. Please install Git first.
    pause
    exit /b 1
)
echo ✅ git is installed

REM Install Vercel CLI if not present
vercel --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 📦 Installing Vercel CLI...
    npm install -g vercel
) else (
    echo ✅ Vercel CLI is installed
)

REM Install Supabase CLI if not present
supabase --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 📦 Installing Supabase CLI...
    npm install -g supabase
) else (
    echo ✅ Supabase CLI is installed
)

echo.
echo 🔧 Setup Instructions:
echo ======================
echo.
echo 1. 🗄️  Setup Supabase:
echo    - Go to https://supabase.com/
echo    - Create a new project
echo    - Get your project URL and keys from Settings ^> API
echo    - Create a storage bucket named 'papers'
echo.
echo 2. ⚙️  Configure Environment Variables:
echo    - Copy .env.template to .env
echo    - Fill in your Supabase credentials
echo    - Generate a secure SECRET_KEY
echo.
echo 3. 🚀 Deploy to Vercel:
echo    - Run: vercel
echo    - Add environment variables in Vercel dashboard
echo    - Set up custom domain (optional)
echo.
echo 4. 🗃️  Initialize Database:
echo    - Run the setup SQL in Supabase SQL Editor
echo    - Or use: python run.py init_db (locally first)
echo.
echo 📝 Environment Variables needed:
echo    SUPABASE_URL
echo    SUPABASE_ANON_KEY
echo    SUPABASE_SERVICE_ROLE_KEY
echo    DATABASE_URL
echo    SECRET_KEY
echo    SUPABASE_STORAGE_BUCKET=papers
echo.
echo 🎉 Ready for deployment!
echo Run 'vercel' to deploy your application.
pause