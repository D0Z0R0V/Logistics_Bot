CREATE TABLE IF NOT EXISTS channels (
    id INTEGER PRIMARY KEY,
    names VARCHAR(100) NOT NULL,
    link TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS posts (
    id INTEGER PRIMARY KEY,
    channels_id INTEGER REFERENCES channels(id) ON DELETE CASCADE,
    post_text TEXT NOT NULL,
    time_start TIME,
    time_end TIME,
    status BOOLEAN NOT NULL
);