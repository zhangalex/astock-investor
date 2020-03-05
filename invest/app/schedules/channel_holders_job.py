from app import celery 
from app import db
import requests 
import re
import decimal
from bs4 import BeautifulSoup
from datetime import datetime
from sqlalchemy.sql import exists
from sqlalchemy import func
from app.common import helper
from . import LOGGER
import traceback


from app.models.main import NorthFlow, Participant, DailyRecord, HkDailyRecord
TARGET_URL = 'http://sc.hkexnews.hk/TuniS/www.hkexnews.hk/sdw/search/searchsdw_c.aspx'
#读取股东持有数据
@celery.task(autoretry_for=(Exception,),
          retry_kwargs={'max_retries': 3})
def run(hkcode, stockcode, dateStr, source):
  #dateStr %Y-%m-%d
  with db.app.app_context():
    if db.session.query(exists().where(Participant.recordDate == dateStr).where(Participant.stockcode == stockcode)).scalar() == True:
      return 

  targetCode = hkcode
  if source == 'hk':
    return
    # targetCode = helper.transLongHkCodeFromHkCode(hkcode) 
    # stockcode =  helper.transLongHkCodeFromHkCode(hkcode)

  date = datetime.strptime(dateStr, '%Y-%m-%d')

  payload = {
                '__EVENTTARGET': 'btnSearch',
                '__EVENTARGUMENT': '',
               '__VIEWSTATE': '/wEPDwULLTIwNTMyMzMwMThkZHNjXATvSlyVIlPSDhuziMEZMG94',
                '__VIEWSTATEGENERATOR': '3B50BBBD',
               'today': datetime.now().strftime('%Y%m%d'),
               'sortBy': 'shareholding',
               'sortDirection': 'desc',
               'alertMsg': '',
               'txtShareholdingDate':   date.strftime('%Y/%m/%d'),
               'txtStockCode': targetCode,
              }

  r = requests.post((TARGET_URL), data = payload, timeout = 20)
  data = []
  # print(r)
  if r.status_code == 200:
    soup = BeautifulSoup(r.text, "lxml")
    qdate = soup.select('input#txtShareholdingDate')[0].get('value')
    target_date = datetime.strptime(qdate, '%Y/%m/%d')

    if date.strftime('%Y%m%d') == target_date.strftime('%Y%m%d'):
        # rows = soup.find('table', {'id':'participantShareholdingList'}).find_all('tr')[3:]
        rows = soup.find('table', class_='table-mobile-list').find_all('tr')[1:]
        # print(len(rows))
        for row in rows:
            #print(row)
            tds = row.find_all('td')
            data.append({'code': tds[0].find_all('div')[1].get_text(strip=True), 
                        'name': tds[1].find_all('div')[1].get_text(strip=True), 
                        'holdQuantity': tds[3].find_all('div')[1].get_text(strip=True).replace(',',''), 
                        'stockPercent': tds[4].find_all('div')[1].get_text(strip=True).replace('%','') if len(tds) > 4 else 0,
                        'recordDate': target_date.strftime('%Y-%m-%d')})
   
    else:
        print('Error: %s' % date)

  try:
    with db.app.app_context():
      if data and len(data) > 0:
        latestClosePrice = __getClosePrice(stockcode, source)

        for item in data:
          participant = Participant()
          participant.hkcode          = hkcode
          participant.stockcode       = stockcode
          participant.source          = source
          participant.code            = item['code']
          participant.name            = item['name']
          participant.holdQuantity    = item['holdQuantity']
          participant.stockPercent    = item['stockPercent']
          participant.recordDate      = item['recordDate']
          participant.dayIndex        = None

          preOneDaysPt  = __getPreDaysParticipant(item['recordDate'], item['code'], stockcode, 2)
          preFiveDaysPt = __getPreDaysParticipant(item['recordDate'], item['code'], stockcode, 5)
          

          if preOneDaysPt != None:
            participant.oneDayIncre = int(participant.holdQuantity) - preOneDaysPt.holdQuantity
          else:
            participant.oneDayIncre = int(participant.holdQuantity)

          if latestClosePrice != None:
            participant.oneDayAmount = participant.oneDayIncre * latestClosePrice 
          else:
            participant.oneDayAmount = None 



          if preFiveDaysPt != None:
            participant.fiveDayIncre = int(participant.holdQuantity) - preFiveDaysPt.holdQuantity 
          else:
            participant.fiveDayIncre    = None

          participant.holdMarketValue = (decimal.Decimal(participant.holdQuantity) * decimal.Decimal(latestClosePrice)) if latestClosePrice != None else None
          db.session.add(participant)

      db.session.commit()
      db.session.close()
      LOGGER.info('completed %s on %s' % (stockcode, dateStr))


  except Exception as e:
    LOGGER.error(e)
    traceback.print_exc()

def __getClosePrice(code, source):
    if source != 'hk':
        record = db.session.query(DailyRecord).filter(DailyRecord.code == code, DailyRecord.close != None, DailyRecord.close != 0).order_by(DailyRecord.recordDate.desc()).first()
        return record.close if record != None else decimal.Decimal(0.0) 
    else:
        record = db.session.query(HkDailyRecord).filter(HkDailyRecord.code == code, HkDailyRecord.close != None, HkDailyRecord.close != 0).order_by(HkDailyRecord.recordDate.desc()).first()
        return record.close if record != None else decimal.Decimal(0.0)

def __getPreDaysParticipant(recordDate, code, stockcode, days):
  preDay, *_ = helper.getPreTradeDays(recordDate, days)
  return db.session.query(Participant).filter(Participant.code == code, Participant.stockcode == stockcode, Participant.recordDate == preDay).first()

