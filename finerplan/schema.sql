CREATE TABLE IF NOT EXISTS expenses(
    id INTEGER PRIMARY KEY AUTOINCREMENT, 
    pay_method TEXT,
    accrual_date TEXT, 
    cash_date TEXT, 
    description TEXT,
    category_0 TEXT, 
    category_1 TEXT, 
    category_2 TEXT, 
    value REAL
);

CREATE TABLE IF NOT EXISTS earnings(
    id INTEGER PRIMARY KEY AUTOINCREMENT, 
    accrual_date TEXT, 
    cash_date TEXT, 
    description TEXT, 
    category_0 TEXT,
    value REAL
);

CREATE TABLE IF NOT EXISTS assets(
    id INTEGER PRIMARY KEY AUTOINCREMENT, 
    accrual_date TEXT, 
    cash_date TEXT, 
    description TEXT, 
    category_0 TEXT,
    value REAL
);
