-- Sample tickers
INSERT OR IGNORE INTO tickers (symbol, name, exchange, sector, industry) VALUES
('AAPL', 'Apple Inc.', 'NASDAQ', 'Technology', 'Consumer Electronics'),
('MSFT', 'Microsoft Corporation', 'NASDAQ', 'Technology', 'Software'),
('GOOGL', 'Alphabet Inc.', 'NASDAQ', 'Technology', 'Internet Services'),
('AMZN', 'Amazon.com Inc.', 'NASDAQ', 'Consumer Cyclical', 'Internet Retail'),
('TSLA', 'Tesla Inc.', 'NASDAQ', 'Consumer Cyclical', 'Auto Manufacturers'),
('NVDA', 'NVIDIA Corporation', 'NASDAQ', 'Technology', 'Semiconductors'),
('META', 'Meta Platforms Inc.', 'NASDAQ', 'Technology', 'Social Media'),
('JPM', 'JPMorgan Chase & Co.', 'NYSE', 'Financial Services', 'Banks'),
('V', 'Visa Inc.', 'NYSE', 'Financial Services', 'Credit Services'),
('JNJ', 'Johnson & Johnson', 'NYSE', 'Healthcare', 'Drug Manufacturers');

-- Admin user (password: admin123)
INSERT OR IGNORE INTO users (email, password_hash) VALUES
('admin@marketmonitor.com', 'PLACEHOLDER_HASH');
