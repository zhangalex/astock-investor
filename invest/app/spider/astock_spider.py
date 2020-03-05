import requests
import re
from bs4 import BeautifulSoup
from datetime import datetime
from sqlalchemy.sql import exists
from pypinyin import pinyin, lazy_pinyin
import pypinyin
import csv 
import tushare as ts
import pandas as pd 

from app import db
from app import app
from app.models.main import Msci
from app.models.main import StockBasic, StockFinanceMain, DailyRecord, StockIndustry

import datetime
import time

import json
import demjson

#http://nufm.dfcfw.com/EM_Finance2014NumericApplication/JS.aspx?type=CT&cmd=C._HKS&sty=FCOQB&sortType=C&sortRule=-1&page=1&pageSize=100&js=var%20quote_123%3d{rank:[(x)],pages:(pc)}&token=7bc05d0d4c3c22ef9fca8c2a912d779c&jsName=quote_123&_g=0.7851060561209007

def fetch_msci():

    try:
        url = 'http://nufm.dfcfw.com/EM_Finance2014NumericApplication/JS.aspx?type=CT&cmd=C.BK08211&sty=FCOIATA&sortType=C&sortRule=-1&page=1&pageSize=251&js=var%20quote_123%3d{rank:[(x)],pages:(pc)}&token=7bc05d0d4c3c22ef9fca8c2a912d779c&jsName=quote_123&_g=0.25177081925437017'
        res = requests.get(url)
        text = res.text 
        _, data = text.split('=')
        py_obj = demjson.decode(data)
        db.session.query(Msci).delete()

        for item in py_obj['rank']:
            vals = item.split(',')
            code = vals[1]
            name = vals[2]
            pys = pinyin(name, style=pypinyin.FIRST_LETTER)
            pyname = ''.join([i[0] for i in pys])
            if db.session.query(exists().where(Msci.code == code)).scalar() == False:
                    item = Msci(code, name, '', pyname) 
                    db.session.add(item)
                    db.session.commit()
                    print('%s =----------------------------------->' % code)

        updateMsciIndustry()

    finally:
        db.session.close()

def updateGrowthRate():
    try:
        queries = db.session.query(Msci)
        for msci in queries:
            print(msci.name)

    finally:
        db.session.close()

def refreshBasicInfo():
    try:
        # db.session.query(StockBasic).delete()
        df = ts.get_stock_basics()
        df = df.astype(object).where(pd.notnull(df), None)
        #[df.columns.tolist()] + df.reset_index().values.tolist()
        dx = df.reset_index().values.tolist()
        #['300026','红日药业', '中成药', '天津', 22.99, 22.46, 30.11, 738695.5, 375573.72,
        #108218.02, 61736.45, 0.21, 0.15, 2.11, 2.18, 20091030, 259275.8,
        #0.86, -11.93, -5.31, 71.65, 18.88, 71907.0]
        for item in dx:
            stock = db.session.query(StockBasic).filter(StockBasic.code == item[0]).first()
            isCreate = False
            if stock == None:
                stock = StockBasic()
                stock.code = item[0]
                isCreate = True

            stock.name = item[1].replace(' ','')
            stock.industry = item[2] if item[2] != None else ''
            stock.area = item[3] if item[3] != None else ''
            
            stock.pe = item[4]
            stock.outstanding = item[5]
            stock.totals = item[6]
            stock.totalAssets = item[7]
            stock.liquidAssets = item[8]
            stock.fixedAssets = item[9]
            stock.reserved = item[10]
            stock.reservedPerShare = item[11]
            stock.esp = item[12]
            stock.bvps = item[13]
            stock.pb = item[14]
            if(str(item[15]) != '' and str(item[15]) != '0'):
                stock.timeToMarket = datetime.datetime.strptime(str(item[15]),'%Y%m%d')

            stock.undp = item[16]
            stock.perundp = item[17]
            stock.rev = item[18]
            stock.profit = item[19]
            stock.gpr = item[20]
            stock.npr = item[21]
            stock.holders = item[22]

            if stock.timeToMarket != None:
                stock.tomarketYear = stock.timeToMarket.strftime('%Y')
                stock.tomarketYearMonth = stock.timeToMarket.strftime('%Y%m')

            if isCreate == True: 
                db.session.add(stock)

            db.session.commit()

    finally:
        db.session.close()

# def refreshStockFinanceMain(year, quarter):
#     try:
#         df = ts.get_report_data(year, quarter)
#         values = df.values 
#         for item in values:
#             stock = db.session.query(StockFinanceMain).filter(StockFinanceMain.code == item[0], StockFinanceMain.year == year, StockFinanceMain.quarter == quarter).first()
#             if stock == None:
#                 stock = StockFinanceMain()
#                 stock.code = item[0]
#                 stock.name = item[1]
#                 stock.year = year
#                 stock.quarter = quarter
#                 stock.code = item[0]
#                 stock.code = item[0]
#                 stock.code = item[0]
#                 stock.code = item[0]
#                 stock.code = item[0]

#     finally:
#         db.session.close()


def updateMsciIndustry():
    try:
        queries = db.session.query(Msci)
        for msci in queries:
            ins = db.session.query(StockBasic).filter(StockBasic.code == msci.code).first()
            if ins != None:
                msci.industry = ins.industry
                db.session.commit()

    finally:
        db.session.close()

def warmDailyRecord():
    ROOT_PATH = app.config['DAILY_DATA_PATH']
    dates = ['20171128.csv', '20171201.csv', '20171206.csv', '20171211.csv', '20171214.csv', '20171219.csv', '20171222.csv', '20171227.csv',
'20171129.csv', '20171204.csv', '20171207.csv', '20171212.csv', '20171215.csv', '20171220.csv', '20171225.csv', '20171228.csv',
'20171130.csv', '20171205.csv', '20171208.csv', '20171213.csv', '20171218.csv', '20171221.csv', '20171226.csv', '20171229.csv']
    for i, item in enumerate(sorted(dates)):
        filePath = '%s%s' % (ROOT_PATH, item)
        index = i + 1
        input_file = csv.DictReader(open(filePath))
        date = time.strptime(item.replace('.csv',''), '%Y%m%d')
        recordDate = time.strftime('%Y-%m-%d', date)
        for row in input_file:
            record = DailyRecord()
            record.code = row['code']
            record.name = row['name']
            record.changepercent = '%.4f' % float(row['changepercent'])
            record.close = '%.4f' % float(row['trade'])
            record.open = '%.4f' % float(row['open'])
            record.high = '%.4f' % float(row['high'])
            record.low = '%.4f' % float(row['low'])
            record.settlement = '%.4f' % float(row['settlement'])
            record.volume = '%.4f' % float(row['volume'])
            record.turnoverratio = '%.4f' % float(row['turnoverratio'])
            record.amount = '%.4f' % float(row['amount'])
            record.per = '%.4f' % float(row['per'])
            record.pb = '%.4f' % float(row['pb'])
            record.mktcap = float(row['mktcap']) * 10000
            record.nmc = float(row['nmc']) * 10000
            record.recordDate = recordDate
            record.recordIndex = index
            # print(record.as_dict())
            db.session.add(record)

        db.session.commit() 
        print('>> %s' % recordDate)
        # break

def fetchHkRecords():
    url = 'http://nufm.dfcfw.com/EM_Finance2014NumericApplication/JS.aspx?type=CT&cmd=C._HKS&sty=FCOQB&sortType=C&sortRule=-1&page=%s&pageSize=100&js=var quote_123={rank:[(x)],pages:(pc)}&token=7bc05d0d4c3c22ef9fca8c2a912d779c&jsName=quote_123&_g=0.7851060561209007' 
    columns = ['code', 'name', 'volume', 'amount', 'close', 'change', 'changepercent', 'open', 'high', 'low', 'settlement']
    rows = [] 
    for page in range(1, 23):
        res = requests.get(url)
        text = res.text 
        _, data = text.split('=')
        py_obj = demjson.decode(data)
        items = py_obj['rank']
        for item in items:
            dc = {} 
            arrays = item.split(',')
            dc['code']          = arrays[0]
            dc['name']          = arrays[1]
            dc['close']         = arrays[2]
            dc['change']        = arrays[3]
            dc['changepercent'] = arrays[4].replace('%','')
            dc['volume']        = arrays[5]
            dc['amount']        = arrays[6]
            dc['open']          = arrays[7]
            dc['high']          = arrays[8]
            dc['low']           = arrays[9]
            dc['settlement']    = arrays[10]
            rows.append(dc)

        # print('#')

    return rows 

def updateSwSecondIndustry():
    df = pd.read_excel('/Users/Raymond/Downloads/swsecond.xlsx',converters={'股票代码':str})
    rlist = df.to_dict('records')
    source = 'sw'
    level  = 2
    db.session.query(StockIndustry).delete()

    for item in rlist:
        code, industry = [item['股票代码'], item['行业名称']]   
        ins = db.session.query(StockIndustry).filter(StockIndustry.source == source, StockIndustry.level == level, StockIndustry.code == code).first()
        if ins == None:
            ins = StockIndustry(code, industry, source, level)
            db.session.add(ins)
        else:
            ins.name = industry

    db.session.commit()

def refreshDailyRecord(recordDate):
    ROOT_PATH = app.config['DAILY_DATA_PATH']
    filePath = '%s%s.csv' % (ROOT_PATH, recordDate.replace('-', ''))


    if db.session.query(exists().where(DailyRecord.recordDate == recordDate)).scalar() == False:
        print('%s is not exist data' % recordDate)
        return 

    input_file = csv.DictReader(open(filePath))

    existedList = []
    for row in input_file:
        if row['code'] in existedList:
            continue
        else:
            existedList.append(row['code'])

        record = db.session.query(DailyRecord).filter(DailyRecord.recordDate == recordDate, DailyRecord.code == row['code']).first()
        if record == None:
            continue

        record.code = row['code']
        record.name = row['name']
        record.changepercent = '%.4f' % float(row['changepercent'])
        record.close = '%.4f' % float(row['trade'])
        record.open = '%.4f' % float(row['open'])
        record.high = '%.4f' % float(row['high'])
        record.low = '%.4f' % float(row['low'])
        record.settlement = '%.4f' % float(row['settlement'])
        record.volume = '%.4f' % float(row['volume'])
        record.turnoverratio = '%.4f' % float(row['turnoverratio'])
        record.amount = '%.4f' % float(row['amount'])
        record.per = '%.4f' % float(row['per'])
        record.pb = '%.4f' % float(row['pb'])
        record.mktcap = float(row['mktcap']) * 10000
        record.nmc = float(row['nmc']) * 10000

        db.session.commit() 

    print('refresh completed !')
