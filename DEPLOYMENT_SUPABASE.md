# 🚀 Paper-CMS Automated Deployment Guide

Your Paper-CMS is now configured for your specific Supabase database! Here's everything you need to deploy it automatically.

## 📋 Quick Overview

**Your Supabase Project**: `xssqhifnabymmsvvybgx`
**Database URL**: `postgresql://postgres:Admin@123#Admin@db.xssqhifnabymmsvvybgx.supabase.co:5432/postgres`
**Supabase URL**: `https://xssqhifnabymmsvvybgx.supabase.co`

## 🔧 What I've Configured For You

✅ Updated `config.py` with your Supabase connection  
✅ Updated `.env.example` with your specific settings  
✅ Created automated deployment scripts  
✅ Prepared database setup files  
✅ Fixed UUID casting issues in SQL  

## 🚀 One-Click Deployment Options

### Option 1: Automated Windows Deployment
```powershell
# Run this in PowerShell
.\deploy-vercel.ps1
```

### Option 2: Manual Step-by-Step

#### Step 1: Get Supabase API Keys
1. Go to: https://supabase.com/dashboard/project/xssqhifnabymmsvvybgx/settings/api
2. Copy these values:
   - **Project URL**: `https://xssqhifnabymmsvvybgx.supabase.co` ✅ (already set)
   - **Anon/Public Key**: `eyJhbGciOiJIUzI1NiIsInR5cCI6...`
   - **Service Role Key**: `eyJhbGciOiJIUzI1NiIsInR5cCI6...`

#### Step 2: Setup Database
```powershell
# Automated setup
.\setup-database.ps1

# OR manually copy/paste supabase_setup_simple.sql into Supabase SQL Editor
```

#### Step 3: Create Storage Bucket
1. Go to: https://supabase.com/dashboard/project/xssqhifnabymmsvvybgx/storage/buckets
2. Click **"New bucket"**
3. Name: `papers`
4. Set to **Private**
5. Click **"Create bucket"**

#### Step 4: Deploy to Vercel
```bash
# Install Vercel CLI
npm install -g vercel

# Login to Vercel
vercel login

# Deploy
vercel --prod
```

#### Step 5: Set Environment Variables in Vercel
Add these in your Vercel project settings:

```env
FLASK_CONFIG=vercel
SECRET_KEY=paper-cms-super-secret-key-2025-change-this
SUPABASE_URL=https://xssqhifnabymmsvvybgx.supabase.co
SUPABASE_ANON_KEY=your-anon-key-from-step-1
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key-from-step-1
DATABASE_URL=postgresql://postgres:Admin@123#Admin@db.xssqhifnabymmsvvybgx.supabase.co:5432/postgres
SUPABASE_STORAGE_BUCKET=papers
VERCEL=1
```

## 🎯 Default Login Credentials

After database setup, you can login with:
- **Email**: `admin@paper-cms.com`
- **Password**: `admin123`

**⚠️ IMPORTANT**: Change this password immediately after first login!

## 🔗 Your URLs

- **Supabase Dashboard**: https://supabase.com/dashboard/project/xssqhifnabymmsvvybgx
- **SQL Editor**: https://supabase.com/dashboard/project/xssqhifnabymmsvvybgx/sql
- **Storage**: https://supabase.com/dashboard/project/xssqhifnabymmsvvybgx/storage/buckets
- **API Settings**: https://supabase.com/dashboard/project/xssqhifnabymmsvvybgx/settings/api

## 🛠️ Files Created/Updated

- ✅ `config.py` - Updated with your Supabase connection
- ✅ `.env.example` - Your environment template
- ✅ `deploy-vercel.ps1` - Windows automated deployment
- ✅ `setup-database.ps1` - Windows database setup
- ✅ `supabase_setup_simple.sql` - Fixed SQL without RLS issues
- ✅ `DEPLOYMENT_SUPABASE.md` - This guide

## 🆘 Need Help?

If anything fails:
1. Check your Supabase API keys are correct
2. Ensure the storage bucket `papers` exists
3. Verify all environment variables are set in Vercel
4. Check Vercel deployment logs for any errors

## 🎉 You're All Set!

Everything is configured for your specific Supabase project. Just run the deployment script or follow the manual steps above!