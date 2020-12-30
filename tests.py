import base64

from flask_testing import TestCase
from sqlalchemy.orm import close_all_sessions

import app

user_data = dict(
    id=1,
    username="admin",
    first_name="admin",
    last_name="admin",
    email="admin@gmail.com",
    phone="+3806300101102",
    password="admin")

user_data2 = dict(
    id=2,
    username="notadmin",
    first_name="notadmin",
    last_name="notadmin",
    email="notadmin@gmail.com",
    phone="+3806300101122",
    password="notadmin")

song_data = dict(
    id=1,
    name="Believer",
    name_of_author="ImDr",
    text="First"
)

song_data2 = dict(
    id=2,
    name="Other song",
    name_of_author="Smth",
    text="Second"
)

playlist_data = dict(
    id=1,
    songs=[1, 2],
    name="Top playlist",
    is_private=True
)

playlist_data2 = dict(
    id=2,
    songs=[2],
    name="2 playlist",
    is_private=False
)


def auth_header(username, password):
    valid_credentials = base64.b64encode(bytes(f"{username}:{password}", "utf-8")).decode("utf-8")
    return {"Authorization": "Basic " + valid_credentials}


def playlist_resp(playlist):
    playlist_data_resp = playlist.copy()
    playlist_data_resp["songs"] = [{"id": i} for i in playlist_data_resp["songs"]]
    return playlist_data_resp


class TestBase(TestCase):
    TESTING = True

    def create_app(self):
        app_ = app.app
        app_.config['TESTING'] = True
        return app_

    def setUp(self):
        app.db_session.remove()
        close_all_sessions()
        app.Base.metadata.drop_all(app.engine)
        app.Base.metadata.create_all(app.engine)

    def tearDown(self):
        app.db_session.remove()
        close_all_sessions()
        app.Base.metadata.drop_all(app.engine)


class Test(TestBase):
    def test_get_users_empty(self):
        response = self.client.get("/users")
        self.assert200(response)
        self.assertEqual(response.json, list())

    def test_get_user_unexist(self):
        response = self.client.get("/users/unexist")
        self.assert404(response)
        self.assertEqual(response.json, {'message': "User is not found", "code": 404})

    def test_get_user(self):
        self.test_create_user()

        response = self.client.get(f"/users/{user_data['username']}")

        self.assert200(response)

        user_data_without_pass = user_data.copy()
        user_data_without_pass.pop("password")
        self.assertEqual(response.json, user_data_without_pass)

    def test_create_user(self):
        response = self.client.post("/users", json=user_data)

        self.assert200(response)
        self.assertEqual(response.json, {'message': 'New user created!'})


class TestWithAuth(TestBase):
    def setUp(self):
        super().setUp()
        self.user1 = app.Users(**user_data)
        self.user1.password = app.bcrypt.generate_password_hash(user_data["password"]).decode('utf-8')
        app.session.add(self.user1)

        self.user2 = app.Users(**user_data2)
        self.user2.password = app.bcrypt.generate_password_hash(user_data2["password"]).decode('utf-8')
        app.session.add(self.user2)
        app.session.commit()

    def test_delete_user_bad_credo(self):
        response = self.client.delete(f"/users/{self.user1.username}")
        self.assert401(response)

        response = self.client.delete(f"/users/{self.user1.username}",
                                      headers=auth_header(self.user2.username, user_data2["password"]))
        self.assert401(response)

    def test_delete_user(self):
        response = self.client.delete(f"/users/{self.user1.username}",
                                      headers=auth_header(self.user1.username, user_data["password"]))

        self.assert200(response)
        self.assertEqual(response.json, {'message': 'User is deleted!'})

        response = self.client.get(f"/users/{self.user1.username}",
                                   headers=auth_header(self.user2.username, user_data2["password"]))
        self.assert404(response)

    def test_update_user_unexist(self):
        response = self.client.put(f"/users/qwertyui",
                                   headers=auth_header(self.user2.username, user_data2["password"]))
        self.assert404(response)

    def test_update_user_bad_credo(self):
        response = self.client.put(f"/users/{self.user1.username}")
        self.assert401(response)

        response = self.client.put(f"/users/{self.user1.username}",
                                   headers=auth_header(self.user2.username, user_data2["password"]))
        self.assert401(response)

    def test_update_user_and_get_user(self):
        modified_user = user_data.copy()
        modified_user["email"] = "other.admin@gmail.com"
        response = self.client.put(f"/users/{self.user1.username}", json=modified_user,
                                   headers=auth_header(self.user1.username, user_data["password"]))
        modified_user.pop("password")

        self.assert200(response)
        self.assertEqual(response.json, modified_user)

        response = self.client.get(f"/users/{self.user1.username}")
        self.assert200(response)
        self.assertEqual(response.json, modified_user)

    def test_login_incognito(self):
        response = self.client.delete(f"/users/qwerty123qwerty")
        self.assert401(response)

    def test_login_with_bad_credos(self):
        response = self.client.delete(f"/users/qwerty123qwerty",
                                      headers=auth_header(self.user1.username, "notPass123"))
        self.assert401(response)

    def test_login(self):
        response = self.client.delete(f"/users/qwerty123qwerty",
                                      headers=auth_header(self.user1.username, user_data["password"]))
        self.assert404(response)

    def test_get_songs_empty(self):
        response = self.client.get(f"/songs")
        self.assert200(response)
        self.assertEqual(response.json, [])

    def test_add_song(self):
        response = self.client.post(f"/songs", json=song_data)
        self.assert200(response)
        self.assertEqual(response.json, {'message': 'New song is added!'})

        response = self.client.post(f"/songs", json=song_data2)
        self.assert200(response)
        self.assertEqual(response.json, {'message': 'New song is added!'})

        response = self.client.get(f"/songs")
        self.assert200(response)
        self.assertEqual(response.json, [song_data, song_data2])

    def test_create_playlist(self):
        self.test_add_song()

        response = self.client.post(f"/playlists", json=playlist_data)
        self.assert401(response)

        response = self.client.post(f"/playlists", json=playlist_data,
                                    headers=auth_header(self.user1.username, user_data["password"]))
        self.assert200(response)
        self.assertEqual(response.json, {'message': 'New playlist created!'})

        response = self.client.post(f"/playlists", json=playlist_data2,
                                    headers=auth_header(self.user1.username, user_data["password"]))
        self.assert200(response)
        self.assertEqual(response.json, {'message': 'New playlist created!'})

    def test_get_playlists_incognito(self):
        self.test_create_playlist()
        response = self.client.get(f"/playlists")

        self.assert200(response)
        self.assertEqual(response.json, [playlist_resp(playlist_data2)])

    def test_get_playlists(self):
        self.test_create_playlist()
        response = self.client.get(f"/playlists", headers=auth_header(self.user1.username, user_data["password"]))

        self.assert200(response)
        self.assertEqual(response.json, [playlist_resp(playlist_data2), playlist_resp(playlist_data)])

    def test_delete_playlist_bad_credo(self):
        self.test_create_playlist()
        response = self.client.delete(f"/playlists/{playlist_data['id']}")
        self.assert401(response)

        response = self.client.delete(f"/playlists/{playlist_data['id']}",
                                      headers=auth_header(self.user2.username, user_data2["password"]))
        self.assert401(response)

    def test_delete_playlist_unexist(self):
        response = self.client.delete(f"/playlists/{playlist_data['id']}",
                                      headers=auth_header(self.user1.username, user_data["password"]))
        self.assert404(response)
        self.assertEqual(response.json, {'message': "Playlist is not found", "code": 404})

    def test_delete_playlist(self):
        self.test_create_playlist()

        response = self.client.delete(f"/playlists/{playlist_data['id']}",
                                      headers=auth_header(self.user1.username, user_data["password"]))
        self.assert200(response)
        self.assertEqual(response.json, {'message': 'Playlist is deleted!'})

    def test_get_playlist_unexist(self):
        response = self.client.get(f"/playlists/{playlist_data['id']}")

        self.assert404(response)
        self.assertEqual(response.json, {'message': "Playlist is not found", "code": 404})

    def test_get_playlist(self):
        self.test_create_playlist()
        response = self.client.get(f"/playlists/{playlist_data['id']}")

        self.assert401(response)
        self.assertEqual(response.data, b'Access is not available')

        response = self.client.get(f"/playlists/{playlist_data['id']}",
                                   headers=auth_header(self.user1.username, user_data["password"]))

        self.assert200(response)
        self.assertEqual(response.json, playlist_resp(playlist_data))

    def test_get_playlistbyp_unexist(self):
        response = self.client.get("/playlists/findByName", json={"parameter": "Top playlist"})

        self.assert404(response)
        self.assertEqual(response.json, {'message': "Playlist is not found", "code": 404})

    def test_get_playlistbyp(self):
        self.test_create_playlist()
        response = self.client.get("/playlists/findByName", json={"parameter": "Top playlist"})
        self.assert401(response)

        response = self.client.get("/playlists/findByName", json={"parameter": "Top playlist"},
                                   headers=auth_header(self.user1.username, user_data["password"]))

        self.assert200(response)
        self.assertEqual(response.json, playlist_resp(playlist_data))

    def test_update_playlist_incognito(self):
        self.test_create_playlist()
        response = self.client.put(f"/playlists/{playlist_data['id']}")
        self.assert401(response)

    def test_update_playlist_unexist(self):
        self.test_create_playlist()
        playlist_data_mod = playlist_data
        playlist_data_mod["name"] = "Not top playlist ("
        response = self.client.put(f"/playlists/{playlist_data['id']}", json=playlist_data_mod,
                                   headers=auth_header(self.user1.username, user_data["password"]))
        self.assert200(response)
        self.assertEqual(response.json, playlist_resp(playlist_data_mod))
