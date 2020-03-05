from flask import Blueprint, request, jsonify
from sqlalchemy import func
from sqlalchemy.sql import exists
from flask_jwt_extended import (jwt_required, get_jwt_identity, get_jwt_claims)

from app import db
from app.models.main import StockBasic, Msci
from app.common import helper

bprint = Blueprint('astock', __name__, url_prefix='/api/v1.0/astock')

@bprint.route('/statistic')
@jwt_required
def astock_map():
    queries = db.session.query(StockBasic.area, func.count(StockBasic.id)).group_by(StockBasic.area).all()
    list = [{'name': item[0], 'value': item[1]} for item in queries]
    return jsonify({'list': list})

@bprint.route('/ipo_statistic')
@jwt_required
def ipo_statistic():
    statBy  = request.args.get('statBy')
    if helper.isEmpty(statBy):
        statBy = 'year'

    if statBy == 'year':
        queries = db.session.query(StockBasic.tomarketYear, func.count(StockBasic.id)).group_by(StockBasic.tomarketYear).filter(StockBasic.tomarketYear != None).order_by(StockBasic.tomarketYear.asc()).all()
    else: 
        queries = db.session.query(StockBasic.tomarketYearMonth, func.count(StockBasic.id)).group_by(StockBasic.tomarketYearMonth).filter(StockBasic.tomarketYearMonth != None).order_by(StockBasic.tomarketYearMonth.asc()).all()

    list = [{'name': item[0], 'value': item[1]} for item in queries]
    return jsonify({'list': list})


@bprint.route('/baseinfo')
@jwt_required
def astock_baseinfo():
    page           = request.args.get('page')
    per_page       = request.args.get('perPage')
    orderBy        = request.args.get('orderBy')
    orderDirection = request.args.get('orderDirect')
    qtype          = request.args.get('qtype')

    if page == None or page =='':
        page = 1

    if per_page == None or per_page == '':
        per_page = 12

    if orderBy == None or orderBy == '':
        orderBy        = 'esp'
        orderDirection = 'desc'

    columns = [
        {'name': 'code', 'type': 'stockcode',  'title': '代码'},
        {'name': 'name', 'type': 'string',  'title': '名称'},
        # {'name': 'industry', 'type': 'string',  'title': '行业'},
        {'name': 'pe', 'type': 'string',  'title': '市盈率'},
        # {'name': 'totalAssets', 'type': 'string',  'title': '市值'},
        {'name': 'esp', 'type': 'string',  'title': '每股收益'},
        {'name': 'bvps', 'type': 'string',  'title': '每股净资产'},
        {'name': 'pb', 'type': 'string',  'title': '市净率'},
        {'name': 'rev', 'type': 'percent',  'title': '收入同比', 'hasPercented': True},
        {'name': 'profit', 'type': 'percent',  'title': '利润同比', 'hasPercented': True},
        {'name': 'gpr', 'type': 'percent',  'title': '毛利率', 'hasPercented': True},
        {'name': 'npr', 'type': 'percent',  'title': '净利润率', 'hasPercented': True}
    ]

    if qtype == 'msci':
        queries = db.session.query(StockBasic).join(Msci,StockBasic.code == Msci.code).order_by(getattr(getattr(StockBasic, orderBy), orderDirection)()).order_by(StockBasic.id.asc()).paginate(int(page), int(per_page), True)
    else: 
        queries = db.session.query(StockBasic).order_by(getattr(getattr(StockBasic, orderBy), orderDirection)()).order_by(StockBasic.id.asc()).paginate(int(page), int(per_page), True)

    pageInfo = {
        'total':   queries.total,  
        'current': int(page),  
        'pagenum': int(per_page), 
        'page':    queries.pages,
        'pagegroup': 5,    
        'skin':'#00D1B2'  
    }

    list = []
    for item in queries.items:
        dic = item.as_dict()
        list.append(dic)

    return jsonify({'list': list, 'columns': columns, 'orderBy': orderBy, 'orderDirect': orderDirection, 'lastUpdate': '', 'pagination': pageInfo})


