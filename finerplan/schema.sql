CREATE TABLE IF NOT EXISTS expenses(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pay_method TEXT,
    accrual_date TEXT,
    cash_date TEXT,
    description TEXT,
    category TEXT,
    category_1 TEXT,
    category_2 TEXT,
    value REAL
);

CREATE TABLE IF NOT EXISTS earnings(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    accrual_date TEXT,
    cash_date TEXT,
    description TEXT,
    category TEXT,
    value REAL
);

CREATE TABLE IF NOT EXISTS brokerage_transfers(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    accrual_date TEXT,
    cash_date TEXT,
    custodian TEXT,
    origin TEXT,
    description TEXT,
    value REAL
);

CREATE TABLE IF NOT EXISTS assets(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT,
    class TEXT,
    subclass TEXT,
    asset TEXT,
    maturity TEXT,
    aim_bool INTEGER,
    aim REAL
);

CREATE TABLE IF NOT EXISTS investments(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT,
    code TEXT,
    quantity REAL,
    value REAL,
    custodian TEXT,
    notes TEXT
);

CREATE TABLE IF NOT EXISTS value_history(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT,
    date TEXT,
    quantity REAL,
    unit_value REAL,
    gross_value REAL,
    net_value REAL
);

CREATE TABLE IF NOT EXISTS rendimentos(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT,
    asset TEXT,
    carteira REAL,
    aporte REAL,
    cotas REAL,
    valor_cotas REAL,
    medium_annual_price REAL,
    medium_historical_price REAL,
    month_earning REAL,
    year_earning REAL,
    total_earning REAL
);
