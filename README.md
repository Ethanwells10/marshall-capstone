# Market Monitor

A full-stack financial dashboard for retail investors and finance students. Track stocks, manage watchlists, view interactive price charts, and stay informed with market news -- all using free APIs.

## Features

- **User Authentication** - Secure registration and login
- **Watchlist Management** - Create custom watchlists and track stock tickers with live quotes
- **Stock Detail Pages** - Company profiles, interactive Chart.js price charts, and related news
- **Market Dashboard** - Overview of major indices (SPY, QQQ, DIA) and cryptocurrency prices (BTC, ETH, ADA)
- **Research Notes** - Attach personal notes to any stock ticker

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python / Flask |
| Database | MySQL 8.0 |
| Frontend | Bootstrap 5 + Chart.js |
| Templating | Jinja2 |
| Hosting | AWS Lightsail |
| CI/CD | GitHub Actions |

## Project Structure

```
├── backend/          # Flask application
├── frontend/         # Static assets
├── docs/             # Project documentation
│   ├── project-proposal.md
│   ├── api-design.md
│   ├── database-schema.md
│   └── architecture.md
├── CLAUDE.md         # AI assistant context
└── README.md
```

## External APIs

- [Alpha Vantage](https://www.alphavantage.co/) - Stock quotes and historical data
- [NewsAPI](https://newsapi.org/) - Financial news headlines
- [CoinGecko](https://www.coingecko.com/en/api) - Cryptocurrency prices

## Getting Started

```bash
cd backend
pip install -r requirements.txt
python run.py
```

## Deployment

Pushes to `main` trigger automated deployment to AWS Lightsail via GitHub Actions.

Live at: https://marshallcapew.xyz

## Author

Ethan Wells - Marshall University Capstone Project
