from app import db
from app import app
from app.models.main import DailyRecord
from app.common import tradeday 
from . import LOGGER

from app import celery
from sqlalchemy.sql import exists
from sqlalchemy import func
import datetime 
import time
import csv
import tushare  as ts

@celery.task(autoretry_for=(Exception,),
          retry_kwargs={'max_retries': 4})
def run():
  # print('start at: %s', datetime.datetime.now())

  if tradeday.isTradeDay():
    with db.app.app_context():
      ROOT_PATH = app.config['DAILY_DATA_PATH']
      today = time.strftime('%Y%m%d')
      filePath = '%s%s.csv' % (ROOT_PATH, today)
      df = ts.get_today_all()
      df.to_csv(filePath)
      __saveRecord(filePath)


  else: 
    LOGGER.info('%s is not trade day.' % datetime.datetime.now())  

def __saveRecord(filePath):

  recordDate = time.strftime('%Y-%m-%d')
  if db.session.query(exists().where(DailyRecord.recordDate == recordDate)).scalar() == True:
    return 

  input_file = csv.DictReader(open(filePath))

  existedList = []
  for row in input_file:
    if row['code'] in existedList:
      continue
    else:
      existedList.append(row['code'])

    record = DailyRecord()
    record.code = row['code']
    record.name = row['name']
    record.changepercent = '%.4f' % float(row['changepercent'])
    record.close = '%.4f' % float(row['trade'])
    record.open = '%.4f' % float(row['open'])
    record.high = '%.4f' % float(row['high'])
    record.low = '%.4f' % float(row['low'])
    record.settlement = '%.4f' % float(row['settlement'])
    record.volume = '%.4f' % float(row['volume'])
    record.turnoverratio = '%.4f' % float(row['turnoverratio'])
    record.amount = '%.4f' % float(row['amount'])
    record.per = '%.4f' % float(row['per'])
    record.pb = '%.4f' % float(row['pb'])
    record.mktcap = float(row['mktcap']) * 10000
    record.nmc = float(row['nmc']) * 10000
    record.recordDate = recordDate
    db.session.add(record)

  db.session.commit() 


