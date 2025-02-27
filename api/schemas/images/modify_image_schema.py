from marshmallow import Schema, fields


class ModifyImageSchema(Schema):
    file = fields.Field(required=True)
