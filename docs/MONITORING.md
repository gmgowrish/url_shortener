# Monitoring Setup (Free Tier)

This guide shows how to set up monitoring for your URL shortener without any cost.

## 1. Render Dashboard (Built-in)

Render provides free monitoring for all services:

### Access Dashboard
1. Go to [dashboard.render.com](https://dashboard.render.com)
2. Select your service
3. View tabs:
   - **Logs**: Real-time application logs
   - **Metrics**: CPU, Memory, Request count
   - **Events**: Deployments and incidents

### Key Metrics Available
- Request latency (p50, p95, p99)
- Error rate (4xx, 5xx)
- CPU utilization
- Memory usage

## 2. Uptime Robot (External Monitoring)

Free uptime monitoring with alerts.

### Setup
1. Sign up at [uptimerobot.com](https://uptimerobot.com) (free)
2. Click "Add New Monitor"
3. Configure:
   - **Monitor Type**: HTTP(s)
   - **Friendly Name**: URL Shortener API
   - **URL**: `https://your-api.onrender.com/health/`
   - **Monitoring Interval**: 5 minutes (free tier)

### Alert Contacts
Configure how you want to be notified:
- Email (free)
- SMS (paid, skip for free tier)
- Push notifications via mobile app (free)

### Status Page (Optional)
Create a public status page:
1. Go to "Status Pages" → "Create Status Page"
2. Add your monitors
3. Share the public URL

## 3. Better Stack (Log Management)

Free tier: 10,000 logs/month

### Setup
1. Sign up at [betterstack.com](https://betterstack.com)
2. Create new project
3. Get your **Source Token**
4. Add to Render environment variables:
   ```env
   BETTER_STACK_TOKEN=your-token
   ```

### Django Integration
Install the logger:
```bash
pip install python-json-logger
```

Add to `settings.py`:
```python
LOGGING = {
    'version': 1,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'json',
        },
    },
    'formatters': {
        'json': {
            '()': 'pythonjsonlogger.jsonlogger.JsonFormatter',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}
```

## 4. Grafana Cloud (Advanced Metrics)

Free tier: 10,000 samples/minute

### Setup
1. Sign up at [grafana.com](https://grafana.com)
2. Create new stack
3. Get credentials from **Connections** → **Prometheus**

### Django Integration
```bash
pip install prometheus-client
```

Add to `settings.py`:
```python
INSTALLED_APPS += ['django_prometheus']

MIDDLEWARE = [
    'django_prometheus.middleware.PrometheusBeforeMiddleware',
    # ... other middleware
    'django_prometheus.middleware.PrometheusAfterMiddleware',
]
```

Expose metrics at `/metrics/` endpoint (already configured).

## 5. GitHub Actions Status

Monitor your CI/CD:

1. Go to repository **Actions** tab
2. Enable workflows if disabled
3. Set up status badges in README:

```markdown
![Backend CI](https://github.com/username/url-shortener/actions/workflows/backend-ci.yml/badge.svg)
![Frontend CI](https://github.com/username/url-shortener/actions/workflows/frontend-ci.yml/badge.svg)
```

## Recommended Free Stack

For a complete free monitoring setup:

| Need | Tool | Free Limit |
|------|------|------------|
| Application Logs | Render Dashboard | Unlimited |
| Uptime Monitoring | Uptime Robot | 50 monitors |
| Metrics Dashboard | Render Metrics | Basic (free) |
| Error Alerts | Uptime Robot Email | Unlimited |
| Log Aggregation | Better Stack | 10K logs/month |

## Health Check Endpoints

Your API has built-in health endpoints:

| Endpoint | Purpose |
|----------|---------|
| `/health/` | Liveness probe (returns 200 if running) |
| `/ready/` | Readiness probe (returns 200 if ready) |
| `/metrics/` | Prometheus metrics |

## Setting Up Alerts

### Uptime Robot Alerts
1. Go to "Alert Contacts"
2. Add email address
3. Create "Alert Policy":
   - Trigger: Monitor goes DOWN
   - Notify: Your email
   - Check interval: 5 min

### Render Alerts
Render sends email notifications for:
- Failed deployments
- Service crashes
- Database backups

Configure in **Notifications** settings.

## Dashboard Example

Create a simple status page in your README:

```markdown
## Status

- API: ![API Status](https://img.shields.io/website?label=API&url=https://your-api.onrender.com/health/)
- Frontend: ![Frontend Status](https://img.shields.io/website?label=Frontend&url=https://your-app.vercel.app/)
- Uptime: [View Status Page](https://stats.uptimerobot.com/your-id)
```

## Troubleshooting

### "Service Unavailable" on Render
- Check logs for errors
- Verify database connection
- Ensure all migrations ran

### No metrics showing
- Wait 5-10 minutes for data
- Check if health endpoint is accessible
- Verify CORS settings

### Logs not appearing
- Ensure LOGGING config is correct
- Check Render dashboard for real-time logs
