from api.constants import VerificationStatus
from api.helpers.models import get_uuid
from api.models.base_model import BaseModel, db


class Modification(BaseModel):
    __tablename__ = "modification"

    id = db.Column(db.String(32), primary_key=True, unique=True, default=get_uuid)
    original_path = db.Column(db.String(225), nullable=False)
    modified_path = db.Column(db.String(225), nullable=False)
    reversed_path = db.Column(db.String(225), nullable=True)
    modification_data = db.Column(db.JSON, nullable=False)
    verification_status = db.Column(db.String(120), default=VerificationStatus.Pending)

    def __repr__(self):
        return f"<Modification {self.id}>"
