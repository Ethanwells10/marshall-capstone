# Market Monitor - Project Proposal

**Author:** Ethan Wells
**Date:** March 2026
**Stack:** Python/Flask + MySQL + Bootstrap 5 + Chart.js
**Deployment:** AWS Lightsail with GitHub Actions CI/CD

---

## Project Name

Market Monitor

## Target Audience

- Retail investors who want a lightweight, free alternative to paid platforms (Bloomberg Terminal, TradingView Pro)
- Finance students learning about markets and portfolio tracking
- Anyone who wants to organize stock research with watchlists and personal notes

## Problem Statement

Retail investors and finance students lack a simple, free tool to track stocks, organize watchlists, and view market data in one place. Existing platforms are either expensive (Bloomberg, TradingView Pro) or cluttered with features that overwhelm casual users.

## Value Proposition

**My app helps retail investors and finance students to track and research stocks by providing a clean, free dashboard with watchlists, interactive charts, and market news -- all powered by free APIs.**

---

## Must-Have Features (MVP)

1. **User Authentication** - Register, login, logout with secure password hashing. Session-based auth so users see only their own data.

2. **Watchlist Management** - Users can create, rename, and delete named watchlists. Add/remove stock tickers to any watchlist. View live quotes (price, change, volume) for all tickers in a watchlist.

3. **Stock Detail Page** - View detailed info for any ticker: company profile (sector, industry, exchange), interactive Chart.js price chart with multiple timeframes (1W, 1M, 3M, 1Y), and related financial news headlines.

4. **Market Dashboard** - Homepage showing an overview of major indices (SPY, QQQ, DIA) and cryptocurrency prices (BTC, ETH, ADA) via CoinGecko. Quick snapshot of market conditions on login.

5. **Research Notes** - Users can attach personal notes to any stock ticker. Create, edit, and delete notes. Notes are private to each user.

## Explicitly NOT Building (Out of Scope)

- **Portfolio tracking with buy/sell transactions** - No trade logging, P&L calculations, or portfolio performance metrics. This is a watchlist and research tool, not a brokerage.
- **Real-time WebSocket streaming** - All data is fetched on page load or user action. No live-updating tickers or push notifications.
- **Social features** - No sharing watchlists, no public profiles, no comments or community features.
- **Mobile app** - Web-only. Bootstrap 5 provides responsive design, but there is no native iOS/Android app.
- **Algorithmic trading or alerts** - No price alerts, no automated buy/sell signals, no backtesting.

---

## Pages and User Flow

### Pages

| Page | Route | Description |
|------|-------|-------------|
| Landing / Login | `/` | Login form. Link to register. Redirects to dashboard if already logged in. |
| Register | `/register` | Registration form (email, password, confirm password). |
| Dashboard | `/dashboard` | Market overview: major index ETFs, crypto prices. List of user's watchlists with quick links. |
| Watchlist View | `/watchlist/<id>` | Shows all tickers in a watchlist with live quotes. Buttons to add/remove tickers. |
| Stock Detail | `/stock/<symbol>` | Company info, interactive price chart, news headlines, user's notes for this ticker. |
| Notes | `/notes` | All of the user's research notes across all tickers, sortable by date or ticker. |

### User Flow

1. User lands on `/` and logs in (or registers at `/register`)
2. After login, redirected to `/dashboard` showing market overview and their watchlists
3. User clicks a watchlist to see `/watchlist/<id>` with live quotes
4. User clicks a ticker to see `/stock/<symbol>` with charts, news, and notes
5. User can add notes on the stock detail page or view all notes at `/notes`
6. User can create new watchlists or manage existing ones from the dashboard

---

## External APIs (All Free Tier)

| API | Purpose | Rate Limit | Auth |
|-----|---------|------------|------|
| Alpha Vantage | Stock quotes, company profiles, historical prices | 25 requests/day | API key |
| NewsAPI | Financial news headlines by ticker | 100 requests/day | API key |
| CoinGecko | Cryptocurrency prices (BTC, ETH, ADA) | ~30 requests/min | No key required |

### Caching Strategy

Given Alpha Vantage's strict 25 req/day limit, the app will cache API responses in MySQL:
- Stock quotes cached with a timestamp; re-fetched only if older than 15 minutes
- Company profiles cached indefinitely (rarely change)
- Historical price data cached per timeframe; re-fetched only if older than 24 hours
- News headlines cached for 1 hour
- Crypto prices cached for 5 minutes (higher rate limit allows more frequent updates)
