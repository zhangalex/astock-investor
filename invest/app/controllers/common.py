from flask import Blueprint, request, jsonify
from sqlalchemy import func
from sqlalchemy.sql import exists
import decimal 
import json

from app import db
from app.models.main import NorthFlow,DailyRecord
from app.common import helper, const
from app import redis_store 

bprint = Blueprint('common', __name__, url_prefix='/api/v1.0/common')

@bprint.route('/hold_quantiy_hist')
def hold_quantiy_hist():
    code = request.args.get('code')
    if code == None or code == '':
      return 'error code'

    queries = db.session.query(NorthFlow).filter(NorthFlow.source != 'hk', NorthFlow.stockcode == code).order_by(NorthFlow.recordDate.desc()).limit(90)
    items = []
    for item in queries:
      dr = db.session.query(DailyRecord).filter(DailyRecord.code == code, DailyRecord.recordDate == item.recordDate.strftime("%Y-%m-%d")).first()
      if dr != None:
        items.append({'date': item.recordDate.strftime("%m%d"), 'price': dr.close, 'quantity': item.holdQuantity/10000})

    items.reverse()

    return jsonify({'list': items})

@bprint.route('/a_stock_stat')
def a_stock_stat():
  pass

