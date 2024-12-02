DROP TABLE IF EXISTS users;
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    username TEXT NOT NULL UNIQUE,
    hash TEXT NOT NULL,
    role INTEGER NOT NULL DEFAULT 0 CHECK (role IN (0, 1)),
    profile_link TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);


DROP TABLE IF EXISTS rooms;
CREATE TABLE rooms (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    name TEXT NOT NULL UNIQUE,
    description TEXT NOT NULL,
    key TEXT NOT NULL UNIQUE,
    status INTEGER NOT NULL DEFAULT 0 CHECK (status IN (0, 1)),
    creator_id INTEGER NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (creator_id) REFERENCES users(id)
);


DROP TABLE IF EXISTS members;
CREATE TABLE members (
    user_id INTEGER NOT NULL,
    room_id INTEGER NOT NULL,
    joined_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, room_id),
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (room_id) REFERENCES rooms(id)
);


DROP TABLE IF EXISTS mates;
CREATE TABLE mates (
    user_id1 INTEGER NOT NULL,
    user_id2 INTEGER NOT NULL,
    room_id INTEGER NOT NULL,
    status INTEGER NOT NULL CHECK (status IN (0, 1)),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id1, user_id2),
    FOREIGN KEY (room_id) REFERENCES rooms(id),
    FOREIGN KEY (user_id1) REFERENCES users(id),
    FOREIGN KEY (user_id2) REFERENCES users(id)
);

-- Indexes for Faster Lookups
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_rooms_key ON rooms(key);
CREATE INDEX idx_members_user_id ON members(user_id);
CREATE INDEX idx_members_room_id ON members(room_id);
CREATE INDEX idx_mates_user_id1 ON mates(user_id1);
CREATE INDEX idx_mates_user_id2 ON mates(user_id2);


CREATE TRIGGER update_users_updated_at
AFTER UPDATE ON users
FOR EACH ROW
BEGIN
    UPDATE users
    SET updated_at = CURRENT_TIMESTAMP
    WHERE id = OLD.id;
END;
