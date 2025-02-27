from flask import request


class VerifyImageQuery:
    @property
    def modification_id(self):
        return self.__modification_id

    def __init__(self):
        data = request.args
        self.__modification_id = data.get("modification_id")
