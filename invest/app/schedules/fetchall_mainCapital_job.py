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
from app.models.main import  DailyRecord
from app.schedules import mainCapitalFlow_job
from app.common import tradeday 
from . import LOGGER


@celery.task(autoretry_for=(Exception,),
          retry_kwargs={'max_retries': 3})
def run():
  today = datetime.today().strftime('%Y-%m-%d')
  if today in tradeday.trade_days:
    with db.app.app_context():
      records = db.session.query(DailyRecord.code, DailyRecord.name).filter(DailyRecord.recordDate == today).all()
      for item in records:
        if "ST" not in item.name:
          mainCapitalFlow_job.run.delay(item.code)

      zhishu = ['000001', '399001', '399005', '399006']
      for code in zhishu:
        mainCapitalFlow_job.run.delay(code)

      #'上证指数': '000001', 
      #'深证成指': '399001',
      #'中小板': '399005',
      #'创业板': '399006',
