from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Table, Boolean
from sqlalchemy.orm import scoped_session, sessionmaker, relationship, backref
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine('postgres://postgres:nastya@localhost:5432/postgres')

db_session = scoped_session(sessionmaker(bind=engine))

Base = declarative_base()


users_playlists = Table("users_playlists",
                       Base.metadata,
                       Column("id", Integer(), ForeignKey("users.id")),
                       Column("playlist_id", Integer(), ForeignKey("playlists.id")))


playlist_songs = Table("playlist_songs",
                       Base.metadata,
                       Column("playlist_id", Integer(), ForeignKey("playlists.id"), primary_key=True),
                       Column("song_id", Integer(), ForeignKey("songs.id"), primary_key=True))


class Songs(Base):
    __tablename__ = "songs"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    name_of_author = Column(String, nullable=False)
    text = Column(String, nullable=False)

    def __repr__(self):
        return f"<Song '{self.name}', author: {self.name_of_author}, text: {self.text}>"


class Playlists(Base):
    __tablename__ = "playlists"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    songs = relationship(Songs, secondary=playlist_songs, lazy="subquery", backref=backref("playlists", lazy=True))

    is_private = Column(Boolean)

    # owner_id = Column(Integer, ForeignKey(Users.id))
    # owner = relationship(Users, backref="playlists", lazy=False)

    def __repr__(self):
        return f"<Playlist '{self.name}', owner: {self.owner}, songs: {self.songs}>"


class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String, nullable=False)
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String)
    password = Column(String)
    phone = Column(String)
    playlists = relationship(Playlists, secondary=users_playlists, lazy="subquery",
                          backref=backref("Playlists", lazy=True))
    def __repr__(self):
        return f"<User {self.username} ({self.first_name} {self.last_name}), email: {self.email}>"
