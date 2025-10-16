#!/bin/bash
# Paper-CMS Vercel Deployment Script
# This script sets up your environment variables and deploys to Vercel

echo "🚀 Paper-CMS Vercel Deployment Setup"
echo "====================================="

# Check if Vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    echo "❌ Vercel CLI is not installed. Installing now..."
    npm install -g vercel
fi

# Login to Vercel
echo "🔑 Logging in to Vercel..."
vercel login

# Set environment variables
echo "⚙️  Setting up environment variables..."

vercel env add FLASK_CONFIG vercel
vercel env add SECRET_KEY paper-cms-super-secret-key-2025-$(date +%s)
vercel env add SUPABASE_URL https://xssqhifnabymmsvvybgx.supabase.co
vercel env add DATABASE_URL "postgresql://postgres:Admin@123#Admin@db.xssqhifnabymmsvvybgx.supabase.co:5432/postgres"
vercel env add SUPABASE_STORAGE_BUCKET papers
vercel env add VERCEL 1

echo "⚠️  IMPORTANT: You need to manually add these API keys from Supabase:"
echo "   - SUPABASE_ANON_KEY"
echo "   - SUPABASE_SERVICE_ROLE_KEY"
echo ""
echo "Get them from: https://supabase.com/dashboard/project/xssqhifnabymmsvvybgx/settings/api"
echo ""

# Deploy to Vercel
echo "🚀 Deploying to Vercel..."
vercel --prod

echo ""
echo "✅ Deployment complete!"
echo "🔗 Your app should be live on Vercel"
echo ""
echo "Next steps:"
echo "1. Add your Supabase API keys to Vercel environment variables"
echo "2. Run the database setup SQL in Supabase"
echo "3. Create the 'papers' storage bucket in Supabase"
echo "4. Test your deployment!"