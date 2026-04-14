# URL Shortener Service

A production-ready URL shortener with analytics, built with Django REST Framework and Next.js. Designed to showcase **Backend + DevOps** skills.

![Python](https://img.shields.io/badge/Python-3.11-blue)
![Django](https://img.shields.io/badge/Django-5.0-green)
![Next.js](https://img.shields.io/badge/Next.js-14-black)
![Docker](https://img.shields.io/badge/Docker-✓-blue)
![License](https://img.shields.io/badge/License-MIT-yellow)

## Features

- **URL Shortening** - Generate short URLs with custom slugs
- **Analytics Dashboard** - Track clicks, unique visitors, and referrers
- **QR Code Generation** - Auto-generated QR codes for each link
- **Link Expiration** - Set expiration dates for links
- **Rate Limiting** - API protection with Redis-backed rate limiting
- **JWT Authentication** - Secure token-based auth
- **Redis Caching** - Hot URL caching for performance
- **Docker Support** - Full containerization for local dev
- **CI/CD** - GitHub Actions workflows for automated testing & deployment

## Tech Stack

### Backend
- **Django 5** + Django REST Framework
- **PostgreSQL** - Primary database
- **Redis** - Caching & rate limiting
- **Gunicorn** - WSGI server
- **WhiteNoise** - Static file serving
- **drf-spectacular** - OpenAPI/Swagger docs

### Frontend
- **Next.js 14** (App Router)
- **React Query** - Data fetching
- **Tailwind CSS** - Styling
- **QRCode React** - QR generation

### DevOps
- **Docker** + Docker Compose
- **GitHub Actions** - CI/CD
- **Render** - Backend hosting
- **Vercel** - Frontend hosting

## Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.11+ (for local dev without Docker)
- Node.js 20+ (for local frontend dev)

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/url-shortener.git
cd url-shortener
```

### 2. Local Development with Docker

```bash
# Start all services
docker-compose up -d

# Backend will be available at http://localhost:8000
# Frontend will be available at http://localhost:3000
# PostgreSQL on localhost:5432
# Redis on localhost:6379
```

### 3. Local Development without Docker

**Backend:**
```bash
cd backend
cp .env.example .env
# Edit .env with your settings
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

**Frontend:**
```bash
cd frontend
cp .env.example .env.local
npm install
npm run dev
```

## API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/api/docs/
- **OpenAPI Schema**: http://localhost:8000/api/schema/

### Key Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/token/` | Get JWT token |
| POST | `/api/accounts/register/` | Register user |
| GET | `/api/links/` | List user's links |
| POST | `/api/links/` | Create short link |
| GET | `/api/links/{id}/` | Get link details |
| DELETE | `/api/links/{id}/` | Delete link |
| GET | `/api/analytics/summary/` | Analytics summary |
| GET | `/api/analytics/link/{id}/` | Link analytics |
| GET | `/{short_code}/` | Redirect to original URL |
| GET | `/{short_code}/qr/` | Get QR code (SVG) |

## Deployment

### Backend (Render)

1. Create a new **Web Service** on [Render](https://render.com)
2. Connect your GitHub repository
3. Set root directory to `backend`
4. Add environment variables (see `.env.example`)
5. Deploy!

Or use the blueprint:
```bash
# Install Render CLI
npm install -g @render-cloud/cli

# Push configuration
render-cli push
```

### Frontend (Vercel)

1. Import project to [Vercel](https://vercel.com)
2. Set root directory to `frontend`
3. Add environment variable: `NEXT_PUBLIC_API_URL`
4. Deploy!

### Environment Variables

**Backend (.env):**
```env
SECRET_KEY=your-secret-key
DEBUG=False
DATABASE_URL=postgresql://...
REDIS_URL=redis://...
ALLOWED_HOSTS=your-domain.com
CORS_ALLOWED_ORIGINS=https://your-frontend.vercel.app
BASE_URL=https://your-api.onrender.com
```

**Frontend (.env.local):**
```env
NEXT_PUBLIC_API_URL=https://your-api.onrender.com/api
```

## Monitoring

### Health Checks
- **Health**: `GET /health/`
- **Readiness**: `GET /ready/`
- **Metrics**: `GET /metrics/` (Prometheus format)

### Uptime Monitoring

Set up free monitoring with [Uptime Robot](https://uptimerobot.com):
1. Create account (free)
2. Add monitor: `https://your-api.onrender.com/health/`
3. Set interval: 5 minutes
4. Get email/SMS alerts on downtime

### Logs

- **Render Dashboard**: View real-time logs
- **Vercel Functions**: Logs in Deployment details

## Testing

```bash
# Backend tests
cd backend
pytest

# With coverage
pytest --cov=. --cov-report=html

# Frontend tests
cd frontend
npm test
```

## Project Structure

```
url-shortener/
├── backend/
│   ├── config/          # Django settings & URLs
│   ├── accounts/        # User authentication
│   ├── links/           # URL shortening logic
│   ├── analytics/       # Click tracking
│   ├── api/             # Shared API utilities
│   ├── Dockerfile
│   ├── requirements.txt
│   └── manage.py
├── frontend/
│   ├── src/
│   │   ├── app/         # Next.js pages
│   │   ├── components/  # React components
│   │   └── lib/         # API utilities
│   ├── Dockerfile
│   └── package.json
├── .github/workflows/   # CI/CD pipelines
├── docker-compose.yml   # Local development
├── render.yaml          # Render blueprint
└── README.md
```

## Security

- ✅ JWT token authentication
- ✅ CORS configured for production
- ✅ Rate limiting (100/hour anon, 1000/hour auth)
- ✅ HTTPS enforced in production
- ✅ Environment variables (no secrets in code)
- ✅ SQL injection protection (Django ORM)
- ✅ XSS protection (Django templates)

## Free Tier Limitations

| Service | Free Tier | Notes |
|---------|-----------|-------|
| Render | Free web service | Spins down after 15min idle |
| PostgreSQL | 1GB storage | 90 days inactive = deleted |
| Redis | 25MB | Sufficient for caching |
| Vercel | Unlimited | Hobby tier is generous |

## Resume Highlights

This project demonstrates:

1. **Backend Engineering**
   - RESTful API design with DRF
   - Database modeling (PostgreSQL)
   - Caching strategies (Redis)
   - Authentication (JWT)

2. **DevOps Skills**
   - Containerization (Docker)
   - CI/CD pipelines (GitHub Actions)
   - Cloud deployment (Render, Vercel)
   - Monitoring & health checks

3. **Production Readiness**
   - Security best practices
   - Rate limiting
   - Error handling
   - API documentation

## License

MIT License - feel free to use for your portfolio!

## Support

For issues or questions, open a GitHub issue.

---

Built with ❤️ for portfolio demonstration
