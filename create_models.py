from model import db_session, Users, Songs, Playlists

session = db_session()

user_1 = Users(id=1, username="Test1", email="test@test.com", first_name="TestName", password="testpass1")

song_1 = Songs(id=1, name="1st song", name_of_author="AuthorName", text="qwertyuiop")
song_2 = Songs(id=2, name="2nd song", name_of_author="2AuthorName", text="asdfghjkl")
song_3 = Songs(id=3, name="3th song", name_of_author="3AuthorName", text="zxcvbnm")

playlist_1 = Playlists(id=1, name="1st playlist", is_private=True, owner=user_1, songs=[song_1, song_2])
playlist_2 = Playlists(id=2, name="2nd playlist", is_private=False, owner=user_1, songs=[song_2, song_3])

session.add(user_1)

session.add(song_1)
session.add(song_2)
session.add(song_3)

session.add(playlist_1)
session.add(playlist_2)

session.commit()

print(session.query(Users).all())
print(session.query(Songs).all())
print(session.query(Playlists).all())
