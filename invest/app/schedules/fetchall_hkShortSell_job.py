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
from app.models.main import  NorthFlow
from app.schedules import hkShortSell_job
from app.common import tradeday 
from . import LOGGER


@celery.task(autoretry_for=(Exception,),
          retry_kwargs={'max_retries': 3})
def run():
  today = datetime.today().strftime('%Y-%m-%d')
  if today in tradeday.trade_days:
    with db.app.app_context():
      latestRecord = db.session.query(NorthFlow.recordDate).order_by(NorthFlow.recordDate.desc()).first()
      records = db.session.query(NorthFlow.stockcode).filter(NorthFlow.recordDate == latestRecord.recordDate, NorthFlow.source == 'hk').all()
      for item in records:
        # print(item.stockcode)
        hkShortSell_job.run.delay(item.stockcode)

   


