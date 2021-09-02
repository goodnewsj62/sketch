from flask import Flask
from configuration.config import Setup
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_mail import Mail

db = SQLAlchemy()
bcrypt_ = Bcrypt()
migrate = Migrate()
login_manager = LoginManager()
mail = Mail()

def create_app():
    app = Flask(__name__,instance_relative_config=True)

    # config 
    app.config.from_object(Setup)

    # object_init
    db.init_app(app)
    bcrypt_.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app,db)
    mail.init_app(app)


    with app.app_context():

        from .gallery.views import gallery
        from .auth.auth import auth
        from .user.user import user
        # from .errors.errors import


        app.register_blueprint(gallery)
        app.register_blueprint(auth)
        app.register_blueprint(user)

    return app