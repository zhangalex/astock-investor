from app import db
from app import app
from app.models.main import DailyRecord, HkDailyRecord, NorthFlow, Participant
from app.common import tradeday, helper
from . import LOGGER

from app import celery
from sqlalchemy.sql import exists
from sqlalchemy import func
from datetime import datetime, timedelta

from . import inform_job

@celery.task(autoretry_for=(Exception,),
          retry_kwargs={'max_retries': 3})
def run():
  if tradeday.isTradeDay():
    if datetime.now().hour >= 16:
      currentDay = datetime.now().strftime('%Y-%m-%d')
      with db.app.app_context():
        hsCount = db.session.query(DailyRecord.id).filter(DailyRecord.recordDate == currentDay).count()
        if hsCount > 0:
          inform_job.send_to_wx.delay('成功-读取每日行情数据', '沪深: %d' % (hsCount))
        else:
          inform_job.send_to_wx.delay('读取每日行情数据-失败', '沪深: %d' % (hsCount))
  

  if datetime.now().hour >= 6 and datetime.now().hour < 16:
    preDay = (datetime.today() - timedelta(days=1)).strftime('%Y-%m-%d')
    if preDay in tradeday.trade_days:
      compareDay, _ = helper.getPreTradeDays(preDay,2)
      with db.app.app_context():
        errors = []
        thatDayCount = db.session.query(NorthFlow.id).filter(NorthFlow.recordDate == preDay).count()
        cpDayCount   = db.session.query(NorthFlow.id).filter(NorthFlow.recordDate == compareDay).count()
        
        if thatDayCount <= 0:
          errors.append('读取沪深股通 数据出错，数据量为： 0')

        if cpDayCount > 0:
          ratio = (thatDayCount - cpDayCount)/(cpDayCount*1.0)
          if abs(ratio) >= 0.1:
            errors.append('读取沪深股通 数据出错，数据量和昨日不匹配，请查明原因')

        holdersCount = db.session.query(Participant.id).filter(Participant.recordDate == preDay).count() 
        if holdersCount <= 0:
          errors.append('读取股东数据出错，请查明原因，数量为：0')

        if len(errors) > 0:
          inform_job.send_to_wx.delay('读取沪深数据和股东数据-失败', " , ".join(errors))
        else:
          inform_job.send_to_wx.delay('成功-读取沪深数据和股东数据', '沪深: %d, 股东: %d' % (thatDayCount, holdersCount))

        





