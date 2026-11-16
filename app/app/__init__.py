
import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.engine import URL

from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()


def create_app():

    app = Flask(__name__)

    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")

    database_url = URL.create(
        drivername="postgresql+psycopg",
        username=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST", "postgres"),
        port=int(os.getenv("DB_PORT", "5432")),
        database=os.getenv("DB_NAME")
    )

    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    migrate.init_app(app,db)
    #importa os modelos do Alembic
    from . import models
    from .routes import main
    app.register_blueprint(main)

    return app
