from flask import Flask, request, jsonify, abort
from schema import *
from wtforms import ValidationError
from flask_bcrypt import Bcrypt
from flask_session import Session

app = Flask(__name__)
session = db_session()
bcrypt = Bcrypt(app)



@app.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    new_user = Users(id=data['id'], username=data['username'], first_name=data['first_name'],
                    last_name=data['last_name'], email=data['email'], phone=data['phone'],
                    password=bcrypt.generate_password_hash(data['password']).decode('utf-8'))
    session.add(new_user)
    session.commit()
    return jsonify({'message': 'New user created!'})


@app.route('/users/<username>', methods=['GET'])
def get_user(username):
    user = session.query(Users).filter(Users.username == username).one_or_none()
    if user is None:
        return jsonify({'message': "User is not found", "code": 404}), 404
    user_schema = UsersSchema()
    result = user_schema.dump(user)
    return result


@app.route('/users/<username>', methods=['DELETE'])
def delete_user(username):
    user = session.query(Users).filter_by(username=username).first()
    if user is None:
        return jsonify({'message': "User is not found", "code": 404}), 404
    session.delete(user)
    session.commit()
    return jsonify({'message': 'User is deleted!'})


@app.route('/users', methods=['GET'])
def get_users():
    users_list = session.query(Users)
    if users_list :
        return jsonify(UsersSchema(exclude=['password'], many=True).dump(users_list))
    else:
        return 'There is no users'



@app.route('/users/<username>', methods=['PUT'])
def update_user(username):
    user = session.query(Users).filter_by(username=username).first()
    if user is None:
        return jsonify({'message': "User is not found", "code": 404}), 404
    data = request.get_json()
    playlists = []
    if 'playlist_id' in data:
        for i in data['playlist_id']:
            playlists.append(session.query(Playlists).filter_by(id=i).first())
    user.first_name = data['first_name'] if 'first_name' in data else user.first_name
    user.last_name = data['last_name'] if 'last_name' in data else user.last_name
    user.phone = data['phone'] if 'phone' in data else user.phone
    user.password = bcrypt.generate_password_hash(data['password']).decode('utf-8') if 'password' in data else user.password
    user.email = data['email'] if 'email' in data else user.email
    user.playlists=playlists

    session.commit()
    user_schema = UsersSchema()
    result = user_schema.dump(user)
    return result



@app.route('/songs', methods=['GET'])
def get_songs():
    songs_list = session.query(Songs)
    if songs_list :
        return jsonify(SongsSchema(many=True).dump(songs_list))
    else:
        return 'There is no songs'




@app.route('/songs', methods=['POST'])
def add_song():

    data = request.get_json()

    new_song = Songs(id=data['id'], name=data['name'],
                    name_of_author=data['name_of_author'], text=data['text'])
    session.add(new_song)
    session.commit()
    return jsonify({'message': 'New song is added!'})


@app.route('/playlists', methods=['POST'])
def create_playlist():
    data = request.get_json()
    songs = []
    for i in data['songs']:
        song = session.query(Songs).filter_by(id=i).first()
        if song not in songs:
            songs.append(song)

    new_playlist = Playlists(id=data['id'], name=data['name'], is_private=data['is_private'], songs=songs)

    user = session.query(Users).filter_by(id=data['owner_id']).first()
    # print(user)
    if user is None:
        return jsonify({'message': "User is not found", "code": 404}), 404
    user.playlists.append(new_playlist)

    session.add(new_playlist)
    session.commit()
    return jsonify({'message': 'New playlist created!'})

@app.route('/playlists', methods=['GET'])
def get_playlists():

    playlists_list = session.query(Playlists)
    playlists = []
    for i in playlists_list:
        if i.is_private == False:
            playlists.append(i)
    if playlists_list :
        return jsonify(PlaylistsSchema(many=True).dump(playlists))
    else:
        return 'There is no playlists'

@app.route('/playlists/<playlist_id>', methods=['DELETE'])
def delete_playlist(playlist_id):
    playlist = session.query(Playlists).filter_by(id=playlist_id).first()
    if playlist is None:
        return jsonify({'message': "Playlist is not found", "code": 404}), 404
    session.delete(playlist)
    session.commit()
    return jsonify({'message': 'Playlist is deleted!'})


@app.route('/playlists/<playlists_id>', methods=['GET'])
def get_playlist(playlists_id):
    playlist = session.query(Playlists).filter_by(id=playlists_id).first()
    if playlist is None:
        return jsonify({'message': "Playlist is not found", "code": 404}), 404
    playlists_schema = PlaylistsSchema()
    result = playlists_schema.dump(playlist)
    return result


@app.route('/playlists/findByName', methods=['GET'])
def get_playlistbyp():
    data = request.get_json()
    parameter = data['parameter']
    playlist = session.query(Playlists).filter_by(name=parameter).first()
    if playlist:
        playlists_schema = PlaylistsSchema()
        result = playlists_schema.dump(playlist)
        return result
    else:
        return jsonify({'message': "Playlist is not found", "code": 404}), 404


@app.route('/playlists/<playlist_id>', methods=['PUT'])
def update_playlist(playlist_id):
    playlist = session.query(Playlists).filter_by(id=playlist_id).first()
    if playlist is None:
        return jsonify({'message': "Playlist is not found", "code": 404}), 404
    data = request.get_json()
    songs = []
    if 'songs' in data:
        for i in data['songs']:
            songs.append(session.query(Songs).filter_by(id=i).first())
    playlist.name = data['name'] if 'name' in data else playlist.name
    playlist.is_private = data['is_private'] if 'is_private' in data else playlist.is_private
    playlist.songs = songs

    session.commit()
    playlist_schema = PlaylistsSchema()
    result = playlist_schema.dump(playlist)
    return result








if __name__ == '__main__':
    app.run(debug=True)

