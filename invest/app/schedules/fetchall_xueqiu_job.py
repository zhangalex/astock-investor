import requests
import re
import time
import decimal
import os
from datetime import datetime, timedelta
from sqlalchemy.sql import exists
from sqlalchemy import func

from app import celery
from app import db
from app import app
from app.models.main import NorthFlow, XueqiuStockStat

from app.spider import nf_spider
from app.common import tradeday 
from app.schedules import xueqiu_stat_job
import time 
from . import inform_job
from . import LOGGER

@celery.task(autoretry_for=(Exception,),
          retry_kwargs={'max_retries': 15, 'countdown': 15*60}, soft_time_limit=10800)
def run():
  preDay = (datetime.today() - timedelta(days=1)).strftime('%Y-%m-%d')
  if preDay in tradeday.trade_days:
    LOGGER.info('start at: %s' % datetime.now())
   

    with db.app.app_context():
      nf = db.session.query(NorthFlow).order_by(NorthFlow.recordDate.desc()).first()
      queries = db.session.query(NorthFlow.stockcode).filter(NorthFlow.recordDate == nf.recordDate).distinct()
      codes = [item.stockcode for item in queries]
      recordDate = nf.recordDate.strftime('%Y-%m-%d')

      codes.append('01810')

      
      for code in codes:
        if db.session.query(exists().where(XueqiuStockStat.recordDate == recordDate).where(XueqiuStockStat.code == code)).scalar() == False:
          # print(code)
          xueqiu_stat_job.run(code, recordDate)
          # time.sleep(1)

      todayCount = db.session.query(XueqiuStockStat.id).filter(XueqiuStockStat.recordDate == recordDate).count()

      if(todayCount == len(codes)):
        inform_job.send_to_wx.delay('读取雪球成功：%s' % todayCount)


      LOGGER.info('completed task at: %s' % datetime.now())

  else: 
    LOGGER.info('%s is not trade day.' % preDay)  


