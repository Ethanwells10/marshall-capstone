# Market Monitor - Architecture

## System Overview

Market Monitor is a server-rendered Flask application with client-side interactivity via Chart.js. It follows a traditional MVC pattern with Flask handling both the API and HTML rendering.

```
┌─────────────┐     ┌──────────────────┐     ┌─────────┐
│   Browser   │────>│  Flask (Gunicorn) │────>│  MySQL  │
│ Bootstrap 5 │<────│  Python 3.x       │<────│  8.0    │
│ Chart.js    │     └──────────────────┘     └─────────┘
└─────────────┘              │
                             │ HTTP requests
                    ┌────────┴────────┐
                    │  External APIs  │
                    │ - Alpha Vantage │
                    │ - NewsAPI       │
                    │ - CoinGecko     │
                    └─────────────────┘
```

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.x, Flask |
| Database | MySQL 8.0 |
| Frontend | Bootstrap 5, Chart.js |
| Templating | Jinja2 (Flask templates) |
| Server | Gunicorn behind Nginx |
| Hosting | AWS Lightsail (Ubuntu) |
| CI/CD | GitHub Actions |
| Domain | marshallcapew.xyz (HTTPS via Let's Encrypt) |

## Project Structure

```
marshall-capstone/
├── backend/
│   ├── app/
│   │   ├── __init__.py          # Flask app factory
│   │   ├── models.py            # SQLAlchemy models (or raw SQL)
│   │   ├── routes/
│   │   │   ├── auth.py          # Login, register, logout
│   │   │   ├── watchlists.py    # Watchlist CRUD
│   │   │   ├── stocks.py        # Stock data + charts
│   │   │   ├── notes.py         # User notes CRUD
│   │   │   └── market.py        # Dashboard overview
│   │   ├── services/
│   │   │   ├── alpha_vantage.py # Alpha Vantage API client
│   │   │   ├── news.py          # NewsAPI client
│   │   │   ├── coingecko.py     # CoinGecko API client
│   │   │   └── cache.py         # API response caching
│   │   └── templates/           # Jinja2 HTML templates
│   │       ├── base.html
│   │       ├── login.html
│   │       ├── dashboard.html
│   │       ├── watchlist.html
│   │       ├── stock.html
│   │       └── notes.html
│   ├── requirements.txt
│   ├── config.py
│   └── run.py                   # Entry point
├── frontend/                    # Static assets (if separated)
├── docs/
│   ├── project-proposal.md
│   ├── api-design.md
│   ├── database-schema.md
│   └── architecture.md
├── CLAUDE.md
├── README.md
└── .github/
    └── workflows/
        └── deploy.yml
```

## Deployment Flow

1. Developer pushes to `main` branch on GitHub
2. GitHub Actions workflow triggers:
   - Installs Python dependencies
   - Runs any tests
   - SSHs into Lightsail instance
   - Copies updated code
   - Restarts Gunicorn service
3. Nginx reverse-proxies requests to Gunicorn
4. HTTPS handled by Let's Encrypt / Certbot

## Key Design Decisions

- **Server-rendered with Jinja2** rather than a separate SPA frontend. Simpler deployment, fewer moving parts, and Bootstrap 5 provides a clean responsive UI.
- **API caching in MySQL** to stay within free-tier rate limits. The `api_cache` table stores serialized JSON responses with expiration timestamps.
- **Session-based auth** via Flask sessions rather than JWT tokens. Simpler for a server-rendered app.
- **Gunicorn + Nginx** is the standard production Flask deployment pattern.
