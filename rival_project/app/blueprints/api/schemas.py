from marshmallow import Schema, fields

class UserSchema(Schema):
    id = fields.Int(required=True)
    username = fields.Str(required=True)
    email = fields.Email(required=True)

class CompanySchema(Schema):
    id = fields.Int(required=True)
    name = fields.Str(required=True)
    description = fields.Str()

class EventSchema(Schema):
    id = fields.Int(required=True)
    title = fields.Str(required=True)
    date = fields.Date(required=True)

class WatchlistSchema(Schema):
    id = fields.Int(required=True)
    user_id = fields.Int(required=True)
    company_id = fields.Int(required=True)