from app import db
from app import app
from app.models.main import DailyRecord, HkDailyRecord, NorthFlow, Participant
from app.common import tradeday, helper
from . import LOGGER

from app import celery
from datetime import datetime, timedelta
import tushare as ts
import requests
from . import inform_job

STOCKS = [{'code': '002129', 'name': '中环股份', 'notifyPrice': 11, 'source': 'hs'}, {'code': '603535', 'name': '嘉城国际', 'notifyPrice': 35, 'source': 'hs'}]
@celery.task(autoretry_for=(Exception,),
          retry_kwargs={'max_retries': 3})
def run():
  if tradeday.isTradeDay():
    for item in STOCKS:
      if item['source'] == 'hs':
        df = ts.get_realtime_quotes(item['code'])
        if float(df['price'][0]) >= float(item['notifyPrice']):
          inform_job.send_to_wx.delay('[%s] 当前价格为：%s ，已经达到通知条件。' % (item['name'], df['price'][0]))


  else:
    print('Today is not trade day.')

# def send_to_wx(title, desc=''):
#   url = 'https://sc.ftqq.com/SCU19880Te116691c07d63925173ee3175f92533d5a55b93258cfd.send?text=%s&desp=%s' % (title, desc)
#   requests.post(url)


        




