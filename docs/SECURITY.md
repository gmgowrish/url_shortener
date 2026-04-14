# Security & Secrets Management

This document covers how to manage secrets and secure your URL shortener in production.

---

## 🔐 Never Commit Secrets

### Files to Exclude

These files are in `.gitignore` and should **NEVER** be committed:

```
.env
.env.local
.env.*.local
*.pem
*.key
credentials.json
```

### What Not to Commit

- Database passwords
- API keys
- JWT secrets
- AWS/Cloud credentials
- Service account files

---

## Environment Variables

### Local Development

Create `.env` files from examples:

**Backend:**
```bash
cd backend
cp .env.example .env
# Edit .env with your values (never commit!)
```

**Frontend:**
```bash
cd frontend
cp .env.example .env.local
# Edit .env.local (never commit!)
```

### Production (Render)

Add environment variables in Render Dashboard:

1. Go to service → **Environment**
2. Click **Add Environment Variable**
3. Add each variable individually (more secure than bulk upload)

**Required Variables:**

| Key | Example Value | Notes |
|-----|---------------|-------|
| `SECRET_KEY` | `django-insecure-...` | Generate with `python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'` |
| `DEBUG` | `False` | Always False in prod |
| `DATABASE_URL` | `postgresql://...` | From Render PostgreSQL |
| `REDIS_URL` | `redis://...` | From Render Redis |
| `ALLOWED_HOSTS` | `your-api.onrender.com` | Your domain |
| `CORS_ALLOWED_ORIGINS` | `https://your-app.vercel.app` | Frontend URL |
| `BASE_URL` | `https://your-api.onrender.com` | API base URL |
| `SECURE_SSL_REDIRECT` | `True` | Force HTTPS |

### Production (Vercel)

Add in Vercel Dashboard → Project Settings → Environment Variables:

| Key | Example Value |
|-----|---------------|
| `NEXT_PUBLIC_API_URL` | `https://your-api.onrender.com/api` |

---

## GitHub Secrets

For CI/CD workflows, add secrets in GitHub:

1. Go to repository → **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret**

**Required Secrets:**

| Name | Value | Used In |
|------|-------|---------|
| `RENDER_API_KEY` | Render API token | deploy-backend.yml |
| `RENDER_SERVICE_ID` | Render service ID | deploy-backend.yml |
| `VERCEL_TOKEN` | Vercel token | deploy-frontend.yml |
| `VERCEL_ORG_ID` | Vercel org ID | deploy-frontend.yml |
| `VERCEL_PROJECT_ID` | Vercel project ID | deploy-frontend.yml |

### How to Get These

**Render API Key:**
1. Dashboard → Account Settings → **API Keys**
2. Generate new key

**Vercel Token:**
1. Settings → **Access Tokens**
2. Create new token

**Service/Project IDs:**
- Found in dashboard URL or project settings

---

## Security Features Implemented

### 1. JWT Authentication
- Tokens expire after 1 hour
- Refresh tokens expire after 7 days
- Token rotation enabled

### 2. Rate Limiting
```python
# In settings.py
'DEFAULT_THROTTLE_RATES': {
    'anon': '100/hour',      # Anonymous users
    'user': '1000/hour',     # Authenticated users
    'link_create': '20/hour', # Link creation limit
}
```

### 3. CORS Protection
Only allowed origins can access API:
```python
CORS_ALLOWED_ORIGINS = [
    "https://your-app.vercel.app",
]
```

### 4. HTTPS Enforcement
In production (`DEBUG=False`):
```python
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
```

### 5. Security Headers
Django middleware adds:
- `X-Frame-Options: DENY` (clickjacking protection)
- `X-Content-Type-Options: nosniff`
- `X-XSS-Protection: 1; mode=block`

### 6. Password Validation
```python
AUTH_PASSWORD_VALIDATORS = [
    # Similarity check
    # Minimum length (8 chars)
    # Not common password
    # Not entirely numeric
]
```

---

## Security Checklist

Before deploying to production:

- [ ] Generate new `SECRET_KEY` (not the default)
- [ ] Set `DEBUG = False`
- [ ] Configure `ALLOWED_HOSTS`
- [ ] Set `SECURE_SSL_REDIRECT = True`
- [ ] Add production CORS origins
- [ ] Use strong passwords (min 12 chars)
- [ ] Enable rate limiting
- [ ] Set up monitoring/alerts
- [ ] Test health endpoints
- [ ] Verify HTTPS is working
- [ ] No secrets in code (search for patterns like `key=`, `secret=`)
- [ ] Database backups enabled (Render auto-backs up)

---

## Rotating Secrets

### If a Secret is Leaked

1. **Immediately** revoke/regenerate the leaked secret
2. Update in all environments (Render, Vercel, GitHub)
3. Redeploy services
4. Audit logs for unauthorized access

### Regular Rotation

Recommended schedule:
- API keys: Every 90 days
- JWT secret: Every 30 days (requires user re-login)
- Database passwords: Every 90 days

---

## Monitoring for Security Issues

### Check Logs For

- Multiple failed login attempts (brute force)
- Unusual traffic patterns (DDoS)
- 4xx/5xx error spikes (attacks or bugs)
- Unknown IP addresses accessing admin

### Render Logs

```
Dashboard → Service → Logs
```

Filter by:
- `401` - Failed auth
- `403` - Forbidden access
- `500` - Server errors (potential exploits)

---

## Admin Security

### Protect Admin Endpoint

The Django admin is at `/admin/`. Secure it:

1. **Change default admin URL** (optional):
   ```python
   # urls.py
   path('secret-admin-path/', admin.site.urls)
   ```

2. **Restrict by IP** (advanced):
   ```python
   # Add middleware to check IP for /admin/
   ```

3. **Use strong password** for admin user

### Create Superuser

```bash
# In production (one-time)
heroku run python manage.py createsuperuser
# Or via Render shell
```

---

## Dependency Security

### Keep Dependencies Updated

**Backend:**
```bash
# Check for vulnerabilities
pip-audit

# Update dependencies
pip install --upgrade django djangorestframework
```

**Frontend:**
```bash
# Check for vulnerabilities
npm audit

# Fix automatically
npm audit fix
```

### GitHub Dependabot

Enable automated security updates:

1. Repository → **Settings** → **Code security and analysis**
2. Enable **Dependabot alerts** and **Dependabot security updates**

---

## Incident Response

If you suspect a security breach:

1. **Contain**: Take service offline (Render → Suspend)
2. **Assess**: Check logs for unauthorized access
3. **Rotate**: Change all secrets
4. **Patch**: Fix the vulnerability
5. **Restore**: Redeploy and monitor closely
6. **Document**: Write a post-mortem

---

## Resources

- [Django Security Checklist](https://docs.djangoproject.com/en/stable/topics/security/)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Render Security Best Practices](https://render.com/docs/security)
