# Vercel Environment Variables Setup

## Required Environment Variables for Paper-CMS

Add these environment variables in your Vercel dashboard:

### 1. Go to Vercel Dashboard
- Visit: https://vercel.com/dashboard
- Select your Paper-CMS project
- Go to Settings → Environment Variables

### 2. Add These Variables:

**DATABASE_URL**
```
postgresql://postgres:Admin%40123%23Admin@db.xssqhifnabymmsvvybgx.supabase.co:5432/postgres
```

**SUPABASE_URL**
```
https://xssqhifnabymmsvvybgx.supabase.co
```

**SUPABASE_ANON_KEY**
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inhzc3FoaWZuYWJ5bW1zdnZ5Ymd4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Mjg5Njk2NzgsImV4cCI6MjA0NDU0NTY3OH0.Rcp_1T6oD8raqg7Ol9-rDlk3JJVOZfFyFAGHrM6K8YI
```

**SECRET_KEY**
```
paper-cms-super-secret-key-2025-production
```

**FLASK_ENV**
```
production
```

### 3. Redeploy
After adding these variables, redeploy your application.

### Note about PASSWORD ENCODING:
- Original password: `Admin@123#Admin`
- URL-encoded: `Admin%40123%23Admin`
- @ becomes %40
- # becomes %23