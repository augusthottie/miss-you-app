CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT
); 

CREATE TABLE IF NOT EXISTS notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_id INTEGER,
    target_id INTEGER,
    title TEXT,
    description TEXT,
    is_read BOOLEAN DEFAULT FALSE,
    created_at DATETIME
); 

CREATE TABLE IF NOT EXISTS user_devices (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    device_token TEXT NOT NULL,
    platform TEXT DEFAULT 'ios',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id)
);
