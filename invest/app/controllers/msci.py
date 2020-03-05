from flask import Blueprint, request, jsonify
from sqlalchemy import func
from sqlalchemy.sql import exists
from flask_jwt_extended import (jwt_required, get_jwt_identity, get_jwt_claims)

from app import db
from app.models.main import Msci
from app.common import helper

bprint = Blueprint('msci', __name__, url_prefix='/api/v1.0/msci')

@bprint.route('/list')
@jwt_required
def list():
    columns = [
         {'name': 'code',      'type': 'string',  'title': '代码'},
         {'name': 'name',      'type': 'string',  'title': '名称'},
         {'name': 'industry',  'type': 'string',  'title': '行业'},
         {'name': 'recordDate',  'type': 'date',  'title': '加入时间'}
    ]

    orderBy        = request.args.get('orderBy')
    orderDirection = request.args.get('orderDirect')
    page           = request.args.get('page')
    per_page       = request.args.get('perPage')

    if orderBy == None or orderBy == '':
        orderBy        = 'code'
        orderDirection = 'asc'

    if page == None or page =='':
        page = 1

    if per_page == None or per_page == '':
        per_page = 10

    queries = db.session.query(Msci).order_by(getattr(getattr(Msci, orderBy), orderDirection)()).order_by(Msci.id.asc()).paginate(int(page), int(per_page), False)

    pageInfo = {
        'total':   queries.total,  
        'current': int(page),  
        'pagenum': int(per_page), 
        'page':    queries.pages,
        'pagegroup': 5,    
        'skin':'#00D1B2'  
    }

    dts = []
    for item in queries.items:
        dic = item.as_dict()
        dic['recordDate'] = item.recordDate.strftime("%Y-%m-%d")
        dts.append(dic)

    return jsonify({'list': dts, 'columns': columns, 'orderBy': orderBy, 'orderDirect': orderDirection, 'pagination': pageInfo})

@bprint.route('/chart')
@jwt_required
def chart():
    #col = request.args.get('col')
    cname = getattr(Msci, 'industry')
    queries = db.session.query(cname,func.count(cname).label("ct")).filter(cname !='').group_by(cname).order_by("ct desc").limit(20)
    list = [{'name': item[0], 'value': item[1]} for item in queries]
    return jsonify({'list': list})
