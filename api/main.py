from api.database import Database
from api.flask_app import FlaskApp
from config import DefaultConfig, FlaskAppConfig

flask_app = FlaskApp()
flask_app.set_config_object(FlaskAppConfig)

db = Database()
db.initiate(flask_app.app)

from api.helpers.cronjobs import delete_files, set_cronjobs
from api.routes import images_blueprint

flask_app.register_all_blueprints(
    [
        images_blueprint,
    ]
)

with flask_app.app_context:
    db.create_all()
    delete_files()
    set_cronjobs(flask_app.app_context)

app = flask_app.app

if __name__ == "__main__":
    flask_app.run(debug=FlaskAppConfig.DEBUG, port=DefaultConfig.PORT)
