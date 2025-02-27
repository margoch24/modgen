from flask import send_from_directory
from flask_restful import Resource

from api.helpers.request_validator import RequestValidatorTypes
from api.middlewares.validate_request import validate_request
from api.requests import GetImageQuery, ModifyImageFiles, VerifyImageQuery
from api.schemas import GetImageSchema, ModifyImageSchema, VerifyImageSchema
from api.services.images_service import ImagesService
from config import DefaultConfig


class GetImageResource(Resource):

    @validate_request(GetImageSchema, RequestValidatorTypes.Query)
    def get(self):
        query = GetImageQuery()

        response = send_from_directory(
            f"../{DefaultConfig.UPLOAD_FOLDER}", query.filename
        )
        response.headers["Cross-Origin-Resource-Policy"] = "*"
        return response


class ModifyImageResource(Resource):

    @validate_request(ModifyImageSchema, RequestValidatorTypes.Files)
    def post(self):
        files = ModifyImageFiles()

        response = ImagesService.modify_image(files.file)
        return response


class VerifyImageResource(Resource):

    @validate_request(VerifyImageSchema, RequestValidatorTypes.Query)
    def get(self):
        query = VerifyImageQuery()

        response = ImagesService.verify_image(modification_id=query.modification_id)
        return response
