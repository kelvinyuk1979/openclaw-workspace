-- 时区套利 Agent 数据库初始化脚本

-- 交易记录表
CREATE TABLE IF NOT EXISTS trades (
    id SERIAL PRIMARY KEY,
    market_name VARCHAR(255) NOT NULL,
    market_id VARCHAR(100) NOT NULL,
    entry_price DECIMAL(10, 4) NOT NULL,
    settlement_price DECIMAL(10, 4),
    position_size DECIMAL(15, 2) NOT NULL,
    expected_return DECIMAL(15, 2) NOT NULL,
    actual_return DECIMAL(15, 2),
    edge_percent DECIMAL(10, 2) NOT NULL,
    confidence DECIMAL(5, 4) NOT NULL,
    status VARCHAR(50) DEFAULT 'pending',  -- pending, executed, settled, cancelled
    settlement_time TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 信息源信号表
CREATE TABLE IF NOT EXISTS signals (
    id SERIAL PRIMARY KEY,
    source_name VARCHAR(100) NOT NULL,
    signal_type VARCHAR(50) NOT NULL,  -- rss, livestream, api
    market_name VARCHAR(255) NOT NULL,
    true_probability DECIMAL(5, 4) NOT NULL,
    market_price DECIMAL(10, 4) NOT NULL,
    confidence DECIMAL(5, 4) NOT NULL,
    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processed BOOLEAN DEFAULT FALSE
);

-- 执行日志表
CREATE TABLE IF NOT EXISTS execution_logs (
    id SERIAL PRIMARY KEY,
    trade_id INTEGER REFERENCES trades(id),
    action VARCHAR(50) NOT NULL,  -- notify, approve, execute, settle
    details JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 性能统计表
CREATE TABLE IF NOT EXISTS performance_stats (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL UNIQUE,
    total_trades INTEGER DEFAULT 0,
    winning_trades INTEGER DEFAULT 0,
    losing_trades INTEGER DEFAULT 0,
    total_invested DECIMAL(15, 2) DEFAULT 0,
    total_return DECIMAL(15, 2) DEFAULT 0,
    total_profit DECIMAL(15, 2) DEFAULT 0,
    avg_edge_percent DECIMAL(10, 2) DEFAULT 0,
    avg_roi_percent DECIMAL(10, 2) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 索引
CREATE INDEX idx_trades_status ON trades(status);
CREATE INDEX idx_trades_settlement_time ON trades(settlement_time);
CREATE INDEX idx_signals_detected_at ON signals(detected_at);
CREATE INDEX idx_signals_processed ON signals(processed);
CREATE INDEX idx_performance_stats_date ON performance_stats(date);

-- 初始数据：2026-03-14 首笔交易记录
INSERT INTO trades (market_name, market_id, entry_price, settlement_price, position_size, expected_return, actual_return, edge_percent, confidence, status, settlement_time)
VALUES
    ('Japan BOJ rate decision', 'boj-2026-03-14', 0.23, 1.00, 2000, 6739.13, 8200, 195.65, 0.90, 'settled', '2026-03-14 04:00:00'),
    ('EU emergency vote', 'eu-vote-2026-03-14', 0.31, 1.00, 2000, 4451.61, 6900, 222.58, 0.85, 'settled', '2026-03-14 04:30:00'),
    ('South Korea policy', 'korea-policy-2026-03-14', 0.19, 1.00, 2000, 8526.32, 11400, 426.32, 0.80, 'settled', '2026-03-14 05:00:00'),
    ('Australia trade deal', 'au-trade-2026-03-14', 0.27, 1.00, 2000, 5407.41, 7100, 270.37, 0.75, 'settled', '2026-03-14 05:15:00'),
    ('UAE production cut', 'uae-oil-2026-03-14', 0.15, 1.00, 2000, 11333.33, 5800, 566.67, 0.85, 'settled', '2026-03-14 05:45:00'),
    ('Singapore regulation', 'sg-reg-2026-03-14', 0.22, 1.00, 2000, 7090.91, 4400, 354.55, 0.80, 'settled', '2026-03-14 06:00:00');

-- 性能统计
INSERT INTO performance_stats (date, total_trades, winning_trades, losing_trades, total_invested, total_return, total_profit, avg_edge_percent, avg_roi_percent)
VALUES ('2026-03-14', 6, 6, 0, 12000, 43800, 31800, 356.02, 265.00);
