
#helper module 
import tushare as ts 
import decimal
import hashlib
import pandas as pd
from .tradeday import trade_days

def transToCodeFromHkCode(hkcode):
    if hkcode[:1] == '9':
        return '60' + hkcode[1:]

    if hkcode[:1] == '7':
        if hkcode[:2] == '77':
            return '300' + hkcode[2:]
        else:
            return '00' + hkcode[1:]

def transLongHkCodeFromHkCode(hkcode):
    codeLen = len(str(hkcode))
    if codeLen >= 5:
        return codeLen 
    diff = 5 - codeLen

    return ('0' * diff) + str(hkcode)

def amountWithUnit(amount):
    if amount == None:
        return None 

    if abs(amount / decimal.Decimal(10000)) >= decimal.Decimal(10000):
        return '%.2f亿' % (amount / decimal.Decimal(100000000)).quantize(decimal.Decimal('.01'), rounding='ROUND_HALF_UP')
    else:
        return '%.2f万' % (amount / decimal.Decimal(10000)).quantize(decimal.Decimal('.01'), rounding='ROUND_HALF_UP')

def encodePassword(pwd):
    md5 = hashlib.md5()
    md5.update(pwd.encode('utf8'))
    return md5.hexdigest()

def isEmpty(str):
    return str == None or str.strip() == ''

#获取从某个交易日之前的N个交易日列表
def getPreTradeDays(startDate, preDays):
    cindex = trade_days.index(startDate)
    return trade_days[(cindex-preDays+1):(cindex+1)]

def convertToFloat(strval):
    try:
        return float(strval)
    except ValueError:
        return None

# def calculateGoldenCross(dataList, colName):
#     #dataList [{'date':'xxx', 'price':'xxx', 'colName': 'colVal', 'cross': 'gold/die'}]
#     df = pd.DataFrame(dataList)
#     df[colName] = df[colName].astype(float)

#     ma_list = [5,10,20]
#     for ma in ma_list:
#         df['ma' + str(ma)] = df[colName].rolling(center=False, window=ma).mean()

#     rtList = []
#     cicle = 0
#     for index, row in df.iterrows():
#         ma5 = row['ma5']
#         ma10 = row['ma10']
#         ma20 = row['ma20']
#         row['cross'] = ''
#         rtList.append(row)
#         if ma5 != None and ma10 != None and ma20 != None:
#             if ma5 < ma10:

# def _findCross(index, rows):
#     while index < len(rows):
#         ma5 = rows[index]['ma5']
#         ma10 = rows[index]['ma10']
#         ma20 = rows[index]['ma20'] 




