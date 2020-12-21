from marshmallow import Schema, fields, validate, post_load
from model import *


class UsersSchema(Schema):
    id = fields.Int()
    username = fields.Str()
    first_name = fields.Str()
    last_name = fields.Str()
    email = fields.Email(validate=validate.Email())
    password = fields.Str()
    phone = fields.Str()

    @post_load
    def create_user(self, data, **kwargs):
        return Users(**data)


class SongsSchema(Schema):
    id = fields.Int()
    name = fields.Str()
    name_of_author = fields.Str()
    text = fields.Str()


class PlaylistsSchema(Schema):
    id = fields.Int()
    name = fields.Str()
    is_private = fields.Bool()
    # owner_id = fields.Int()
    songs = fields.List(fields.Nested(SongsSchema(only=('id',))))
    @post_load
    def create_playlist(self, data, **kwargs):
        return Playlists(**data)

