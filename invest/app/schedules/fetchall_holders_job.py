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
from app.models.main import NorthFlow

from app.spider import nf_spider
from app.common import tradeday 
from app.schedules import channel_holders_job 

from . import LOGGER

@celery.task
def run():
  preDay = (datetime.today() - timedelta(days=1)).strftime('%Y-%m-%d')
  if preDay in tradeday.trade_days:
    LOGGER.info('start at: %s' % datetime.now())
    try:
      with db.app.app_context():
        nf = db.session.query(NorthFlow).order_by(NorthFlow.recordDate.desc()).first()
        queries = db.session.query(NorthFlow).filter(NorthFlow.recordDate == nf.recordDate).all()
        for item in queries:
          channel_holders_job.run.delay(item.hkcode, item.stockcode, item.recordDate.strftime('%Y-%m-%d'), item.source)

        LOGGER.info('completed task at: %s' % datetime.now())

    except Exception as e:
      LOGGER.error(e, exc_info=True)

  else: 
    LOGGER.info('%s is not trade day.' % preDay)  

def fetchByDate(date):
  try:
    with db.app.app_context():
      queries = db.session.query(NorthFlow).filter(NorthFlow.recordDate == date).all()
      for item in queries:
        channel_holders_job.run.delay(item.hkcode, item.stockcode, item.recordDate.strftime('%Y-%m-%d'), item.source)

      LOGGER.info('completed task at: %s' % datetime.now())

  except Exception as e:
      LOGGER.error(e, exc_info=True)

