CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_name TEXT NOT NULL,
    product_url TEXT UNIQUE NOT NULL,
    target_price REAL NOT NULL,
    current_price REAL DEFAULT 0,
    notify_email TEXT,
    last_checked TEXT,
    status TEXT DEFAULT 'Not checked',
    notified INTEGER DEFAULT 0
);
