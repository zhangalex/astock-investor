import requests
import re
import time
import decimal
import os
import copy
from datetime import datetime, timedelta
from sqlalchemy.sql import exists
from sqlalchemy import func
from operator import itemgetter

from app import celery
from app import db
from app import app
from app.models.main import NorthFlow, ShortStat, StockIndustry, IndustryStat
from app.services import dailytrade_service

from app.spider import nf_spider
from app.common import tradeday, const, helper
from . import LOGGER

@celery.task(autoretry_for=(Exception,),
          retry_kwargs={'max_retries': 3})
def run():
  preDay = (datetime.today() - timedelta(days=1)).strftime('%Y-%m-%d')
  if preDay in tradeday.trade_days:
    LOGGER.info('start at: %s' % datetime.now())
    with db.app.app_context():
      pastDays = helper.getPreTradeDays(preDay,3)

      for rday in pastDays:
        if db.session.query(exists().where(ShortStat.stype == const.SUDDEN_QTY_INCRE).where(ShortStat.recordDate == rday)).scalar() == False:
          increList, reduceList = __sudden_qty(rday)
          stat = ShortStat(increList, const.SUDDEN_QTY_INCRE, rday)
          db.session.add(stat)
        
          reduceStat = ShortStat(reduceList, const.SUDDEN_QTY_REDUCE, rday)
          db.session.add(reduceStat)

      #只保留最近3天的数据
      db.session.query(ShortStat).filter(ShortStat.stype == const.SUDDEN_QTY_INCRE, ShortStat.recordDate < pastDays[0]).delete()
      db.session.query(ShortStat).filter(ShortStat.stype == const.SUDDEN_QTY_REDUCE, ShortStat.recordDate < pastDays[0]).delete()
      db.session.commit()

      #计算连续上榜
      __calculateContinue(pastDays, const.SUDDEN_QTY_INCRE) 
      __calculateContinue(pastDays, const.SUDDEN_QTY_REDUCE) 
      

      __industry_daily_marketValue_stat(preDay)
      # __industry_daily_amount_stat(preDay)
      __industry_daily_quantity_stat(preDay)

      __industry_stat(preDay) #计算行业统计数据
      __industry_amount_incre_stat(preDay) #沪，深股通 行业资金当日增量排名统计


      LOGGER.info('completed task at: %s' % datetime.now())


  else: 
    LOGGER.info('%s is not trade day.' % preDay)  

#持有量激增和激减
def __sudden_qty(record_date):
  pastDays = 5
  rtIncreList  = []
  rtReduceList = []
  for source in ['sh', 'sz', 'hk']:
    # nf = db.session.query(NorthFlow).filter_by(source=source).order_by(NorthFlow.recordDate.desc()).first()
    # lastDate = nf.recordDate

    queries = db.session.query(NorthFlow).filter(NorthFlow.source == source, NorthFlow.recordDate == record_date, NorthFlow.circularPercent > 0, NorthFlow.holdMarketValue >= 5000000).all()
    for item in queries:
      preIndex = item.dayIndex - pastDays
      rt = db.session.query(func.avg(NorthFlow.holdQuantity).label('average')).filter(NorthFlow.dayIndex >= preIndex, NorthFlow.dayIndex < item.dayIndex, NorthFlow.stockcode == item.stockcode).first()
      if rt != None and rt.average != None and  rt.average > 0:
        incres = (item.holdQuantity - rt.average)/rt.average

        if incres >= 0.3:
          rtIncreList.append({'hkcode': item.hkcode, 'code': item.stockcode, 'name': item.stockname, 'holdMarketValue': str(item.holdMarketValue), 'circularPercent': str(item.circularPercent), 'source': source, 'incre': str(incres)})

        if incres < 0 and abs(incres) >= 0.25:
          rtReduceList.append({'hkcode': item.hkcode, 'code': item.stockcode, 'name': item.stockname, 'holdMarketValue': str(item.holdMarketValue), 'circularPercent': str(item.circularPercent), 'source': source, 'incre': str(incres)})


  return [rtIncreList, rtReduceList]

def __calculateContinue(pastDays, stype):
  oneList    = db.session.query(ShortStat).filter(ShortStat.stype == stype, ShortStat.recordDate == pastDays[0]).first().content 
  twoList    = db.session.query(ShortStat).filter(ShortStat.stype == stype, ShortStat.recordDate == pastDays[1]).first().content
  lastRecord = db.session.query(ShortStat).filter(ShortStat.stype == stype, ShortStat.recordDate == pastDays[2]).first()
  threeList  = copy.deepcopy(lastRecord.content)
  for item in threeList:
    item['continue'] = 1
    if any(x['code'] == item['code'] for x in twoList):
       item['continue'] = item['continue'] + 1

    if any(x['code'] == item['code'] for x in oneList):
       item['continue'] = item['continue'] + 1

  lastRecord.content = threeList 
  db.session.commit()


#沪，深股通 行业统计
def __industry_stat(record_date):
  
  try:
    # nf = db.session.query(NorthFlow).filter(NorthFlow.source != 'hk').order_by(NorthFlow.recordDate.desc()).first()
    # lastDate = nf.recordDate    
    queries = db.session.query(NorthFlow).filter(NorthFlow.recordDate == record_date, NorthFlow.source != 'hk')

    industryResult = db.session.query(StockIndustry).with_entities(StockIndustry.code, StockIndustry.name)
    industryItems = {item.code: item.name for item in industryResult}

    rt = {}
    for item in queries:
        key = industryItems.get(item.stockcode)
        if key == None:
          continue
        if rt.get(key):
            rt[key] = rt[key] + item.circularPercent
        else:
            rt[key] = item.circularPercent

    # circularStat = sorted(rt.items(), key=itemgetter(1), reverse=True)
    circularStat = [{'name': k, 'value': str(v)} for (k,v) in rt.items()]

    rt = {}
    for item in queries:
        key = industryItems.get(item.stockcode)
        if key == None:
          continue
        if rt.get(key):
            rt[key] = rt[key] + item.holdMarketValue
        else:
            rt[key] = item.holdMarketValue

    # holdMarketStat = sorted(rt.items(), key=itemgetter(1), reverse=True)
    holdMarketStat = [{'name': k, 'value': str(v)} for (k,v) in rt.items()]

    content = {'circular': circularStat, 'holdmarket': holdMarketStat}

    stat = db.session.query(ShortStat).filter(ShortStat.stype == const.INDUSTRY_STAT_TYPE).first() 
    if stat == None:
      stat = ShortStat(content, const.INDUSTRY_STAT_TYPE, record_date)
      db.session.add(stat)
    else:
      stat.content = content 
      stat.recordDate = datetime.now().strftime('%Y-%m-%d')

    db.session.commit()

    # print(circularStat, holdMarketStat)


  except Exception as e:
      LOGGER.error(e, exc_info=True)

#沪，深股通 行业资金当日增量排名统计
def __industry_amount_incre_stat(record_date):
  
  try:
    # nf = db.session.query(NorthFlow).filter(NorthFlow.source != 'hk').order_by(NorthFlow.recordDate.desc()).first()
    # lastDate = nf.recordDate    
    queries = db.session.query(NorthFlow).filter(NorthFlow.recordDate == record_date, NorthFlow.source != 'hk')

    industryResult = db.session.query(StockIndustry).with_entities(StockIndustry.code, StockIndustry.name)
    industryItems = {item.code: item.name for item in industryResult}

    rt = {}
    for item in queries:
        key = industryItems.get(item.stockcode)
        if key == None:
          continue
        if rt.get(key):
            rt[key] = rt[key] + item.oneDayAmount
        else:
            rt[key] = item.oneDayAmount

    amountStat = [{'name': k, 'value': str(v)} for (k,v) in rt.items()]

    stat = db.session.query(ShortStat).filter(ShortStat.stype == const.INDUSTRY_AMOUNT_INCRE).first() 
    if stat == None:
      stat = ShortStat(amountStat, const.INDUSTRY_AMOUNT_INCRE, record_date)
      db.session.add(stat)
    else:
      stat.content = amountStat 
      stat.recordDate = datetime.now().strftime('%Y-%m-%d')

    db.session.commit()


  except Exception as e:
    LOGGER.error(e, exc_info=True)


def __init_fetch_all_industry():
  # dates = db.session.query(NorthFlow.recordDate).distinct().order_by(NorthFlow.recordDate.desc()).limit(200)
  # for date in dates:
    # print(date[0])
    # __industry_daily_marketValue_stat(date[0])

  dates = db.session.query(NorthFlow.recordDate).distinct().order_by(NorthFlow.recordDate.desc()).limit(200)
  for date in dates:
    print(date[0])
    __industry_daily_quantity_stat(date[0])


#沪，深股通 行业 持有市值统计
def __industry_daily_marketValue_stat(record_date):
  
  try:

    queries = db.session.query(NorthFlow).filter(NorthFlow.recordDate == record_date, NorthFlow.source != 'hk')

    industryResult = db.session.query(StockIndustry).with_entities(StockIndustry.code, StockIndustry.name)
    industryItems = {item.code: item.name for item in industryResult}

    rt = {}
    for item in queries:
        industryName = industryItems.get(item.stockcode)
        if industryName == None:
          continue
        if rt.get(industryName):
            rt[industryName] = rt[industryName] + item.holdMarketValue
        else:
            rt[industryName] = item.holdMarketValue

    for (k, v) in rt.items():
      db.session.query(IndustryStat).filter(IndustryStat.recordDate == record_date, IndustryStat.name == k, IndustryStat.source == 'hs').delete()
      stat = IndustryStat(k, v, 'hs', record_date)
      db.session.add(stat)

    db.session.commit()

    print('completed: %s' % record_date)

  except Exception as e:
    print(e)
    LOGGER.error(e, exc_info=True)

def __industry_daily_amount_stat(record_date):
  
  try:

    queries = db.session.query(NorthFlow).filter(NorthFlow.recordDate == record_date, NorthFlow.source != 'hk')

    industryResult = db.session.query(StockIndustry).with_entities(StockIndustry.code, StockIndustry.name)
    industryItems = {item.code: item.name for item in industryResult}

    rt = {}
    for item in queries:
        industryName = industryItems.get(item.stockcode)
        if industryName == None:
          continue
        if rt.get(industryName):
            rt[industryName] = rt[industryName] + item.oneDayAmount
        else:
            rt[industryName] = item.oneDayAmount

    for (k, v) in rt.items():
      db.session.query(IndustryStat).filter(IndustryStat.recordDate == record_date, IndustryStat.name == k, IndustryStat.source == 'hs_daily_incre').delete()
      stat = IndustryStat(k, v, 'hs_daily_incre', record_date)
      db.session.add(stat)

    db.session.commit()

    print('completed: %s' % record_date)

  except Exception as e:
    print(e)
    LOGGER.error(e, exc_info=True)

def __industry_daily_quantity_stat(record_date):
  
  try:

    queries = db.session.query(NorthFlow).filter(NorthFlow.recordDate == record_date, NorthFlow.source != 'hk')

    industryResult = db.session.query(StockIndustry).with_entities(StockIndustry.code, StockIndustry.name)
    industryItems = {item.code: item.name for item in industryResult}

    rt = {}
    for item in queries:
        industryName = industryItems.get(item.stockcode)
        if industryName == None:
          continue
        if rt.get(industryName):
            rt[industryName] = rt[industryName] + item.holdQuantity
        else:
            rt[industryName] = item.holdQuantity

    for (k, v) in rt.items():
      db.session.query(IndustryStat).filter(IndustryStat.recordDate == record_date, IndustryStat.name == k, IndustryStat.source == 'hs_daily_quantity').delete()
      stat = IndustryStat(k, v, 'hs_daily_quantity', record_date)
      db.session.add(stat)

    db.session.commit()

    print('completed: %s' % record_date)

  except Exception as e:
    print(e)
    LOGGER.error(e, exc_info=True)

# #上榜统计
# #统计过去5天连续
# def __continueInTopTen():
#   pass

