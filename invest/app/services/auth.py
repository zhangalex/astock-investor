from flask_jwt_extended import (
    get_jwt_identity, get_jwt_claims
)
from flask import request, jsonify
from datetime import datetime
from app.models.main import User
from app import jwt
from app import app

DATETIME_FORMAT = '%Y-%m-%d %H:%M'

@jwt.user_claims_loader
def add_claims_to_access_token(user):
    return {'roles': [] if user.roles == None or user.roles == '' else user.roles.split(','), 'latestLoginTime': user.latestLoginTime.strftime(DATETIME_FORMAT), 'username': user.username, 'avatar': user.avatar}

@jwt.user_identity_loader
def user_identity_lookup(user):
    return user.mobile

@jwt.claims_verification_loader
def claims_verification_loader(claims):
    expiredTimes = int(app.config["CUSTOM_JWT_TOKEN_EXPIRES"]) #seconds
    lastLoginTime = datetime.strptime(claims["latestLoginTime"], DATETIME_FORMAT)
    diff = (datetime.now() - lastLoginTime).seconds
    if diff > expiredTimes:
        return False
    else:
        return True

@jwt.claims_verification_failed_loader
def claims_verification_failed_loader():
    return jsonify({"message": "User claims verification failed or token expired", "code": -1}), 401