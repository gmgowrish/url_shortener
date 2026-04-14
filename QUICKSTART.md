# Quick Start Guide

Get your URL shortener running in 5 minutes!

## Option 1: Docker (Recommended)

```bash
# Clone and enter directory
git clone https://github.com/yourusername/url-shortener.git
cd url-shortener

# Start all services (PostgreSQL, Redis, Backend, Frontend)
docker-compose up -d

# Done! Visit:
# - Frontend: http://localhost:3000
# - Backend: http://localhost:8000
# - API Docs: http://localhost:8000/api/docs/
```

## Option 2: Manual Setup

### Backend
```bash
cd backend
cp .env.example .env
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

### Frontend (new terminal)
```bash
cd frontend
cp .env.example .env.local
npm install
npm run dev
```

## Create Your First Short URL

1. Register at http://localhost:3000/register
2. Login at http://localhost:3000/login
3. Paste a long URL and click "Shorten"
4. Copy your short link and share!

## Next Steps

- [Full Documentation](README.md)
- [Deploy to Production](docs/DEPLOYMENT.md)
- [Setup Monitoring](docs/MONITORING.md)
