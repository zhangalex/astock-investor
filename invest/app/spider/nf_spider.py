import requests
import re
import time
import decimal
import csv
import os
import json
import demjson 
from bs4 import BeautifulSoup
from datetime import datetime
from sqlalchemy.sql import exists
from sqlalchemy import func

from app import db
from app import app
from app.models.main import NorthFlow, StockBasic, NorthStatistics, StockShareHolder, DailyRecord, HkDailyRecord
from app.common import tradeday 
from app.common import helper

TARGET_URL = 'http://sc.hkexnews.hk/TuniS/www.hkexnews.hk/sdw/search/mutualmarket_c.aspx?t=%s'
# http://sc.hkexnews.hk/TuniS/www.hkexnews.hk/sdw/search/mutualmarket_c.aspx?t=sh
# http://sc.hkexnews.hk/TuniS/www.hkexnews.hk/sdw/search/mutualmarket_c.aspx?t=sz
# wind 研究报告首页 ： http://180.96.8.44/WindRCHost/

def run():
    print('>> start read 沪股通,....')
    __fetch_north_flows('sh')
    print('>> start read 深股通....')
    __fetch_north_flows('sz')
    static_data('sh')
    static_data('sz')

    #判断沪股通是否关闭
    if (not __isClosedChannel('sh')) and (not __isClosedChannel('sz')):
        print('>> start refresh...')
        refreshHSCircularPercent()
        buildHSStatisticData()
    else:
        #沪股通当日关闭
        print('沪股通当日关闭')
        __deleteLatestBySource('sh')
        __deleteLatestBySource('sz')

    # print('>> start read 港股通....')
    # __fetch_north_flows('hk')
    # static_data('hk')

    # if __isClosedChannel('hk'):
    #     print('港股通当日关闭')
    #     __deleteLatestBySource('hk')
    # else:
    #     refreshHKCircularPercent()
    #     buildHKStatisticData()

    #刷新持有市值
    refreshMarketValue()
    #刷新持续买卖
    refresh_continue_buyAndSold()


    print("Completed!!")

#判断通道是否关闭
def __isClosedChannel(source):
    nf = db.session.query(NorthFlow).filter_by(source=source).order_by(NorthFlow.recordDate.desc()).first()
    lastDate = nf.recordDate
    result =  db.session.query(func.sum(NorthFlow.oneDayIncre).label("oneDayIncre")).filter(NorthFlow.recordDate == lastDate, NorthFlow.source == source).first()

    return result.oneDayIncre == None or result.oneDayIncre == 0

def __deleteLatestBySource(source):
    nf = db.session.query(NorthFlow).filter_by(source=source).order_by(NorthFlow.recordDate.desc()).first()
    lastDate = nf.recordDate
    db.session.query(NorthFlow).filter(NorthFlow.source == source, NorthFlow.recordDate == lastDate).delete()
    db.session.commit()
    db.session.close()


def __fetch_north_flows(source = 'sh'):
    # print(TARGET_URL % source)
    r = requests.get(TARGET_URL % source)
    data = []
    if r.status_code == 200:
        soup = BeautifulSoup(r.text, "lxml")
        qdate = soup.select('input#txtShareholdingDate')[0].get('value')
        dt = datetime.strptime(qdate, '%Y/%m/%d')

        rows = soup.find('table', class_='table-mobile-list').find_all('tr')[1:]
        for row in rows:
            tds = row.find_all('td')
            data.append({'hkcode':        tds[0].find_all('div')[1].get_text(strip=True), 
                         'stockname':     tds[1].find_all('div')[1].get_text(strip=True), 
                         'holdQuantity':  tds[2].find_all('div')[1].get_text(strip=True).replace(',',''), 
                         'astockPercent': tds[3].find_all('div')[1].get_text(strip=True).replace('%','')})


        # for d in data:
        #     print(d)

        # return 

        nf = db.session.query(NorthFlow).filter_by(source=source).order_by(NorthFlow.recordDate.desc()).first()
        currentIndex = None
        if nf:
            currentIndex = nf.dayIndex + 1
        else:
            currentIndex = 0

        for rd in data:
            if db.session.query(exists().where(NorthFlow.recordDate == dt).where(NorthFlow.hkcode == rd['hkcode']).where(NorthFlow.source == source)).scalar() == False:
                percent = rd['astockPercent'] if rd['astockPercent'] != '' else '0'
                stockname = rd['stockname'].replace(' ','').replace("ＴＣＬ",'TCL')
                stockname = stockname[:45]
                if stockname[:2] == '片仔':
                    stockname = '片仔癀'

                if stockname[:3] == '苏州固':
                    stockname = '苏州固锝'

                if stockname == '安信信讬':
                    stockname = '安信信托'

                if source == 'hk':
                    stockcode = helper.transLongHkCodeFromHkCode(rd['hkcode'])
                else:
                    stockcode = helper.transToCodeFromHkCode(rd['hkcode'])


                nf = NorthFlow(rd['hkcode'], stockname, rd['holdQuantity'], percent, dt, currentIndex, source, stockcode)
                db.session.add(nf)

        db.session.commit()
        db.session.close()


def static_data(source):
    #统计日持股增量
    nf = db.session.query(NorthFlow).filter_by(source=source).order_by(NorthFlow.recordDate.desc()).first()
    lastDate = nf.recordDate
    queries = db.session.query(NorthFlow).filter_by(recordDate=lastDate, source=source)
    for item in queries:
        prevOne  = db.session.query(NorthFlow).filter_by(dayIndex = (item.dayIndex - 1),  hkcode=item.hkcode, source=source).first()
        prevFive = db.session.query(NorthFlow).filter_by(dayIndex= (item.dayIndex - 4), hkcode=item.hkcode, source=source).first()
        prevTen  = db.session.query(NorthFlow).filter_by(dayIndex= (item.dayIndex - 9), hkcode=item.hkcode, source=source).first()
        if prevOne:
            item.oneDayIncre = item.holdQuantity - prevOne.holdQuantity

        if prevFive:
            item.fiveDayIncre = item.holdQuantity - prevFive.holdQuantity

        if prevTen:
            item.tenDayIncre = item.holdQuantity - prevTen.holdQuantity

    db.session.commit()
    
    db.session.close()

def fix_indexes(source = 'sh'):
    dates = []
    start_date = '2017-03-18'
    end_date   = '2017-11-17'
    k = 0
    for day in tradeday.trade_days:
        if __dateStrToInt(day) >= __dateStrToInt(start_date) and __dateStrToInt(day) <= __dateStrToInt(end_date):
            if db.session.query(exists().where(NorthFlow.recordDate == day).where(NorthFlow.source == source)).scalar() == True:
                queries = db.session.query(NorthFlow).filter_by(recordDate = day, source = source)
                for qe in queries:
                    qe.dayIndex = k

                db.session.commit()
                db.session.close()
                k = k + 1



def fetch_old_records(source = 'sh'):
    try:
        dates = []
        start_date = '2017-03-18'
        end_date   = '2017-11-17'
        for day in tradeday.trade_days:
            if __dateStrToInt(day) >= __dateStrToInt(start_date) and __dateStrToInt(day) <= __dateStrToInt(end_date):
                dates.append(day)

        # print(dates)
        for dt in dates:
            if db.session.query(exists().where(NorthFlow.recordDate == dt).where(NorthFlow.source == source)).scalar() == False:
                records = fetch_data_by_date(dt, source)
                for rd in records:
                    percent = rd['astockPercent'] if rd['astockPercent'] != '' else '0'
                    nf = NorthFlow(rd['hkcode'], rd['stockname'], rd['holdQuantity'], percent, dt, -1, source)
                    db.session.add(nf)

                db.session.commit()
                # print(records)
                print('%s ====================================================================================' % dt)
    
        print('Completed...')

    finally:
        db.session.close()


#date format Y-m-d
def fetch_data_by_date(date, source):
    query_date = datetime.strptime(date, '%Y-%m-%d')
    payload = {
               '__VIEWSTATE': 'Zlv74YbF59Eq+74WFavokt0q/5WYKuYW1g+L25BumPoEsRQaU+h3m6nB1ncyCzphqt8wn55ejVVnCc+wq3Y0trs9KyoF5Yv1v3RZcXXNNYkCDv9McUi80zHUnxQUNelS4jNkpmG1oSr9qqiSBYol3xUYk6AMYxqUeAUz05z33Mp1tpw1cbIWT+VWsR2Km3gPq9j2pA==',
                '__VIEWSTATEGENERATOR': 'EC4ACD6F',
               '__EVENTVALIDATION': 'LM9+kfN6/m+JE0bfZ+DngQ+oQ1REVYhesXrHtQ0tYCn0ArZOiQ6fpcgKe6YOT67heEAZ9EN8jn6VgDkro1fY9HGNVVnAOVZP+L6zPVSkDNxWQFJTH8hYQIJTwad2wr9HkrMrdWiseNfZSygiSBjb6LVm1f6pxQDjpDO82cUn7q3rx1AbAZuEaCCGm5xnbBo/g6UVjHQqh/q4gCawuyTnTt874ORGEQmOQ7DUVK4a024soem4dDBxLD12fe2ExXgsvLOLyGKalwrzN6bTV0xnRg9ddjpCOoESBNGC2Wxpm42r7sLiHnxtiFWVEU79RE+4zOz306lJyGtZiXVSq2YYy+aK6zdCwK3DBD9D3JwJdgufbsnc5ZmbzAl1OUJDDNnckgxfOqZngNQRvyJTjYufG6U7YI1YDy/J0FXrStKDOg8A6uBe99xaWfOVIMg7zn5s9r5lffEQLYAcJmRTUSLwx6pTRoMTUy7xx8a/ATCBPyM4sIpPB91ZD3KOwyKklPcM1WCuUz8fjBBofOY+ozfrH9B/mujGpMDPqF2zy1lLGv1we5UvlPpjveZCzMH+heCV5YnK3sHARO/27Ff0+RIybfPXG5BEprxAUt43XVz5OCV4YCPTznXSzpmJ/SGKvJulOTl4RPaKX+bqyChA0f/TX9dOyujG495DrEhVIGktqC8gv3R4tA4b9n4+kafJZQW+4oLhO3VWinFQtuOTiJR2LwgeZO5daX/dK6DCS2nQ8/qmGIr9J6NswW3NZbqf0FFerPQ+PRY5zx+GKvEbBY/v7Q0wW0v0Me7XVkalVKIle0LjQN8LwdcdvT9wXUO/yOtUQJ4NO9QrK2nyKeEKZmT98p81CaW/i/dGEsXG+6czEomGU9WTUjUpyvUYXTW6lriPWBOluKyD3O+29SkfIVOYA5f8m2NVsKuQBU3JdBFVxL5YXH2fySnTRNeoxUKxW4UB+9s+ATs2uNNlJZVRVAYzBo9a6WaMrzizgNOrfrMz08ddfpNdhijLnf/z2RUAYB9vPaAa46z9eiU3mSTVnhc18483oNQIiqtUfnDmxedFd6MyvkJX2+XBX/oQDrVsOaeAQ5Ax/M4suvA66bRWjTKb+jT7vKXZ/2MzB7f+z1MX8yGo+DMIi6b84y75jdnJwjJ3kqUddxCn05ta7e5okrC2I2aHwEc=',
               'today': datetime.now().strftime('%Y%m%d'),
               'sortBy': 'ShareholdingPercent',
               'alertMsg': '',
               'ddlShareholdingDay':   query_date.strftime('%d'),
               'ddlShareholdingMonth': query_date.strftime('%m'),
               'ddlShareholdingYear':  query_date.strftime('%Y'),
               'btnSearch.x': '27',
               'btnSearch.y': '16'
              }
    r = requests.post((TARGET_URL % source), data = payload, timeout = 10)
    

    data = []
    if r.status_code == 200:
        soup  = BeautifulSoup(r.text, "lxml")
        qdate = soup.select('div#pnlResult > div')[0].get_text(strip=True)
        target_date = datetime.strptime(re.split(r'\s+', qdate)[1], '%d/%m/%Y')
        
        if query_date.strftime('%Y%m%d') == target_date.strftime('%Y%m%d'):
            rows = soup.find('table', class_='result-table').find_all('tr')[2:]
            #rows = soup.select('table.result-table > tbody > tr')[2:]
            for row in rows:
                tds = row.find_all('td')
                data.append({'hkcode': tds[0].get_text(strip=True), 
                             'stockname': tds[1].get_text(strip=True), 
                             'holdQuantity': tds[2].get_text(strip=True).replace(',',''), 
                             'astockPercent': tds[3].get_text(strip=True).replace('%',''),
                             'recordDate': target_date.strftime('%Y-%m-%d')})
   
        else:
            print('Error: %s' % date)

    return data 


def __dateStrToInt(dr):
    return int(dr.replace('-',''))



#统计沪股通，深股通
def buildHSStatisticData():
    try:
        qResults = db.session.query(NorthFlow.recordDate, func.count(NorthFlow.id)).group_by(NorthFlow.recordDate).filter(NorthFlow.source != 'hk').order_by(NorthFlow.recordDate.desc()).all()
        dateList = [item[0] for item in qResults][:2]

        for qdate in dateList:
            if db.session.query(exists().where(NorthStatistics.recordDate == qdate).where(NorthStatistics.source !='hk')).scalar() == False:
                queries = db.session.query(NorthFlow).filter(NorthFlow.recordDate == qdate, NorthFlow.source != 'hk')
                for item in queries:
                    # code = helper.transToCodeFromHkCode(item.hkcode)
                    closePrice = __getClosePrice(item.stockcode, qdate, item.source)
                    if item.oneDayIncre != None and item.oneDayIncre != 0 and closePrice != None:
                        item.oneDayAmount = item.oneDayIncre * decimal.Decimal(closePrice)
                    else:
                        item.oneDayAmount = 0

                db.session.commit()

                buyCount = db.session.query(NorthFlow).filter(NorthFlow.recordDate == qdate, NorthFlow.oneDayIncre > 0, NorthFlow.source != 'hk').count()
                soldCount = db.session.query(NorthFlow).filter(NorthFlow.recordDate == qdate, NorthFlow.oneDayIncre < 0, NorthFlow.source != 'hk').count()
                buyResult =  db.session.query(func.sum(NorthFlow.oneDayAmount).label("sumAmount")).filter(NorthFlow.recordDate == qdate, NorthFlow.oneDayAmount > 0, NorthFlow.source != 'hk').first()
                soldResult =  db.session.query(func.sum(NorthFlow.oneDayAmount).label("sumAmount")).filter(NorthFlow.recordDate == qdate, NorthFlow.oneDayAmount < 0, NorthFlow.source != 'hk').first()
                buyAmount = buyResult.sumAmount if buyResult.sumAmount != None else 0
                soldAmount = soldResult.sumAmount if soldResult.sumAmount != None else 0

                stat = NorthStatistics()
                stat.recordDate = qdate
                stat.buyCount = buyCount
                stat.soldCount = soldCount
                stat.buyAmount = buyAmount
                stat.soldAmount = soldAmount
                stat.source = 'hs'
                db.session.add(stat)
                db.session.commit()

    finally:
        db.session.close()

#统计港股通
def buildHKStatisticData():
    try:
        qResults = db.session.query(NorthFlow.recordDate, func.count(NorthFlow.id)).group_by(NorthFlow.recordDate).filter(NorthFlow.source == 'hk').order_by(NorthFlow.recordDate.desc()).all()
        dateList = [item[0] for item in qResults][:2]

        for qdate in dateList:
            if db.session.query(exists().where(NorthStatistics.recordDate == qdate).where(NorthStatistics.source != 'hs')).scalar() == False:
                queries = db.session.query(NorthFlow).filter(NorthFlow.recordDate == qdate, NorthFlow.source == 'hk')
                for item in queries:
                    # code = helper.transToCodeFromHkCode(item.hkcode)
                    closePrice = __getClosePrice(item.stockcode, qdate, item.source)
                    if item.oneDayIncre != None and item.oneDayIncre != 0 and closePrice != None:
                        item.oneDayAmount = item.oneDayIncre * decimal.Decimal(closePrice)
                    else:
                        item.oneDayAmount = 0

                db.session.commit()

                buyCount = db.session.query(NorthFlow).filter(NorthFlow.recordDate == qdate, NorthFlow.oneDayIncre > 0, NorthFlow.source == 'hk').count()
                soldCount = db.session.query(NorthFlow).filter(NorthFlow.recordDate == qdate, NorthFlow.oneDayIncre < 0, NorthFlow.source == 'hk').count()
                buyResult =  db.session.query(func.sum(NorthFlow.oneDayAmount).label("sumAmount")).filter(NorthFlow.recordDate == qdate, NorthFlow.oneDayAmount > 0, NorthFlow.source == 'hk').first()
                soldResult =  db.session.query(func.sum(NorthFlow.oneDayAmount).label("sumAmount")).filter(NorthFlow.recordDate == qdate, NorthFlow.oneDayAmount < 0, NorthFlow.source == 'hk').first()
                buyAmount = buyResult.sumAmount if buyResult.sumAmount != None else 0
                soldAmount = soldResult.sumAmount if soldResult.sumAmount != None else 0

                stat = NorthStatistics()
                stat.recordDate = qdate
                stat.buyCount = buyCount
                stat.soldCount = soldCount
                stat.buyAmount = buyAmount
                stat.soldAmount = soldAmount
                stat.source = 'hk'
                db.session.add(stat)
                db.session.commit()

    finally:
        db.session.close()

def refreshHSCircularPercent():
    try:
        nf = db.session.query(NorthFlow).filter(NorthFlow.source != 'hk').order_by(NorthFlow.recordDate.desc()).first()
        lastDate = nf.recordDate    
        queries = db.session.query(NorthFlow).filter(NorthFlow.recordDate == lastDate, NorthFlow.source != 'hk')
        for item in queries:
            basicInfo = db.session.query(StockBasic).filter(StockBasic.code == helper.transToCodeFromHkCode(item.hkcode)).first()
            if basicInfo != None:
                circularQuantity = decimal.Decimal(basicInfo.outstanding * 10000 * 10000)
                if circularQuantity > 0:
                    item.circularPercent = ((decimal.Decimal(item.holdQuantity) / circularQuantity) * decimal.Decimal(100)).quantize(decimal.Decimal('.01'), rounding='ROUND_HALF_UP')
                else:
                    item.circularPercent = item.astockPercent

        db.session.commit()

    finally:
        db.session.close()

def refreshHKCircularPercent():
    try:
        nf = db.session.query(NorthFlow).filter(NorthFlow.source == 'hk').order_by(NorthFlow.recordDate.desc()).first()
        lastDate = nf.recordDate    
        queries = db.session.query(NorthFlow).filter(NorthFlow.recordDate == lastDate, NorthFlow.source == 'hk')
        for item in queries:
            item.circularPercent = item.astockPercent  #港股通暂时和持股比例相等
        
        db.session.commit()
            # basicInfo = db.session.query(StockBasic).filter(StockBasic.code == helper.transToCodeFromHkCode(item.hkcode)).first()
            # if basicInfo != None:
                # item.circularPercent = item.astockPercent  #港股通暂时和持股比例相等
                # circularQuantity = decimal.Decimal(basicInfo.outstanding * 10000 * 10000)
                # item.circularPercent = ((decimal.Decimal(item.holdQuantity) / circularQuantity) * decimal.Decimal(100)).quantize(decimal.Decimal('.01'), rounding='ROUND_HALF_UP')
                # db.session.commit()

    finally:
        db.session.close()


def refreshMarketValue(targetDate = None):
    try:
        nf = db.session.query(NorthFlow).order_by(NorthFlow.recordDate.desc()).first()
        lastDate = targetDate or nf.recordDate  

        queries = db.session.query(NorthFlow).filter(NorthFlow.recordDate == lastDate)
        for item in queries:
            closePrice = __getClosePrice(item.stockcode, lastDate, item.source)
            if closePrice != None:
                item.holdMarketValue = item.holdQuantity * decimal.Decimal(closePrice) 

        db.session.commit()


    finally:
        db.session.close()


def fetch_latest_shareholders():
    targetDate = '2017-09-30'
    LTG_URL = 'http://data.eastmoney.com/DataCenter_V3/gdfx/stockholder.ashx?code=%s&date=%s&type=Lt'
    GD_URL = 'http://data.eastmoney.com/DataCenter_V3/gdfx/stockholder.ashx?code=%s&date=%s&type=Sd'

    # LTG_URL = "http://dcfm.eastmoney.com/em_mutisvcexpandinterface/api/js/get?type=NSHDDETAIL&token=70f12f2f4f091e459a279469fe49eca5&cmd=&st=SHAREHDNUM&sr=-1&p=1&ps=20&filter=(SCODE='%s')(RDATE=^%s^)&js=(x)"
    # GD_URL = "http://dcfm.eastmoney.com/em_mutisvcexpandinterface/api/js/get?type=HDDETAIL&token=70f12f2f4f091e459a279469fe49eca5&cmd=&st=SHAREHDNUM&sr=-1&p=1&ps=20&filter=(SCODE='%s')(RDATE=^%s^)&js=(x)"

    try:
        queries = db.session.query(StockBasic).all()
        for item in queries:
            print(item.code, item.name)
            #获取十大流通股东
            if db.session.query(exists().where(StockShareHolder.reportDate == targetDate).where(StockShareHolder.code == item.code).where(StockShareHolder.category == 0)).scalar() == False:
                ltRes = requests.get(LTG_URL % (item.code, targetDate))
                ltData = ltRes.json()['data']
                for dt in ltData:
                    holder = StockShareHolder()
                    holder.code = item.code
                    holder.name = item.name
                    holder.holderType = dt["SHAREHDTYPE"]
                    holder.holderName = dt["SHAREHDNAME"]
                    holder.stockType = dt["SHARESTYPE"]
                    holder.holdQuantity = dt["SHAREHDNUM"]
                    holder.stockPercent = '%.2f' % (float(dt["ZB"]) * float(100))
                    holder.change = dt["BZ"]
                    holder.changeQuantity = dt["BDSUM"] if dt["BDSUM"] != '-' else '0'
                    holder.category = 0
                    holder.reportDate = targetDate
                    db.session.add(holder)

                db.session.commit()
                time.sleep(200)

            #获取十大股东
            if db.session.query(exists().where(StockShareHolder.reportDate == targetDate).where(StockShareHolder.code == item.code).where(StockShareHolder.category == 1)).scalar() == False:
                ltRes = requests.get(GD_URL % (item.code, targetDate))
                ltData = ltRes.json()['data']
                for dt in ltData:
                    holder = StockShareHolder()
                    holder.code = item.code
                    holder.name = item.name
                    holder.holderType = dt["SHAREHDTYPE"]
                    holder.holderName = dt["SHAREHDNAME"]
                    holder.stockType = dt["SHARESTYPE"]
                    holder.holdQuantity = dt["SHAREHDNUM"]
                    holder.stockPercent = float(dt["SHAREHDRATIO"]) * float(100)
                    holder.change = dt["BZ"]
                    holder.changeQuantity = None
                    holder.category = 1
                    holder.reportDate = targetDate
                    db.session.add(holder)

                db.session.commit()
                time.sleep(200)

            
            # break


    finally:
        db.session.close()


def refresh_continue_buyAndSold():
    try:
        qResults = db.session.query(NorthFlow.recordDate, func.count(NorthFlow.id)).group_by(NorthFlow.recordDate).order_by(NorthFlow.recordDate.desc()).limit(30)
        dateList = [item[0] for item in qResults]
        startDate = dateList[len(dateList) - 1]
        endDate = dateList[0]
        queries = db.session.query(NorthFlow).filter(NorthFlow.recordDate == endDate)
        codes = [item.hkcode for item in queries]

        # print(cbuyList)
        for code in codes:
            queries = db.session.query(NorthFlow).filter(NorthFlow.recordDate >= startDate, NorthFlow.hkcode == code).order_by(NorthFlow.recordDate.desc())
            useContinueBuy  = False 
            useContinueSold = False
            firstItem = None
            for i, item in enumerate(queries):
                # print(i, item.recordDate)
                if i == 0:
                    if item.oneDayIncre == None:
                        break 

                    if item.oneDayIncre > 0:
                        item.continueBdays = 1
                        useContinueBuy = True
                    
                    if item.oneDayIncre < 0:
                        item.continueSdays = 1
                        useContinueSold = True 
                    
                    firstItem = item

                else:
                    if item.oneDayIncre == None:
                        continue

                    if useContinueBuy:
                        if item.oneDayIncre > 0:
                            firstItem.continueBdays = firstItem.continueBdays + 1

                        if item.oneDayIncre < 0:
                            break 

                    if useContinueSold:
                        if item.oneDayIncre < 0:
                            firstItem.continueSdays = firstItem.continueSdays + 1

                        if item.oneDayIncre > 0:
                            break

            # print(code)
        db.session.commit()

    finally:
        db.session.close()


def __getClosePrice(code, recordDate, source):
    if source != 'hk':
        record = db.session.query(DailyRecord).filter(DailyRecord.code == code, DailyRecord.close != None, DailyRecord.close != 0).order_by(DailyRecord.recordDate.desc()).first()
        return record.close if record != None else decimal.Decimal(0.0) 
    else:
        record = db.session.query(HkDailyRecord).filter(HkDailyRecord.code == code, HkDailyRecord.close != None, HkDailyRecord.close != 0).order_by(HkDailyRecord.recordDate.desc()).first()
        return record.close if record != None else decimal.Decimal(0.0)


# def refreshHkCode():

#     try:
#         nf = db.session.query(NorthFlow).filter(NorthFlow.source == 'hk').order_by(NorthFlow.recordDate.desc()).first()
#         lastDate = nf.recordDate  

#         queries = db.session.query(NorthFlow).filter(NorthFlow.recordDate == lastDate, NorthFlow.source == 'hk')
#         for item in queries:
#             item.stockcode = helper.transLongHkCodeFromHkCode(item.hkcode)

#         db.session.commit()
#         print('completed.')


#     finally:
#         db.session.close()
    
    





