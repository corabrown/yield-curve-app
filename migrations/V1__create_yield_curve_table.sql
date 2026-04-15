CREATE TABLE tenors (
    id             SERIAL PRIMARY KEY,
    fred_series_id VARCHAR(20)   NOT NULL UNIQUE,   -- 'DGS10', 'DGS1MO', etc.
    code           VARCHAR(10)   NOT NULL UNIQUE,   -- '10Y', '1M', etc.
    maturity_years NUMERIC(7, 4) NOT NULL,
    sort_order     INTEGER       NOT NULL UNIQUE
);

INSERT INTO tenors (fred_series_id, code, maturity_years, sort_order) VALUES
    ('DGS1MO',  '1M',   0.0833,  1),
    ('DGS3MO',  '3M',   0.2500,  2),
    ('DGS6MO',  '6M',   0.5000,  3),
    ('DGS1',    '1Y',   1.0000,  4),
    ('DGS2',    '2Y',   2.0000,  5),
    ('DGS3',    '3Y',   3.0000,  6),
    ('DGS5',    '5Y',   5.0000,  7),
    ('DGS7',    '7Y',   7.0000,  8),
    ('DGS10',   '10Y', 10.0000,  9),
    ('DGS20',   '20Y', 20.0000, 10),
    ('DGS30',   '30Y', 30.0000, 11);

CREATE TABLE yield_curve_rates (
    id         SERIAL PRIMARY KEY,
    date       DATE          NOT NULL,
    tenor_id   INTEGER       NOT NULL REFERENCES tenors(id),
    rate       NUMERIC(7, 3),
    created_at TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_yield_curve_date_tenor UNIQUE (date, tenor_id)
);

CREATE INDEX idx_yield_curve_rates_date ON yield_curve_rates (date DESC);
