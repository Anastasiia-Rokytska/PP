CREATE TABLE users
(
    id          SERIAL NOT NULL,
    username    VARCHAR,
    first_name  VARCHAR,
    last_name   VARCHAR,
    email       VARCHAR,
    password    VARCHAR,
    phone       VARCHAR,
    user_status INTEGER,
    PRIMARY KEY (id)
);

CREATE TABLE songs
(
    id             SERIAL  NOT NULL,
    name           VARCHAR NOT NULL,
    name_of_author VARCHAR NOT NULL,
    text           VARCHAR NOT NULL,
    PRIMARY KEY (id)
);

CREATE TABLE playlists
(
    id         SERIAL  NOT NULL,
    name       VARCHAR NOT NULL,
    is_private BOOLEAN NOT NULL,
    owner_id   INTEGER NOT NULL,
    FOREIGN KEY(owner_id)  REFERENCES users (id) ON DELETE CASCADE,
    PRIMARY KEY (id)
);

CREATE TABLE playlist_songs
(
    playlist_id INTEGER NOT NULL,
    song_id     INTEGER NOT NULL,
    PRIMARY KEY (playlist_id, song_id),
    FOREIGN KEY (playlist_id) REFERENCES playlists (id) ON DELETE CASCADE,
    FOREIGN KEY (song_id) REFERENCES songs (id) ON DELETE CASCADE
);
--
-- CREATE TABLE users_playlists(
--   id INTEGER,
--   playlist_id INTEGER,
--   FOREIGN KEY (id) REFERENCES users(id) ,
--   FOREIGN KEY (playlist_id) REFERENCES playlists(id)
-- );

