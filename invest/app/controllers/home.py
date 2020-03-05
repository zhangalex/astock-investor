from flask import Blueprint, request, jsonify
from sqlalchemy import func
from sqlalchemy.sql import exists
from flask_jwt_extended import (jwt_required, get_jwt_identity, get_jwt_claims)
import decimal 
from datetime import datetime, timedelta

from app import db
from app.models.main import ShortStat, AttentionStocks, User, IndustryStat
from app.common import helper, const

bprint = Blueprint('home', __name__, url_prefix='/api/v1.0/home')

@bprint.route('/industry_stats')
@jwt_required
def industry_stats():
    stats = db.session.query(ShortStat).filter(ShortStat.stype == const.INDUSTRY_STAT_TYPE).first()
    circularStat, holdMarketStat = stats.content['circular'], stats.content['holdmarket']

    
    for item in holdMarketStat:
        item['value'] = '%.2f' % (decimal.Decimal(item['value']) / decimal.Decimal(100000000)).quantize(decimal.Decimal('.01'), rounding='ROUND_HALF_UP')

    circularStat = sorted(circularStat, key=lambda k: decimal.Decimal(k['value']), reverse=True) 
    holdMarketStat = sorted(holdMarketStat, key=lambda k: decimal.Decimal(k['value']), reverse=True) 

    return jsonify({'circular': circularStat, 'holdmarket': holdMarketStat})

@bprint.route('/industry_amount_stats')
@jwt_required
def industry_amount_stats():
    stats = db.session.query(ShortStat).filter(ShortStat.stype == const.INDUSTRY_AMOUNT_INCRE).first()
    amountStats = stats.content
    
    for item in amountStats:
        item['value'] = '%.2f' % (decimal.Decimal(item['value']) / decimal.Decimal(100000000)).quantize(decimal.Decimal('.01'), rounding='ROUND_HALF_UP')

    amountStats = sorted(amountStats, key=lambda k: decimal.Decimal(k['value']), reverse=True) 

    return jsonify({'amountStatsHead': amountStats[:10], 'amountStatsTail': amountStats[-10:], 'updateDate': stats.recordDate.strftime('%Y-%m-%d')})

@bprint.route('/sudden_incres')
@jwt_required
def sudden_incres():
  sourceValue       = request.args.get('source') 
  stype             = request.args.get('stype') 
  targetDate        = request.args.get('targetDate') 
  columns = [
        {'name': 'index',      'type': 'number',  'title': 'No.', 'sortable': False},
        {'name': 'stockcode', 'type': 'stockcode',  'title': '代码', 'sortable': False},
        {'name': 'name', 'type': 'custom',  'title': '名称', 'sortable': False},
        {'name': 'holdMarketValue',  'type': 'amount',  'title': '持有市值', 'sortable': False},
        {'name': 'circularPercent', 'type': 'percent', 'title': '流通占比', 'sortable': False},
        {'name': 'continue', 'type': 'string', 'title': '连续上榜', 'sortable': False},
  ]

  targetType = const.SUDDEN_QTY_INCRE
  if stype == 'reduce':
    targetType = const.SUDDEN_QTY_REDUCE
    columns.append({'name': 'incre', 'type': 'sold', 'title': '持股量激减', 'sortable': False})
  else:
    columns.append({'name': 'incre', 'type': 'buy', 'title': '持股量激增', 'sortable': False})
  
  columns.append({'name': 'isAttention',   'type': 'attention',  'title': '关注', 'sortable': False})

  current_user = db.session.query(User).filter(User.mobile == get_jwt_identity()).first()

  if targetDate == None:
    query = db.session.query(ShortStat).filter(ShortStat.stype == targetType).order_by(ShortStat.recordDate.desc()).first()
  else:
    query = db.session.query(ShortStat).filter(ShortStat.stype == targetType, ShortStat.recordDate == targetDate).first()

  rtList = []
  index = 0
  if sourceValue != 'hk':
    for item in query.content:
      if item['source'] != 'hk':
        rtList.append(item)
  else:
    for item in query.content:
      if item['source'] == 'hk':
        rtList.append(item)

  rtList = sorted(rtList, key=lambda k: decimal.Decimal(k['holdMarketValue']), reverse=True) 
  for item in rtList:
    index += 1
    item['index'] = index 
    item['stockcode'] = item['code']
    if item.get('continue'):
      if int(item['continue']) == 1:
        item['continue'] = '新上榜'
      else:
        item['continue'] = '连续 %s 日' % item['continue']

    else:
      item['continue'] = ''

    item['incre'] = "{0:.2f}%".format(float(item['incre'])*100)
    item['holdMarketValue'] = helper.amountWithUnit(decimal.Decimal(item['holdMarketValue']))
    item['circularPercent'] = decimal.Decimal(item['circularPercent'])/100
    item['isAttention'] = db.session.query(exists().where(AttentionStocks.code == item['code']).where(AttentionStocks.user_id == current_user.id)).scalar()    

  return jsonify({'list': rtList[:12], 'columns': columns, 'lastUpdate': query.recordDate.strftime('%Y-%m-%d')})

@bprint.route('/sudden_incres_dates')
@jwt_required
def sudden_incres_dates():
  qts = db.session.query(ShortStat).with_entities(ShortStat.recordDate).filter(ShortStat.stype == const.SUDDEN_QTY_INCRE).order_by(ShortStat.recordDate.desc()).all()
  dates = [item.recordDate.strftime('%Y-%m-%d') for item in qts]
  return jsonify({'dates': dates})



@bprint.route('/industry_incres_dates')
@jwt_required
def industry_incres_dates():
  startDate     = request.args.get('startDate')
  endDate     = request.args.get('endDate')
  source = request.args.get('source')

  if startDate == None or startDate == '':
    startDate = (datetime.today() - timedelta(days=60)).strftime('%Y-%m-%d')

  if endDate == None or endDate == '':
    endDate = datetime.today().strftime('%Y-%m-%d')


  statsDates = db.session.query(IndustryStat.recordDate).filter(IndustryStat.recordDate >= startDate, IndustryStat.recordDate <= endDate).order_by(IndustryStat.recordDate.asc()).distinct()
  if statsDates.first() != None:
    statsNames = db.session.query(IndustryStat.name).filter(IndustryStat.recordDate == statsDates[-1].recordDate, IndustryStat.source == source).order_by(IndustryStat.amount.asc())
    stats = []
    for sns in statsNames[-10:]:
      stats.append({'name': sns.name, 'values': [{'date': item.recordDate.strftime('%Y-%m-%d'), 'value': (db.session.query(IndustryStat.amount).filter(IndustryStat.recordDate == item.recordDate, IndustryStat.name == sns.name, IndustryStat.source == source).first()).amount} for item in statsDates]})

    for item in stats:
      if source == 'hs':
        item['values'] = [{'date': x['date'], 'value': (x['value'] / decimal.Decimal(100000000)).quantize(decimal.Decimal('.01'), rounding='ROUND_HALF_UP')} for x in item['values'] if x['value'] != None]
      else: 
        item['values'] = [{'date': x['date'], 'value': (x['value'] / decimal.Decimal(10000)).quantize(decimal.Decimal('.01'), rounding='ROUND_HALF_UP')} for x in item['values'] if x['value'] != None]

      item['values'] = sorted(item['values'], key=lambda k: int(k['date'].replace('-',''))) 

    return jsonify({'stats': stats, 'start': startDate, 'end': endDate})
  
  else:
    return jsonify({'stats': [], 'start': startDate, 'end': endDate})
    



