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
from app.models.main import HkShortSell, HkDailyRecord
from app.channel import eastmoney

from app.common import tradeday 
from . import LOGGER


@celery.task(autoretry_for=(Exception,),
          retry_kwargs={'max_retries': 3})
def run(code):
  today = datetime.today().strftime('%Y-%m-%d')
  if today in tradeday.trade_days:
    with db.app.app_context():
      rows = eastmoney.getHkShortSellingData(code)
      for item in rows:
        if db.session.query(exists().where(HkShortSell.recordDate == item['date']).where(HkShortSell.code == code)).scalar() == False:
          todayHkRecord = db.session.query(HkDailyRecord).filter(HkDailyRecord.code == code, HkDailyRecord.recordDate == item['date']).first()

          hss = HkShortSell()
          hss.recordDate = item['date']
          hss.code = code
          hss.name = item['name']
          hss.quantity = item['quantity']
          hss.avgPrice = item['avgPrice']
          hss.sellAmount = item['sellAmount']
          hss.totalAmount = item['totalAmount']
          hss.ratio = item['ratio']
          if todayHkRecord != None:
            hss.price = todayHkRecord.close

          db.session.add(hss)

      db.session.commit()
