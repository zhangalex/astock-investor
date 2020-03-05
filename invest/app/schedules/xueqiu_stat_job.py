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
from app.models.main import XueqiuStockStat
from app.services.xueqiu_service import XueqiuService 

from app.common import tradeday 
from . import LOGGER

RATING_SCORE = {'买入': 5, '增持': 4, '强烈推荐': 3, '推荐': 2, '优大于市': 1, '强于大市': 1, '减持': -4, '卖出': -5}

@celery.task(autoretry_for=(Exception,),
          retry_kwargs={'max_retries': 3})
def run(code, recordDate):
  with db.app.app_context():

    db.session.query(XueqiuStockStat).filter(XueqiuStockStat.recordDate == recordDate, XueqiuStockStat.code == code).delete()

    xq = XueqiuService(code)
    followCount = xq.getFollowCount()
    discussCount = xq.getDiscussCount()
    #雪球港股没有研报
    if len(code) > 5:
      researchInfo = xq.getOtherInfo(20, '研报')['list']
      rating = [{'name': item['title'].split('：')[0].strip().replace('［',''), 'rate': item['title'].split('：')[1][:2]} for item in researchInfo]
      totalScore = 0
      for item in rating:
        if item['rate'] in RATING_SCORE and  RATING_SCORE[item['rate']] != None:
          totalScore = totalScore + int(RATING_SCORE[item['rate']])

      xs = XueqiuStockStat(code, followCount, discussCount, rating, totalScore, recordDate)
      db.session.add(xs)
    else:
      xs = XueqiuStockStat(code, followCount, discussCount, None, None, recordDate)
      db.session.add(xs)
    
    db.session.commit() 

    LOGGER.info('completed task at: %s' % datetime.now())


