# Market Monitor - Database Schema

**Database:** MySQL 8.0
**Tables:** 5 core tables + 1 cache table
**Foreign Keys:** 4 relationships with CASCADE deletes

---

## Entity Relationship Overview

```
users 1──M watchlists 1──M watchlist_items M──1 tickers
  |                                                |
  └──────────────── user_notes ────────────────────┘
```

- Users own watchlists (one-to-many)
- Watchlists contain tickers via watchlist_items junction table (many-to-many)
- Users write notes on tickers (many-to-many)

---

## Table Definitions

### users

| Column | Type | Constraints |
|--------|------|-------------|
| id | INT | PRIMARY KEY, AUTO_INCREMENT |
| email | VARCHAR(255) | UNIQUE, NOT NULL |
| password_hash | VARCHAR(255) | NOT NULL |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP |

### tickers

| Column | Type | Constraints |
|--------|------|-------------|
| symbol | VARCHAR(10) | PRIMARY KEY |
| name | VARCHAR(255) | |
| exchange | VARCHAR(50) | |
| sector | VARCHAR(100) | |
| industry | VARCHAR(100) | |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP |

### watchlists

| Column | Type | Constraints |
|--------|------|-------------|
| id | INT | PRIMARY KEY, AUTO_INCREMENT |
| user_id | INT | FK -> users(id) ON DELETE CASCADE, NOT NULL |
| name | VARCHAR(100) | NOT NULL |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP |

**Unique constraint:** `UNIQUE(user_id, name)` -- a user cannot have two watchlists with the same name.

### watchlist_items

| Column | Type | Constraints |
|--------|------|-------------|
| id | INT | PRIMARY KEY, AUTO_INCREMENT |
| watchlist_id | INT | FK -> watchlists(id) ON DELETE CASCADE, NOT NULL |
| ticker_symbol | VARCHAR(10) | FK -> tickers(symbol) ON DELETE CASCADE, NOT NULL |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP |

**Unique constraint:** `UNIQUE(watchlist_id, ticker_symbol)` -- a ticker can only appear once per watchlist.

### user_notes

| Column | Type | Constraints |
|--------|------|-------------|
| id | INT | PRIMARY KEY, AUTO_INCREMENT |
| user_id | INT | FK -> users(id) ON DELETE CASCADE, NOT NULL |
| ticker_symbol | VARCHAR(10) | FK -> tickers(symbol) ON DELETE CASCADE, NOT NULL |
| note_text | TEXT | NOT NULL |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP |

### api_cache

| Column | Type | Constraints |
|--------|------|-------------|
| id | INT | PRIMARY KEY, AUTO_INCREMENT |
| cache_key | VARCHAR(255) | UNIQUE, NOT NULL |
| cache_data | JSON | NOT NULL |
| cached_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP |
| expires_at | TIMESTAMP | NOT NULL |

This table stores cached API responses to stay within free-tier rate limits. The `cache_key` encodes the API source and parameters (e.g., `alphavantage:quote:AAPL`). Application logic checks `expires_at` before serving cached data.

---

## SQL Schema

```sql
CREATE DATABASE IF NOT EXISTS market_monitor;
USE market_monitor;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE tickers (
    symbol VARCHAR(10) PRIMARY KEY,
    name VARCHAR(255),
    exchange VARCHAR(50),
    sector VARCHAR(100),
    industry VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE watchlists (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE(user_id, name)
);

CREATE TABLE watchlist_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    watchlist_id INT NOT NULL,
    ticker_symbol VARCHAR(10) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (watchlist_id) REFERENCES watchlists(id) ON DELETE CASCADE,
    FOREIGN KEY (ticker_symbol) REFERENCES tickers(symbol) ON DELETE CASCADE,
    UNIQUE(watchlist_id, ticker_symbol)
);

CREATE TABLE user_notes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    ticker_symbol VARCHAR(10) NOT NULL,
    note_text TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (ticker_symbol) REFERENCES tickers(symbol) ON DELETE CASCADE
);

CREATE TABLE api_cache (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cache_key VARCHAR(255) UNIQUE NOT NULL,
    cache_data JSON NOT NULL,
    cached_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL
);
```
