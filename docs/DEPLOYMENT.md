# Production Deployment Guide

Step-by-step guide to deploy your URL shortener for free.

## Prerequisites

- GitHub account
- Render account (free tier)
- Vercel account (free tier)
- Domain name (optional, can use subdomains)

---

## Part 1: Deploy Backend to Render

### Step 1: Prepare Database

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click **New** → **PostgreSQL**
3. Configure:
   - **Name**: `urlshortener-db`
   - **Region**: Oregon (or closest to you)
   - **Plan**: Free
   - **Database Name**: `urlshortener`
4. Click **Create Database**
5. **Save the connection string** (shown after creation)

### Step 2: Create Redis Cache

1. Click **New** → **Redis**
2. Configure:
   - **Name**: `urlshortener-redis`
   - **Region**: Same as database
   - **Plan**: Free
3. Click **Create**
4. **Save the Redis URL**

### Step 3: Deploy Django Backend

1. Click **New** → **Web Service**
2. Connect your GitHub repository
3. Configure:

| Field | Value |
|-------|-------|
| **Name** | `urlshortener-api` |
| **Region** | Same as database |
| **Branch** | `main` |
| **Root Directory** | `backend` |
| **Runtime** | `Python 3` |
| **Build Command** | `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate` |
| **Start Command** | `gunicorn config.wsgi:application --bind 0.0.0.0:$PORT` |
| **Instance Type** | Free |

4. **Environment Variables** - Add these:

```env
SECRET_KEY=<generate-random-string>
DEBUG=False
DATABASE_URL=<paste-from-step-1>
REDIS_URL=<paste-from-step-2>
ALLOWED_HOSTS=*
CORS_ALLOWED_ORIGINS=https://your-app.vercel.app
BASE_URL=https://urlshortener-api.onrender.com
SECURE_SSL_REDIRECT=True
```

5. Click **Create Web Service**
6. Wait for deployment (5-10 minutes)
7. Test: Visit `https://urlshortener-api.onrender.com/health/`

### Step 4: Configure Static Files

Render needs a disk for static files:

1. Go to your service → **Disks**
2. Click **Add Disk**
3. Configure:
   - **Mount Path**: `/app/staticfiles`
   - **Size**: 1 GB (free tier max)

---

## Part 2: Deploy Frontend to Vercel

### Step 1: Connect Repository

1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Click **Add New** → **Project**
3. Import your GitHub repository
4. Configure:

| Field | Value |
|-------|-------|
| **Framework Preset** | Next.js |
| **Root Directory** | `frontend` |
| **Build Command** | `npm run build` |
| **Output Directory** | `.next` |

### Step 2: Environment Variables

Click **Environment Variables** → **Add Variable**:

```env
NEXT_PUBLIC_API_URL=https://urlshortener-api.onrender.com/api
```

### Step 3: Deploy

1. Click **Deploy**
2. Wait for build (2-3 minutes)
3. Visit your app: `https://your-app.vercel.app`

---

## Part 3: Update CORS Settings

After frontend is deployed:

1. Go to Render Dashboard → Backend service
2. **Environment** → **Edit**
3. Update `CORS_ALLOWED_ORIGINS`:
   ```env
   CORS_ALLOWED_ORIGINS=https://your-app.vercel.app,https://your-app-username.vercel.app
   ```
4. Save → Service will redeploy

---

## Part 4: Custom Domain (Optional)

### Backend (Render)

1. Go to service → **Settings**
2. Scroll to **Custom Domain**
3. Click **Add Custom Domain**
4. Enter: `api.yourdomain.com`
5. Update DNS (in your domain registrar):
   ```
   Type: CNAME
   Name: api
   Value: urlshortener-api.onrender.com
   ```
6. Enable **Auto-SSL** after DNS propagates

### Frontend (Vercel)

1. Go to project → **Settings** → **Domains**
2. Add: `yourdomain.com` and `www.yourdomain.com`
3. Update DNS:
   ```
   Type: CNAME
   Name: www
   Value: cname.vercel-dns.com

   Type: A
   Name: @
   Value: 76.76.21.21
   ```
4. Vercel auto-configures SSL

---

## Part 5: Post-Deployment Checklist

### Backend Tests

```bash
# Test health endpoint
curl https://your-api.onrender.com/health/

# Test API docs
curl https://your-api.onrender.com/api/docs/

# Test redirect (create a link first via API)
curl -X POST https://your-api.onrender.com/api/links/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"original_url": "https://example.com"}'
```

### Frontend Tests

1. Visit your Vercel URL
2. Try registering a new account
3. Create a short link
4. Test the redirect
5. Check analytics dashboard

### Monitoring

1. Set up [Uptime Robot](./MONITORING.md) for health checks
2. Bookmark Render dashboard for logs
3. Enable GitHub Actions notifications

---

## Troubleshooting

### Backend Issues

**"Service Unavailable"**
- Check Render logs for errors
- Verify database connection string
- Ensure migrations ran successfully

**CORS Errors**
- Double-check `CORS_ALLOWED_ORIGINS` includes your Vercel URL
- Include both `vercel.app` variants

**Database Connection Failed**
- Verify `DATABASE_URL` is correct
- Check database is in same region
- Ensure database is not paused (Render free tier)

### Frontend Issues

**"Failed to fetch" errors**
- Check `NEXT_PUBLIC_API_URL` is correct
- Verify backend is running (check health endpoint)
- Check browser console for CORS errors

**Build fails**
- Ensure `package.json` is in `frontend/` directory
- Check Node version (should be 20+)

---

## Cost Summary

| Service | Plan | Cost |
|---------|------|------|
| Render Web Service | Free | $0/mo |
| Render PostgreSQL | Free | $0/mo |
| Render Redis | Free | $0/mo |
| Vercel | Hobby | $0/mo |
| GitHub Actions | Free | $0/mo |
| **Total** | | **$0/mo** |

### Free Tier Limits

- **Render**: Service sleeps after 15 min inactivity (30s cold start)
- **PostgreSQL**: 1 GB storage, deleted after 90 days inactive
- **Redis**: 25 MB memory
- **Vercel**: Unlimited deployments, 100 GB bandwidth/month

---

## Updating After Code Changes

### Automatic Deployment

Both Render and Vercel auto-deploy on push to `main`:

```bash
git add .
git commit -m "feat: added new feature"
git push origin main
```

- Backend: Deploys in 3-5 minutes
- Frontend: Deploys in 1-2 minutes

### Manual Redeploy

**Render**: Dashboard → Service → **Manual Deploy** → Deploy latest commit

**Vercel**: Project → **Redeploy** (dropdown on latest deployment)

---

## Next Steps

1. Set up monitoring (see [MONITORING.md](./MONITORING.md))
2. Add your project to resume with live URL
3. Create demo video/screenshots
4. Add README badges for build status

Good luck with your job search! 🚀
