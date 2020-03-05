from flask import Blueprint, request, jsonify
from sqlalchemy import func
from sqlalchemy.sql import exists
import decimal 
import json

from app import db
from app.models.main import Simu, User
from app.common import helper, const
from app import redis_store 

bprint = Blueprint('simu', __name__, url_prefix='/api/v1.0/simu')

@bprint.route('/province_stats')
def province_stats():
    KEY = 'SIMU_PROVINCE_STATS'
    # redis_store.delete(KEY)
    list = redis_store.get(KEY)
    if list == None:
        print('read database....')
        queries = db.session.query(Simu.officeProvince, func.count(Simu.id)).filter(Simu.officeProvince != '').group_by(Simu.officeProvince).all()
        list = [{"name": item[0], "value": item[1]} for item in queries]
        redis_store.set(KEY, json.dumps(list), 5 * 24 * 3600) #默认存储5天

    else:
        list = json.loads(str(list, encoding='utf-8'))
        # print(list)
        print('read from cache....')


    return jsonify({'list': list})

