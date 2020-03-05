from app import db
from app import app
from app.models.main import HkDailyRecord
from app.common import tradeday 
from . import LOGGER

import requests
from sqlalchemy.sql import exists
from sqlalchemy import func
import datetime 
import time
import csv
import tushare  as ts
import json
import demjson
from app import celery

#读取港股数据
@celery.task(autoretry_for=(Exception,),
          retry_kwargs={'max_retries': 4})
def run():
  # print('start at: %s', datetime.datetime.now())

  if tradeday.isTradeDay():
    LOGGER.info('start at: %s' % datetime.datetime.now())
    with db.app.app_context():
      __saveRecord()
      LOGGER.info('completed task at: %s' % datetime.datetime.now())


  else: 
    LOGGER.info('%s is not trade day.' % datetime.datetime.now())  

def __saveRecord():

  recordDate = time.strftime('%Y-%m-%d')
  if db.session.query(exists().where(HkDailyRecord.recordDate == recordDate)).scalar() == True:
    return 

  qResults = db.session.query(HkDailyRecord.recordIndex, func.count(HkDailyRecord.id)).group_by(HkDailyRecord.recordIndex).order_by(HkDailyRecord.recordIndex.desc()).first()
  index = 1 if qResults == None else (qResults.recordIndex + 1)

  rows = __fetchData()

  for row in rows:
    record = HkDailyRecord()
    record.code = row['code']
    record.name = row['name']
    record.changepercent = row['changepercent'] if row['changepercent'] != '-' else None
    record.change = row['change'] if row['change'] != '-' else None
    record.close = row['close'] if row['close'] != '-' else None
    record.open = row['open'] if row['open'] != '-' else None
    record.high = row['high'] if row['high'] != '-' else None
    record.low = row['low'] if row['low'] != '-' else None
    record.settlement = row['settlement'] if row['settlement'] != '-' else None
    record.volume = row['volume'] if row['volume'] != '-' else None
    record.amount = row['amount'] if row['amount'] != '-' else None
    record.recordDate = recordDate
    record.recordIndex = index
    db.session.add(record)

  db.session.commit() 

def __fetchData():
  url = 'http://nufm.dfcfw.com/EM_Finance2014NumericApplication/JS.aspx?type=CT&cmd=C._HKS&sty=FCOQB&sortType=C&sortRule=-1&page=%s&pageSize=100&js=var quote_123={rank:[(x)],pages:(pc)}&token=7bc05d0d4c3c22ef9fca8c2a912d779c&jsName=quote_123&_g=0.7851060561209007' 
  columns = ['code', 'name', 'volume', 'amount', 'close', 'change', 'changepercent', 'open', 'high', 'low', 'settlement']
  rows = [] 
  for page in range(1, 23):
    res = requests.get(url % page)
    text = res.text 
    _, data = text.split('=')
    py_obj = demjson.decode(data)
    items = py_obj['rank']
    for item in items:
      dc = {} 
      arrays = item.split(',')
      dc['code']          = arrays[0]
      dc['name']          = arrays[1]
      dc['close']         = arrays[2]
      dc['change']        = arrays[3]
      dc['changepercent'] = arrays[4].replace('%','')
      dc['volume']        = arrays[5]
      dc['amount']        = arrays[6]
      dc['open']          = arrays[7]
      dc['high']          = arrays[8]
      dc['low']           = arrays[9]
      dc['settlement']    = arrays[10]
      rows.append(dc)

  return rows 
