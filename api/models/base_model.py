from api.constants import DEFAULT_LIMIT
from api.database import Database
from api.helpers.helper import current_milli_time

db = Database().get_db()


class BaseModel(db.Model):
    __abstract__ = True

    created_at = db.Column(db.BigInteger, default=current_milli_time)
    updated_at = db.Column(
        db.BigInteger, default=current_milli_time, onupdate=current_milli_time
    )

    @classmethod
    def create(cls, **kwargs):
        record = cls(**kwargs)
        db.session.add(record)
        db.session.commit()
        return record

    @classmethod
    def update_one(cls, record_id, **kwargs):
        record = db.session.get(cls, record_id)
        db.session.query(cls).filter_by(id=record_id).update(kwargs)
        db.session.commit()
        return True

    @classmethod
    def find_one(
        cls,
        condition=None,
        comparative_condition=None,
        join: list[dict] = None,
    ):
        query = db.session.query(cls)

        if join:
            for join_table in join:
                query = query.join(join_table["table"], join_table["condition"])

        if condition:
            query = query.filter_by(**condition)

        if comparative_condition:
            query = query.filter(*comparative_condition)

        return query.first()
