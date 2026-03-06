# Market Monitor - API Design

**Base URL:** `https://marshallcapew.xyz/api`
**Auth:** Session-based (Flask session cookies)
**Format:** JSON request/response

---

## Authentication Endpoints

### POST /api/auth/register

Register a new user account.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response (201):**
```json
{
  "message": "Account created successfully",
  "user": { "id": 1, "email": "user@example.com" }
}
```

**Errors:** 400 (missing fields, invalid email), 409 (email already exists)

### POST /api/auth/login

Log in and create a session.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response (200):**
```json
{
  "message": "Login successful",
  "user": { "id": 1, "email": "user@example.com" }
}
```

**Errors:** 401 (invalid credentials)

### POST /api/auth/logout

End the current session.

**Response (200):**
```json
{ "message": "Logged out" }
```

### GET /api/auth/me

Get the currently logged-in user.

**Response (200):**
```json
{
  "user": { "id": 1, "email": "user@example.com" }
}
```

**Errors:** 401 (not logged in)

---

## Watchlist Endpoints

All watchlist endpoints require authentication.

### GET /api/watchlists

Get all watchlists for the current user.

**Response (200):**
```json
{
  "watchlists": [
    { "id": 1, "name": "Tech Stocks", "item_count": 5, "created_at": "2026-03-06T12:00:00Z" },
    { "id": 2, "name": "Dividends", "item_count": 3, "created_at": "2026-03-06T12:00:00Z" }
  ]
}
```

### POST /api/watchlists

Create a new watchlist.

**Request:**
```json
{ "name": "Tech Stocks" }
```

**Response (201):**
```json
{ "id": 1, "name": "Tech Stocks", "created_at": "2026-03-06T12:00:00Z" }
```

**Errors:** 400 (missing name), 409 (duplicate name)

### PUT /api/watchlists/<id>

Rename a watchlist.

**Request:**
```json
{ "name": "Big Tech" }
```

**Response (200):**
```json
{ "id": 1, "name": "Big Tech" }
```

**Errors:** 404 (not found), 409 (duplicate name)

### DELETE /api/watchlists/<id>

Delete a watchlist and all its items.

**Response (200):**
```json
{ "message": "Watchlist deleted" }
```

---

## Watchlist Items Endpoints

### GET /api/watchlists/<id>/items

Get all tickers in a watchlist with live quote data.

**Response (200):**
```json
{
  "watchlist": { "id": 1, "name": "Tech Stocks" },
  "items": [
    {
      "symbol": "AAPL",
      "name": "Apple Inc.",
      "price": 178.50,
      "change": 2.35,
      "change_percent": 1.33,
      "volume": 54321000
    }
  ]
}
```

### POST /api/watchlists/<id>/items

Add a ticker to a watchlist.

**Request:**
```json
{ "symbol": "AAPL" }
```

**Response (201):**
```json
{ "message": "AAPL added to watchlist", "symbol": "AAPL" }
```

**Errors:** 409 (already in watchlist), 400 (invalid symbol)

### DELETE /api/watchlists/<id>/items/<symbol>

Remove a ticker from a watchlist.

**Response (200):**
```json
{ "message": "AAPL removed from watchlist" }
```

---

## Stock Data Endpoints

### GET /api/stocks/<symbol>

Get detailed information for a stock ticker.

**Response (200):**
```json
{
  "symbol": "AAPL",
  "name": "Apple Inc.",
  "exchange": "NASDAQ",
  "sector": "Technology",
  "industry": "Consumer Electronics",
  "quote": {
    "price": 178.50,
    "change": 2.35,
    "change_percent": 1.33,
    "volume": 54321000
  }
}
```

### GET /api/stocks/<symbol>/history?range=1M

Get historical price data for charting.

**Query params:** `range` - one of `1W`, `1M`, `3M`, `1Y` (default: `1M`)

**Response (200):**
```json
{
  "symbol": "AAPL",
  "range": "1M",
  "prices": [
    { "date": "2026-02-06", "close": 172.30 },
    { "date": "2026-02-07", "close": 173.10 }
  ]
}
```

### GET /api/stocks/<symbol>/news

Get recent news headlines for a ticker.

**Response (200):**
```json
{
  "symbol": "AAPL",
  "articles": [
    {
      "title": "Apple Announces New Product Line",
      "source": "Reuters",
      "url": "https://example.com/article",
      "published_at": "2026-03-06T10:00:00Z"
    }
  ]
}
```

---

## Market Overview Endpoints

### GET /api/market/overview

Get current prices for major indices and crypto.

**Response (200):**
```json
{
  "indices": [
    { "symbol": "SPY", "name": "S&P 500 ETF", "price": 512.30, "change_percent": 0.45 },
    { "symbol": "QQQ", "name": "Nasdaq 100 ETF", "price": 438.20, "change_percent": 0.72 },
    { "symbol": "DIA", "name": "Dow Jones ETF", "price": 389.10, "change_percent": 0.21 }
  ],
  "crypto": [
    { "id": "bitcoin", "symbol": "BTC", "price": 67500.00, "change_percent_24h": 1.2 },
    { "id": "ethereum", "symbol": "ETH", "price": 3450.00, "change_percent_24h": -0.5 },
    { "id": "cardano", "symbol": "ADA", "price": 0.62, "change_percent_24h": 2.1 }
  ]
}
```

---

## Notes Endpoints

All notes endpoints require authentication.

### GET /api/notes

Get all notes for the current user.

**Query params:** `symbol` (optional) - filter by ticker

**Response (200):**
```json
{
  "notes": [
    {
      "id": 1,
      "ticker_symbol": "AAPL",
      "note_text": "Strong earnings report Q4. Watch for services revenue growth.",
      "created_at": "2026-03-06T12:00:00Z",
      "updated_at": "2026-03-06T12:00:00Z"
    }
  ]
}
```

### POST /api/notes

Create a new note.

**Request:**
```json
{
  "ticker_symbol": "AAPL",
  "note_text": "Strong earnings report Q4. Watch for services revenue growth."
}
```

**Response (201):**
```json
{
  "id": 1,
  "ticker_symbol": "AAPL",
  "note_text": "Strong earnings report Q4. Watch for services revenue growth.",
  "created_at": "2026-03-06T12:00:00Z"
}
```

### PUT /api/notes/<id>

Update a note.

**Request:**
```json
{ "note_text": "Updated analysis after Q1 earnings call." }
```

**Response (200):**
```json
{
  "id": 1,
  "note_text": "Updated analysis after Q1 earnings call.",
  "updated_at": "2026-03-06T14:00:00Z"
}
```

### DELETE /api/notes/<id>

Delete a note.

**Response (200):**
```json
{ "message": "Note deleted" }
```

---

## Health Check

### GET /api/health

**Response (200):**
```json
{ "status": "ok", "timestamp": "2026-03-06T12:00:00Z" }
```
