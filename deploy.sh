#!/bin/bash

# Paper-CMS Supabase & Vercel Deployment Script

echo "🚀 Paper-CMS Deployment Setup"
echo "================================"

# Check if required tools are installed
check_tool() {
    if ! command -v $1 &> /dev/null; then
        echo "❌ $1 is not installed. Please install it first."
        exit 1
    else
        echo "✅ $1 is installed"
    fi
}

echo "📋 Checking required tools..."
check_tool "npm"
check_tool "git"

# Install Vercel CLI if not present
if ! command -v vercel &> /dev/null; then
    echo "📦 Installing Vercel CLI..."
    npm install -g vercel
else
    echo "✅ Vercel CLI is installed"
fi

# Install Supabase CLI if not present
if ! command -v supabase &> /dev/null; then
    echo "📦 Installing Supabase CLI..."
    npm install -g supabase
else
    echo "✅ Supabase CLI is installed"
fi

echo ""
echo "🔧 Setup Instructions:"
echo "======================"
echo ""
echo "1. 🗄️  Setup Supabase:"
echo "   - Go to https://supabase.com/"
echo "   - Create a new project"
echo "   - Get your project URL and keys from Settings > API"
echo "   - Create a storage bucket named 'papers'"
echo ""
echo "2. ⚙️  Configure Environment Variables:"
echo "   - Copy .env.template to .env"
echo "   - Fill in your Supabase credentials"
echo "   - Generate a secure SECRET_KEY"
echo ""
echo "3. 🚀 Deploy to Vercel:"
echo "   - Run: vercel"
echo "   - Add environment variables in Vercel dashboard"
echo "   - Set up custom domain (optional)"
echo ""
echo "4. 🗃️  Initialize Database:"
echo "   - Run the setup SQL in Supabase SQL Editor"
echo "   - Or use: python run.py init_db (locally first)"
echo ""
echo "📝 Environment Variables needed:"
echo "   SUPABASE_URL"
echo "   SUPABASE_ANON_KEY"
echo "   SUPABASE_SERVICE_ROLE_KEY"
echo "   DATABASE_URL"
echo "   SECRET_KEY"
echo "   SUPABASE_STORAGE_BUCKET=papers"
echo ""
echo "🎉 Ready for deployment!"
echo "Run 'vercel' to deploy your application."