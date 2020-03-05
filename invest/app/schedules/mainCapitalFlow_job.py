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
from app.models.main import MainCapitalFlow
from app.channel import eastmoney

from app.common import tradeday 
from . import LOGGER


@celery.task(autoretry_for=(Exception,),
          retry_kwargs={'max_retries': 3})
def run(code):
  today = datetime.today().strftime('%Y-%m-%d')
  if today in tradeday.trade_days:
    with db.app.app_context():
      rows = eastmoney.getLatestMainCapitalFlow(code)
      for item in rows:
        if db.session.query(exists().where(MainCapitalFlow.recordDate == item['date']).where(MainCapitalFlow.code == code)).scalar() == False:
          mcf = MainCapitalFlow()
          mcf.recordDate = item['date']
          mcf.code = code
          mcf.price = item['price']
          mcf.change = item['change']
          mcf.netAmount = item['netAmount']
          mcf.netChange = item['netChange']
          db.session.add(mcf)

      db.session.commit()
