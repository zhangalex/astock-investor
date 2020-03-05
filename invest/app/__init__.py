# Import flask and template operators
from flask import Flask, request, jsonify, make_response

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from flask_jwt_extended import (
    JWTManager
)
import os 
import app.celerybuilder as celerybuilder
from flask_redis import FlaskRedis

# import app.scheduleInit as schedule 

# Define the WSGI application object
# app = Flask(__name__, static_folder='./')
app = Flask(__name__)

# Configurations
app.config.from_object('config')
app.config.from_envvar('INVEST_APP_CONFIG',silent=True)

project_root_path = os.path.dirname(os.path.abspath(__file__))
# Define the database object which is imported
# by modules and controllers
db = SQLAlchemy(app)
migrate = Migrate(app, db)

#setup jwt
jwt = JWTManager(app)

#init redis store
redis_store = FlaskRedis(app, config_prefix="CACHE_REDIS")

#init celery 
celery = celerybuilder.make_celery(app)

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

# Import a module / component using its blueprint handler variable (mod_auth)
from app.controllers import home, hkmainland, astock, msci, user, admin, simu, common

# Register blueprint(s)
app.register_blueprint(hkmainland.bprint)
app.register_blueprint(astock.bprint)
app.register_blueprint(msci.bprint)
app.register_blueprint(user.bprint)
app.register_blueprint(admin.bprint)
app.register_blueprint(home.bprint)
app.register_blueprint(simu.bprint)
app.register_blueprint(common.bprint)


# Build the database:
# This will create the database file using SQLAlchemy
# db.create_all()

#init schedule jobs
# schedule.init(app) #再使用ASPSchedule, 使用 Celery 代替

