from flask import Flask
from configuration.config import Setup


def create_app():
    app = Flask(__name__,instance_relative_config=True)

    app.config.from_object(Setup)

    with app.app_context():


    return app