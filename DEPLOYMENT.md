# 🚀 Quick Deployment Guide: Paper-CMS to Supabase + Vercel

## Prerequisites
- GitHub account
- Vercel account
- Supabase account

## Step-by-Step Deployment

### 1. Setup Supabase (5 minutes)

1. Go to [supabase.com](https://supabase.com) and create a new project
2. Wait for project to be ready
3. Go to **Settings > API** and copy:
   - Project URL
   - Anon/Public key
   - Service role key
4. Go to **Settings > Database** and copy the connection string
5. Go to **SQL Editor** and run the contents of `supabase_setup.sql`
6. Go to **Storage** and create a bucket named `papers`

### 2. Prepare Your Code

1. Push your code to GitHub
2. Make sure all files are committed including:
   - `vercel.json`
   - `runtime.txt`
   - `requirements.txt`
   - `supabase_setup.sql`

### 3. Deploy to Vercel (3 minutes)

1. Go to [vercel.com](https://vercel.com) and import your GitHub repo
2. Configure project:
   - Framework Preset: **Other**
   - Build Command: (leave empty)
   - Output Directory: (leave empty)
   - Install Command: `pip install -r requirements.txt`

3. Add Environment Variables:
   ```
   FLASK_CONFIG=vercel
   SECRET_KEY=your-super-secret-key-change-this
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_ANON_KEY=your-anon-key-here
   SUPABASE_SERVICE_ROLE_KEY=your-service-role-key-here
   DATABASE_URL=postgresql://postgres:password@db.your-project.supabase.co:5432/postgres
   SUPABASE_STORAGE_BUCKET=papers
   VERCEL=1
   ```

4. Click **Deploy**

### 4. Test Your Deployment

1. Visit your Vercel URL
2. Register a new account or login with:
   - Email: `admin@paper-cms.com`
   - Password: `admin123`
3. Test paper submission
4. Test file upload

## 🎉 You're Done!

Your Paper-CMS is now live with:
- ✅ PostgreSQL database (Supabase)
- ✅ File storage (Supabase Storage)
- ✅ Serverless hosting (Vercel)
- ✅ SSL certificate (automatic)
- ✅ Global CDN (automatic)

## Next Steps

1. **Custom Domain**: Add your domain in Vercel dashboard
2. **Email Setup**: Configure SMTP settings for notifications
3. **Analytics**: Add Vercel Analytics
4. **Monitoring**: Set up error tracking

## Need Help?

- Check Vercel deployment logs
- Verify Supabase connection in dashboard
- Ensure all environment variables are set correctly
- Review the full README for detailed configuration options

## Security Notes

1. Change the default admin password immediately
2. Generate a strong SECRET_KEY
3. Review Supabase RLS policies
4. Set up proper storage bucket policies
5. Enable 2FA on Vercel and Supabase accounts