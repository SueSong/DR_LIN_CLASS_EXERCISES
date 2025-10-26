-- Trading Agent Database Schema
-- Initialize database with portfolio and transaction tables

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Portfolio table - tracks current holdings
CREATE TABLE portfolio (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id VARCHAR(50) NOT NULL DEFAULT 'default_trader',
    symbol VARCHAR(10) NOT NULL,
    shares DECIMAL(10, 4) NOT NULL DEFAULT 0,
    avg_cost DECIMAL(10, 2) NOT NULL DEFAULT 0,
    current_price DECIMAL(10, 2),
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, symbol)
);

-- Cash balance table
CREATE TABLE cash_balance (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id VARCHAR(50) NOT NULL DEFAULT 'default_trader',
    balance DECIMAL(15, 2) NOT NULL DEFAULT 1000000.00, -- Start with $1M
    reserved DECIMAL(15, 2) NOT NULL DEFAULT 0, -- Reserved for pending orders
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id)
);

-- Transactions table - all buy/sell activities
CREATE TABLE transactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id VARCHAR(50) NOT NULL DEFAULT 'default_trader',
    symbol VARCHAR(10) NOT NULL,
    transaction_type VARCHAR(10) NOT NULL CHECK (transaction_type IN ('BUY', 'SELL')),
    shares DECIMAL(10, 4) NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    total_amount DECIMAL(15, 2) NOT NULL,
    fees DECIMAL(10, 2) DEFAULT 0,
    executed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    agent_reasoning TEXT, -- LLM's reasoning for the trade
    market_data JSONB, -- Store market context at time of trade
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Daily reports table - track daily performance
CREATE TABLE daily_reports (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id VARCHAR(50) NOT NULL DEFAULT 'default_trader',
    report_date DATE NOT NULL,
    starting_balance DECIMAL(15, 2) NOT NULL,
    ending_balance DECIMAL(15, 2) NOT NULL,
    cash_balance DECIMAL(15, 2) NOT NULL,
    portfolio_value DECIMAL(15, 2) NOT NULL,
    total_value DECIMAL(15, 2) NOT NULL,
    daily_return DECIMAL(10, 4), -- Percentage return
    transactions_count INTEGER DEFAULT 0,
    report_data JSONB, -- Detailed report data
    file_path VARCHAR(500), -- Path to generated report file
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, report_date)
);

-- Stock quotes cache table (for performance)
CREATE TABLE stock_quotes (
    symbol VARCHAR(10) PRIMARY KEY,
    price DECIMAL(10, 2) NOT NULL,
    change_percent DECIMAL(6, 3),
    volume BIGINT,
    market_cap BIGINT,
    pe_ratio DECIMAL(8, 2),
    quote_data JSONB, -- Full quote response
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Agent decisions log (for learning and debugging)
CREATE TABLE agent_decisions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id VARCHAR(50) NOT NULL DEFAULT 'default_trader',
    decision_type VARCHAR(20) NOT NULL, -- 'RECOMMENDATION', 'TRADE', 'REBALANCE'
    input_data JSONB NOT NULL, -- What data was provided to LLM
    llm_response JSONB NOT NULL, -- Full LLM response
    action_taken VARCHAR(50), -- What action was executed
    reasoning TEXT, -- LLM's reasoning
    confidence_score DECIMAL(3, 2), -- 0.00 to 1.00
    execution_status VARCHAR(20) DEFAULT 'PENDING', -- 'PENDING', 'EXECUTED', 'FAILED'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX idx_portfolio_user_symbol ON portfolio(user_id, symbol);
CREATE INDEX idx_transactions_user_date ON transactions(user_id, executed_at);
CREATE INDEX idx_transactions_symbol ON transactions(symbol);
CREATE INDEX idx_daily_reports_user_date ON daily_reports(user_id, report_date);
CREATE INDEX idx_stock_quotes_updated ON stock_quotes(last_updated);
CREATE INDEX idx_agent_decisions_user_type ON agent_decisions(user_id, decision_type);

-- Insert initial cash balance
INSERT INTO cash_balance (user_id, balance) 
VALUES ('default_trader', 1000000.00)
ON CONFLICT (user_id) DO NOTHING;

-- Insert some sample stock quotes for testing
INSERT INTO stock_quotes (symbol, price, change_percent, volume, market_cap, quote_data) VALUES
('AAPL', 175.50, 1.25, 50000000, 2800000000000, '{"symbol": "AAPL", "name": "Apple Inc.", "sector": "Technology"}'),
('GOOGL', 135.25, -0.75, 25000000, 1700000000000, '{"symbol": "GOOGL", "name": "Alphabet Inc.", "sector": "Technology"}'),
('MSFT', 340.80, 0.95, 30000000, 2500000000000, '{"symbol": "MSFT", "name": "Microsoft Corporation", "sector": "Technology"}'),
('TSLA', 245.60, 2.15, 75000000, 780000000000, '{"symbol": "TSLA", "name": "Tesla Inc.", "sector": "Automotive"}'),
('AMZN', 145.90, -1.10, 40000000, 1500000000000, '{"symbol": "AMZN", "name": "Amazon.com Inc.", "sector": "E-commerce"}')
ON CONFLICT (symbol) DO UPDATE SET
    price = EXCLUDED.price,
    change_percent = EXCLUDED.change_percent,
    volume = EXCLUDED.volume,
    market_cap = EXCLUDED.market_cap,
    quote_data = EXCLUDED.quote_data,
    last_updated = CURRENT_TIMESTAMP;

-- Create views for easy querying
CREATE OR REPLACE VIEW portfolio_summary AS
SELECT 
    p.user_id,
    p.symbol,
    p.shares,
    p.avg_cost,
    sq.price as current_price,
    (p.shares * sq.price) as market_value,
    (p.shares * sq.price) - (p.shares * p.avg_cost) as unrealized_pnl,
    ((sq.price - p.avg_cost) / p.avg_cost * 100) as return_percent,
    p.last_updated
FROM portfolio p
LEFT JOIN stock_quotes sq ON p.symbol = sq.symbol
WHERE p.shares > 0;

CREATE OR REPLACE VIEW account_summary AS
SELECT 
    cb.user_id,
    cb.balance as cash_balance,
    COALESCE(SUM(ps.market_value), 0) as portfolio_value,
    cb.balance + COALESCE(SUM(ps.market_value), 0) as total_value,
    COUNT(ps.symbol) as positions_count
FROM cash_balance cb
LEFT JOIN portfolio_summary ps ON cb.user_id = ps.user_id
GROUP BY cb.user_id, cb.balance;
