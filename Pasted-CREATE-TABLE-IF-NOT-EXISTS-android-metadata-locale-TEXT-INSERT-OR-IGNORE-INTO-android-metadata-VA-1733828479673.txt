CREATE TABLE IF NOT EXISTS android_metadata (locale TEXT);
INSERT OR IGNORE INTO android_metadata VALUES ('en_US');

CREATE TABLE IF NOT EXISTS ChatMessages (
    message_id INTEGER PRIMARY KEY AUTOINCREMENT,
    messenger TEXT NOT NULL,
    time DATETIME NOT NULL,
    sender TEXT,
    text TEXT
);

CREATE TABLE IF NOT EXISTS SMS (
    sms_id INTEGER PRIMARY KEY AUTOINCREMENT,
    sms_type TEXT NOT NULL,
    time DATETIME NOT NULL,
    from_to TEXT,
    text TEXT,
    location TEXT
);

CREATE TABLE IF NOT EXISTS Calls (
    call_id INTEGER PRIMARY KEY AUTOINCREMENT,
    call_type TEXT NOT NULL,
    time DATETIME NOT NULL,
    from_to TEXT,
    duration INTEGER DEFAULT 0,
    location TEXT
);

CREATE TABLE IF NOT EXISTS Keylogs (
    keylog_id INTEGER PRIMARY KEY AUTOINCREMENT,
    application TEXT NOT NULL,
    time DATETIME NOT NULL,
    text TEXT
);

CREATE TABLE IF NOT EXISTS InstalledApps (
    app_id INTEGER PRIMARY KEY AUTOINCREMENT,
    application_name TEXT NOT NULL,
    package_name TEXT UNIQUE NOT NULL,
    install_date DATETIME
);

CREATE TABLE IF NOT EXISTS Contacts (
    contact_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    phone_number TEXT,
    email TEXT,
    last_contacted DATETIME
);

-- Insert sample data
INSERT OR IGNORE INTO ChatMessages (messenger, time, sender, text) VALUES
    ('Messenger', '2024-10-26 08:00:00', 'John Doe', 'Hey there! How are you?'),
    ('Messenger', '2024-10-26 08:05:00', 'You', 'I''m doing well, thanks. How about you?'),
    ('Messenger', '2024-10-26 08:10:00', 'Jane Smith', 'What are you up to today?');

INSERT OR IGNORE INTO SMS (sms_type, time, from_to, text, location) VALUES
    ('received', '2024-10-25 14:30:00', 'Jane Smith', 'Hey, are we still on for tonight?', 'Home'),
    ('sent', '2024-10-25 14:35:00', 'Jane Smith', 'Yes, still on! See you later.', 'Work');

-- Add indexes for frequently accessed columns
CREATE INDEX IF NOT EXISTS idx_chat_sender ON ChatMessages(sender);
CREATE INDEX IF NOT EXISTS idx_chat_time ON ChatMessages(time);
CREATE INDEX IF NOT EXISTS idx_sms_from_to ON SMS(from_to);
CREATE INDEX IF NOT EXISTS idx_sms_time ON SMS(time);
CREATE INDEX IF NOT EXISTS idx_calls_time ON Calls(time);
CREATE INDEX IF NOT EXISTS idx_keylogs_time ON Keylogs(time);