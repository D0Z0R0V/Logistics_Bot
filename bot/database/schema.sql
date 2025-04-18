CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    userid INTEGER NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS channels (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    link TEXT NOT NULL,
    user_id INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(userid)
);

CREATE TABLE IF NOT EXISTS posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    channels_id INTEGER NOT NULL,
    post_text TEXT NOT NULL,
    time_start TIME,
    time_end TIME,
    status INTEGER NOT NULL CHECK (status IN (0, 1)),
    FOREIGN KEY (channels_id) REFERENCES channels(id) ON DELETE CASCADE
);