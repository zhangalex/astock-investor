from app import db 
from app.models.main import StockBasic, StockFinanceMain, DailyRecord, HkDailyRecord, NorthFlow
from sqlalchemy.sql import exists
from sqlalchemy import func

def getPastDaysChangePercent(code, days, source):
  if source != 'hk':
    limitRecords = db.session.query(DailyRecord).filter(DailyRecord.code == code).order_by(DailyRecord.recordDate.desc()).limit(days)
    lastRecord = limitRecords[0] 
    startDate = (limitRecords[-1]).recordDate

    startRecord = db.session.query(DailyRecord).filter(DailyRecord.code == code, DailyRecord.recordDate >= startDate, DailyRecord.close != 0).order_by(DailyRecord.recordDate.asc()).first() 
    return '%.4f' % float((lastRecord.close - startRecord.close)/startRecord.close)

  else:
    lastRecord = db.session.query(HkDailyRecord).filter(HkDailyRecord.code == code).order_by(HkDailyRecord.recordDate.desc()).first()
    startIndex = lastRecord.recordIndex - days 
    # startRecord = db.session.query(HkDailyRecord).filter(HkDailyRecord.code == code, HkDailyRecord.recordIndex == startIndex).first() 
    startRecord = db.session.query(HkDailyRecord).filter(HkDailyRecord.code == code, HkDailyRecord.recordIndex >= startIndex, HkDailyRecord.close != 0).order_by(HkDailyRecord.recordIndex.asc()).first() 
    return '%.4f' % float((lastRecord.close - startRecord.close)/startRecord.close)
    # if startRecord == None:
      # return None 
    # else:
      # return '%.4f' % float((lastRecord.close - (startRecord.close if startRecord != None else 0))/startRecord.close)

def getPastDaysChangeAmount(code, days):
  lastRecord = db.session.query(NorthFlow).filter(NorthFlow.stockcode == code).order_by(NorthFlow.recordDate.desc()).first()
  startIndex = lastRecord.dayIndex - days 
  result     = db.session.query(func.sum(NorthFlow.oneDayAmount).label("sumAmount")).filter(NorthFlow.stockcode == code, NorthFlow.dayIndex > startIndex).first() 

  return result.sumAmount if result.sumAmount != None else 0

def getClosePrice(code, source):
    if source != 'hk':
        record = db.session.query(DailyRecord).filter(DailyRecord.code == code, DailyRecord.close != None, DailyRecord.close != 0).order_by(DailyRecord.recordDate.desc()).first()
        return record.close if record != None else decimal.Decimal(0.0) 
    else:
        record = db.session.query(HkDailyRecord).filter(HkDailyRecord.code == code, HkDailyRecord.close != None, HkDailyRecord.close != 0).order_by(HkDailyRecord.recordDate.desc()).first()
        return record.close if record != None else decimal.Decimal(0.0)

  
