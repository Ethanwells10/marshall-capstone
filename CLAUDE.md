# Market Monitor - CLAUDE.md

## Project Overview
Market Monitor is a full-stack financial dashboard for retail investors and finance students. Users track stocks, manage watchlists, view interactive price charts, and read market news.

## Tech Stack
- **Backend:** Python 3.x / Flask
- **Database:** MySQL 8.0
- **Frontend:** Jinja2 templates + Bootstrap 5 + Chart.js
- **Deployment:** AWS Lightsail (Ubuntu), Nginx + Gunicorn, GitHub Actions CI/CD
- **Domain:** marshallcapew.xyz

## Project Structure
- `/backend` - Flask application (routes, models, services, templates)
- `/frontend` - Static assets (CSS, JS) if separated from backend templates
- `/docs` - Project proposal, API design, database schema, architecture
- `/.github/workflows/deploy.yml` - CI/CD pipeline

## Database
- MySQL 8.0 with 6 tables: users, tickers, watchlists, watchlist_items, user_notes, api_cache
- Schema defined in `/docs/database-schema.md`
- All foreign keys use CASCADE deletes

## External APIs (Free Tier)
- **Alpha Vantage** - Stock quotes, company profiles, historical prices (25 req/day)
- **NewsAPI** - Financial news headlines (100 req/day)
- **CoinGecko** - Crypto prices (no key required)
- API responses are cached in the `api_cache` MySQL table to stay within rate limits

## API Design
- All API endpoints prefixed with `/api/`
- Session-based authentication (Flask sessions)
- Full endpoint documentation in `/docs/api-design.md`

## Development Commands
```bash
cd backend
pip install -r requirements.txt
python run.py                  # Run dev server
```

## Deployment
- Push to `main` triggers GitHub Actions
- Actions SSH into Lightsail, copy code, restart Gunicorn
- Nginx handles HTTPS via Let's Encrypt
