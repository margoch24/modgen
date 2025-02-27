from marshmallow import Schema, fields


class VerifyImageSchema(Schema):
    modification_id = fields.UUID(required=True)
