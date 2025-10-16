#!/bin/bash
# Automated Supabase Database Setup
# This script connects to your Supabase database and runs the setup SQL

echo "🗄️  Setting up Paper-CMS database in Supabase..."
echo "================================================"

# Your Supabase connection details
DB_URL="postgresql://postgres:Admin@123#Admin@db.xssqhifnabymmsvvybgx.supabase.co:5432/postgres"

# Check if psql is available
if ! command -v psql &> /dev/null; then
    echo "❌ PostgreSQL client (psql) is not installed."
    echo "Please install PostgreSQL client or run the SQL manually in Supabase SQL Editor"
    echo ""
    echo "📋 Copy and paste the contents of supabase_setup_simple.sql"
    echo "   into your Supabase SQL Editor at:"
    echo "   https://supabase.com/dashboard/project/xssqhifnabymmsvvybgx/sql"
    exit 1
fi

echo "🔗 Connecting to Supabase database..."
psql "$DB_URL" -f supabase_setup_simple.sql

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Database setup complete!"
    echo "🎉 Your Paper-CMS database is ready!"
    echo ""
    echo "Default admin login:"
    echo "Email: admin@paper-cms.com"
    echo "Password: admin123"
    echo ""
    echo "⚠️  Remember to change the admin password after first login!"
else
    echo ""
    echo "❌ Database setup failed. Please run the SQL manually:"
    echo "   1. Go to https://supabase.com/dashboard/project/xssqhifnabymmsvvybgx/sql"
    echo "   2. Copy and paste the contents of supabase_setup_simple.sql"
    echo "   3. Click 'Run'"
fi