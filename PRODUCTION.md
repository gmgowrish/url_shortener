# Production Configuration Guide

## Overview

Your URL shortener is now configured for production deployment. The app uses environment variables for all configuration, making it easy to deploy to any platform (Vercel, Render, AWS, etc.).

## Environment Variables

### Frontend (.env.local or Vercel environment variables)

```env
# API URL - change this for production
NEXT_PUBLIC_API_URL=https://your-api-domain.com/api
```

### Backend (.env or Render environment variables)

```env
# Django settings
SECRET_KEY=your-secret-key-here
DEBUG=False

# Hosts and CORS
ALLOWED_HOSTS=yourdomain.com,api.yourdomain.com
CORS_ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Database
DATABASE_URL=postgresql://user:pass@host:5432/dbname

# Redis
REDIS_URL=redis://host:port/db

# URL settings
BASE_URL=https://yourdomain.com

# Security (production)
SECURE_SSL_REDIRECT=True
```

## Deployment Options

### Option 1: Vercel + Render (Free)
- **Frontend**: Vercel (free tier)
- **Backend**: Render (free tier)
- **Database**: Render PostgreSQL (free tier)
- **Cache**: Render Redis (free tier)

### Option 2: Railway (All-in-one)
- Single platform deployment
- PostgreSQL and Redis included
- Easy scaling

### Option 3: AWS/DigitalOcean
- Full control
- Better performance
- Paid services

## Production Checklist

- [ ] Change SECRET_KEY to a random string
- [ ] Set DEBUG=False
- [ ] Configure ALLOWED_HOSTS for your domain
- [ ] Set CORS_ALLOWED_ORIGINS for your frontend domain
- [ ] Update BASE_URL to your production domain
- [ ] Enable SSL/HTTPS
- [ ] Set up monitoring (logs, metrics)
- [ ] Configure backups for database

## Mobile Access

The app now works on all devices because:
- No hardcoded IP addresses
- Environment-based configuration
- Proper CORS settings
- Domain-based URLs instead of IPs

## Testing Production

1. Deploy backend first
2. Update frontend API_URL
3. Deploy frontend
4. Test login and link creation
5. Test QR codes from mobile devices

See `docs/DEPLOYMENT.md` for detailed deployment instructions.