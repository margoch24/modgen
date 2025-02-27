from api.controllers.images_controller import (
    GetImageResource,
    ModifyImageResource,
    VerifyImageResource,
)
from api.flask_app import FlaskApp

app = FlaskApp()

images_blueprint = app.create_blueprint("images")
images_api = app.create_api(images_blueprint)

app.add_resource(images_api, GetImageResource, "/image")
app.add_resource(images_api, ModifyImageResource, "/modify-image")
app.add_resource(images_api, VerifyImageResource, "/verify-image")
