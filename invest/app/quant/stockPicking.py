from datetime import datetime
from sqlalchemy.sql import exists
from sqlalchemy import func

from app import db
from app import app
from app.models.main import MainCapitalFlow, DailyRecord

def pick_main_flow(date = datetime.today().strftime('%Y-%m-%d'), defaultPastDays = 5):
  
  picked = []

  pastDays = defaultPastDays

  dates = db.session.query(MainCapitalFlow.recordDate).group_by(MainCapitalFlow.recordDate).order_by(MainCapitalFlow.recordDate.desc()).limit(pastDays)
  startDate = dates[pastDays - 1].recordDate
  endDate = dates[0].recordDate

  records = db.session.query(MainCapitalFlow.code).filter(MainCapitalFlow.recordDate == date).all()
  for stock in records:
    count = db.session.query(MainCapitalFlow.netAmount).filter(MainCapitalFlow.recordDate >= startDate, MainCapitalFlow.code == stock.code, MainCapitalFlow.netAmount > 0).count()
    if count == pastDays:
      stats = db.session.query(func.sum(MainCapitalFlow.netAmount).label("netAmount")).filter(MainCapitalFlow.code == stock.code, MainCapitalFlow.recordDate >= startDate).first()
      r_start = db.session.query(DailyRecord.close, DailyRecord.name).filter(DailyRecord.recordDate == startDate, DailyRecord.code == stock.code).first()
      r_end = db.session.query(DailyRecord.close, DailyRecord.name).filter(DailyRecord.recordDate == endDate, DailyRecord.code == stock.code).first()
      change = '%.2f' % float(((r_end.close - r_start.close)/r_start.close)*100)
      picked.append({'code': stock.code, 'name': r_start.name , 'change': '%s%%' % change, 'amount': stats.netAmount})

  db.session.close()

  for info in picked:
    print(info)

