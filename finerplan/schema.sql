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
    description TEXT,
    value REAL,
    custodian TEXT
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
    code TEXT,
    value REAL,
    date TEXT,
    quantity REAL,
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
