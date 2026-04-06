-- Sample tickers
INSERT IGNORE INTO tickers (symbol, name, exchange, sector, industry) VALUES
('AAPL', 'Apple Inc.', 'NASDAQ', 'Technology', 'Consumer Electronics');
INSERT IGNORE INTO tickers (symbol, name, exchange, sector, industry) VALUES
('MSFT', 'Microsoft Corporation', 'NASDAQ', 'Technology', 'Software');
INSERT IGNORE INTO tickers (symbol, name, exchange, sector, industry) VALUES
('GOOGL', 'Alphabet Inc.', 'NASDAQ', 'Technology', 'Internet Services');
INSERT IGNORE INTO tickers (symbol, name, exchange, sector, industry) VALUES
('AMZN', 'Amazon.com Inc.', 'NASDAQ', 'Consumer Cyclical', 'Internet Retail');
INSERT IGNORE INTO tickers (symbol, name, exchange, sector, industry) VALUES
('TSLA', 'Tesla Inc.', 'NASDAQ', 'Consumer Cyclical', 'Auto Manufacturers');
INSERT IGNORE INTO tickers (symbol, name, exchange, sector, industry) VALUES
('NVDA', 'NVIDIA Corporation', 'NASDAQ', 'Technology', 'Semiconductors');
INSERT IGNORE INTO tickers (symbol, name, exchange, sector, industry) VALUES
('META', 'Meta Platforms Inc.', 'NASDAQ', 'Technology', 'Social Media');
INSERT IGNORE INTO tickers (symbol, name, exchange, sector, industry) VALUES
('JPM', 'JPMorgan Chase & Co.', 'NYSE', 'Financial Services', 'Banks');
INSERT IGNORE INTO tickers (symbol, name, exchange, sector, industry) VALUES
('V', 'Visa Inc.', 'NYSE', 'Financial Services', 'Credit Services');
INSERT IGNORE INTO tickers (symbol, name, exchange, sector, industry) VALUES
('JNJ', 'Johnson & Johnson', 'NYSE', 'Healthcare', 'Drug Manufacturers');
INSERT IGNORE INTO tickers (symbol, name, exchange, sector, industry) VALUES
('GS', 'Goldman Sachs Group Inc.', 'NYSE', 'Financial Services', 'Capital Markets');
INSERT IGNORE INTO tickers (symbol, name, exchange, sector, industry) VALUES
('BAC', 'Bank of America Corp.', 'NYSE', 'Financial Services', 'Banks');
INSERT IGNORE INTO tickers (symbol, name, exchange, sector, industry) VALUES
('UNH', 'UnitedHealth Group Inc.', 'NYSE', 'Healthcare', 'Health Insurance');
INSERT IGNORE INTO tickers (symbol, name, exchange, sector, industry) VALUES
('XOM', 'Exxon Mobil Corporation', 'NYSE', 'Energy', 'Oil & Gas');
INSERT IGNORE INTO tickers (symbol, name, exchange, sector, industry) VALUES
('DIS', 'Walt Disney Co.', 'NYSE', 'Communication Services', 'Entertainment');

-- Admin user (password: admin123)
INSERT IGNORE INTO users (email, password_hash) VALUES
('admin@marketmonitor.com', 'PLACEHOLDER_HASH');

-- Demo user (password: demo123)
INSERT IGNORE INTO users (email, password_hash) VALUES
('demo@marketmonitor.com', 'DEMO_PLACEHOLDER_HASH');
