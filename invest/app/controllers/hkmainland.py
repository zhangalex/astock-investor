from flask import Blueprint, request, jsonify
from sqlalchemy import func
from sqlalchemy.sql import exists
from flask_jwt_extended import (jwt_required, get_jwt_identity, get_jwt_claims)

import datetime
import requests
import decimal
import operator
import demjson
import re
from operator import itemgetter
# Import the database object from the main app module
from app import db
from app import app
from app.models.main import NorthFlow, Msci, AttentionStocks, StockBasic, NorthStatistics, StockShareHolder, User, ShortStat, Participant, XueqiuStockStat, DailyRecord
from app.common import helper, const
from app.services import dailytrade_service

bprint = Blueprint('hkmainland', __name__, url_prefix='/api/v1.0/hkmainland')

@bprint.route('/north_flows')
@jwt_required
def north_flows():
    onlyShowAttention = request.args.get('attention') == 'true'
    searchValue       = request.args.get('searchValue') if (request.args.get('searchValue') != None and request.args.get('searchValue') != '') else None
    sourceValue       = request.args.get('source') if (request.args.get('source') != None and request.args.get('source') != '') else None
    onlyQueryMSCI     = request.args.get('msci') == 'true'
    rts = []
    
    columns = [
        {'name': 'stockcode',        'type': 'stockcode',  'title': '代码', 'sortable': False},
        {'name': 'stockname',     'type': 'custom',  'title': '名称'},
        {'name': 'holdQuantity',  'type': 'numeric',  'title': '持股量'},
        {'name': 'holdMarketValue',  'type': 'amount',  'title': '持有市值'},
        {'name': 'circularPercent', 'type': 'percent', 'title': '流通占比'},
        {'name': 'oneDayIncre',   'type': 'numeric',  'title': '1日增量'},
        {'name': 'fiveDayIncre',  'type': 'numeric',  'title': '5日增量'},
        {'name': 'oneDayAmount',    'type': 'amount',  'title': '1日买/卖金额'},
        {'name': 'isAttention',   'type': 'attention',  'title': '关注', 'sortable': False}
    ]
   

    current_user = db.session.query(User).filter(User.mobile == get_jwt_identity()).first()

    orderBy        = request.args.get('orderBy')
    orderDirection = request.args.get('orderDirect')
    page           = request.args.get('page')
    per_page       = request.args.get('perPage')

    if orderBy == None or orderBy == '':
        orderBy        = 'circularPercent'
        orderDirection = 'desc'

    if page == None or page =='':
        page = 1

    if per_page == None or per_page == '':
        per_page = 10

    lastDate = None
    if sourceValue != None:
        if sourceValue == 'myliked':
            nf = db.session.query(NorthFlow).order_by(NorthFlow.recordDate.desc()).first()
            lastDate = nf.recordDate
        else:
            nf = db.session.query(NorthFlow).filter(NorthFlow.source == sourceValue).order_by(NorthFlow.recordDate.desc()).first()
            lastDate = nf.recordDate
    else:
        nf = db.session.query(NorthFlow).filter(NorthFlow.source != 'hk').order_by(NorthFlow.recordDate.desc()).first()
        lastDate = nf.recordDate

    # result = NorthFlow.query.outerjoin(AttentionStocks, NorthFlow.hkcode == AttentionStocks.hkcode).outerjoin(Msci, NorthFlow.stockname == Msci.name).filter(NorthFlow.recordDate == lastDate, NorthFlow.astockPercent > 0)
    result = NorthFlow.query.outerjoin(AttentionStocks, (NorthFlow.stockcode == AttentionStocks.code) & (AttentionStocks.user_id == current_user.id)).filter(NorthFlow.recordDate == lastDate, NorthFlow.holdQuantity > 0)

    if onlyQueryMSCI == True:
        result = result.outerjoin(Msci, (Msci.code == NorthFlow.stockcode)).filter(Msci.code != None) 
    
    if searchValue != None:
        if re.match("\d+", searchValue):
            result = result.filter(NorthFlow.stockcode.like('' + searchValue + '%'))
        else:
            result = result.filter(NorthFlow.stockname.like('%' + searchValue + '%'))
    
    if sourceValue != None: 
        if sourceValue != 'myliked':
            result = result.filter(NorthFlow.source == sourceValue)
    else:
        result = result.filter(NorthFlow.source != 'hk')

    if onlyShowAttention == True: 
        result = result.filter(AttentionStocks.code !=None)

    

    queries = result.order_by(getattr(getattr(NorthFlow, orderBy), orderDirection)()).order_by(NorthFlow.id.asc()).paginate(int(page), int(per_page), True)

    pageInfo = {
        'total':   queries.total,  
        'current': int(page),  
        'pagenum': int(per_page), 
        'page':    queries.pages,
        'pagegroup': 5,    
        'skin':'#00D1B2'  
    }

    for item in queries.items:
        dic = item.as_dict() 
        dic['astockPercent'] = item.astockPercent/100  
        dic['circularPercent'] = item.circularPercent/100 
        dic['holdMarketValue'] = helper.amountWithUnit(item.holdMarketValue)
        dic['oneDayAmount'] = helper.amountWithUnit(item.oneDayAmount)
        dic['recordDate'] = item.recordDate.strftime("%Y-%m-%d")
        dic['stockname']   = dic['stockname'][:4]
        dic['isAttention'] = db.session.query(exists().where(AttentionStocks.code == item.stockcode).where(AttentionStocks.user_id == current_user.id)).scalar()    
        dic['isMsci']      = db.session.query(exists().where(Msci.code == item.stockcode)).scalar()   
        rts.append(dic)

     
    return jsonify({'list': rts, 'columns': columns, 'orderBy': orderBy, 'orderDirect': orderDirection, 'lastUpdate': lastDate.strftime('%Y-%m-%d'), 'pagination': pageInfo})

@bprint.route('/flow_detail')
@jwt_required
def flow_detail():
    hkcode        = request.args.get('hkcode')
    columns = [
         {'name': 'index',      'type': 'number',  'title': 'No.', 'sortable': False},
         {'name': 'stockname',     'type': 'string',  'title': '名称'},
         {'name': 'holdQuantity',  'type': 'numeric',  'title': '持股量'},
         {'name': 'holdMarketValue',  'type': 'amount',  'title': '持有市值'},
         {'name': 'circularPercent', 'type': 'percent', 'title': '占比'},
         {'name': 'recordDate', 'type': 'string', 'title': '日期'},
         {'name': 'oneDayIncre',   'type': 'numeric',  'title': '当日增量'},
        #  {'name': 'fiveDayIncre',  'type': 'numeric',  'title': '5日增量'},
        #  {'name': 'tenDayIncre',   'type': 'numeric',  'title': '10日增量'},
         {'name': 'oneDayAmount',    'type': 'amount',  'title': '当日买/卖金额'},
        #  {'name': 'fiveDayIncre',  'type': 'numeric',  'title': '5日增量'},
         
    ]
    queries = db.session.query(NorthFlow).filter(NorthFlow.hkcode == hkcode).order_by(NorthFlow.recordDate.desc()).limit(10)

    # index = (int(page) - 1) * int(per_page)
    index = 0
    dts = []
    for item in queries:
        index += 1
        dic = item.as_dict()
        dic['index'] = index
        dic['recordDate'] = item.recordDate.strftime("%Y-%m-%d")
        dic['circularPercent'] = item.circularPercent/100  if item.circularPercent != None else ''
        dic['holdMarketValue'] = helper.amountWithUnit(item.holdMarketValue)
        dic['oneDayAmount'] = helper.amountWithUnit(item.oneDayAmount)
        dts.append(dic)


    return jsonify({'list': dts, 'columns': columns})
    

@bprint.route('/north_chart')
@jwt_required
def north_chart():
    hkcode        = request.args.get('hkcode')
    startDate     = request.args.get('start') if (request.args.get('start') != None and request.args.get('start') != '') else None
    endDate       = request.args.get('end') if (request.args.get('end') != None and request.args.get('end') != '') else None
    #默认只显示过去六个月的数据 
    today = datetime.datetime.now()
    DD = datetime.timedelta(days=180)
    earlier = (today - DD).strftime("%Y-%m-%d")

    if startDate == None:
        startDate = earlier

    if endDate == None:
        endDate = today.strftime("%Y-%m-%d")

    queries = db.session.query(NorthFlow).filter(NorthFlow.hkcode == hkcode , NorthFlow.recordDate >= startDate, NorthFlow.recordDate <= endDate).order_by(NorthFlow.recordDate.asc())
    xData      = []
    yLineData  = []
    yBarData   = []

    for item in queries:
        xData.append(item.recordDate.strftime("%m%d"))
        yLineData.append(item.astockPercent)
        yBarData.append(item.holdQuantity)

    return jsonify({'stockName': queries[0].stockname, 'xData': xData, 'yBarData': yBarData, 'yLineData': yLineData, 'start': startDate, 'end': endDate})

@bprint.route('/attention', methods=['POST'])
@jwt_required
def attetion_stock():
    code = request.args.get('code')
    user = db.session.query(User).filter(User.mobile == get_jwt_identity()).first()
    if db.session.query(exists().where(AttentionStocks.code == code).where(AttentionStocks.user_id == user.id)).scalar() == False:
        atten = AttentionStocks(code, user.id)
        db.session.add(atten)
        db.session.commit()
        db.session.close()

    return jsonify({'code': 1, 'message': 'ok'})

@bprint.route('/attention', methods=['DELETE'])
@jwt_required
def remove_attetioned_stock():
    code = request.args.get('code')
    user = db.session.query(User).filter(User.mobile == get_jwt_identity()).first()
    atten = db.session.query(AttentionStocks).filter(AttentionStocks.code == code, AttentionStocks.user_id == user.id).first()
    if atten != None:
        db.session.delete(atten)
        db.session.commit()
        db.session.close() 

    return jsonify({'code': 1, 'message': 'ok'})


# @bprint.route('/fetch_stock')
# @jwt_required
# def fetch_stock():
#     code = request.args.get('code')
#     symbol = 'sh' + code if code[:1] == '6' else 'sz' + code
#     url = 'http://hq.sinajs.cn/list=%s' % symbol
#     res = requests.get(url)
#     return res.text

@bprint.route('/fetch_stock_notice')
@jwt_required
def fetch_stock_notice():
    try:
        code = request.args.get('code')
        url  = 'http://www.cninfo.com.cn/cninfo-new/disclosure/szse/fulltext'
        data = {'stock': code, 'searchkey': '', 'category': '', 'pageNum': 1, 'pageSize': 15, 'column': '', 'ssetabName': '', 'latestsortName': '', 'sortType': '', 'limit': '', 'seDate': ''}
        res  = requests.post(url, data = data)
        return res.text

    except Exception as e:
        app.logger.error(str(e))
        return jsonify([]) 

@bprint.route('/fetch_northflow_stats_hs')
@jwt_required
def fetch_northflow_stats_hs():
    queries = db.session.query(NorthStatistics).filter(NorthStatistics.source == 'hs').order_by(NorthStatistics.recordDate.desc()).limit(90)
    dts = []
    for item in queries:
        if item.buyCount == 0 and item.soldCount == 0 and item.buyAmount == 0 and item.soldAmount == 0:
            continue 

        dic = item.as_dict()
        dic['recordDate'] = item.recordDate.strftime("%Y-%m-%d")
        dic['buyAmount'] = (item.buyAmount / decimal.Decimal(100000000)).quantize(decimal.Decimal('.01'), rounding='ROUND_HALF_UP')
        dic['soldAmount'] = (item.soldAmount / decimal.Decimal(100000000)).quantize(decimal.Decimal('.01'), rounding='ROUND_HALF_UP')
        dic['netAmount'] = dic['buyAmount'] - dic['soldAmount']
        dts.append(dic)

    dts.reverse()
    return jsonify({'list': dts})

@bprint.route('/fetch_northflow_stats_hk')
@jwt_required
def fetch_northflow_stats_hk():
    queries = db.session.query(NorthStatistics).filter(NorthStatistics.source == 'hk').order_by(NorthStatistics.recordDate.desc()).limit(90)
    dts = []
    for item in queries:
        if item.buyCount == 0 and item.soldCount == 0 and item.buyAmount == 0 and item.soldAmount == 0:
            continue 

        dic = item.as_dict()
        dic['recordDate'] = item.recordDate.strftime("%Y-%m-%d")
        dic['buyAmount'] = (item.buyAmount / decimal.Decimal(100000000)).quantize(decimal.Decimal('.01'), rounding='ROUND_HALF_UP')
        dic['soldAmount'] = (item.soldAmount / decimal.Decimal(100000000)).quantize(decimal.Decimal('.01'), rounding='ROUND_HALF_UP')
        dic['netAmount'] = dic['buyAmount'] - dic['soldAmount']
        dts.append(dic)

    dts.reverse()
    return jsonify({'list': dts})

@bprint.route('/fetch_shareholders')
@jwt_required
def fetch_shareholders():
    code = request.args.get('code')
    holder = db.session.query(StockShareHolder).filter(StockShareHolder.code == code).order_by(StockShareHolder.reportDate.desc()).first()
    lastDate = holder.reportDate
    ltgdList = []
    gdList = []
    ltgdQ = db.session.query(StockShareHolder).filter(StockShareHolder.code == code, StockShareHolder.reportDate == lastDate, StockShareHolder.category == 0).order_by(StockShareHolder.reportDate.desc()).all()
    gddQ = db.session.query(StockShareHolder).filter(StockShareHolder.code == code, StockShareHolder.reportDate == lastDate, StockShareHolder.category == 1).order_by(StockShareHolder.reportDate.desc()).all()

    for item in ltgdQ:
        dic = item.as_dict()
        dic['reportDate'] = item.reportDate.strftime('%Y-%m-%d')
        dic['holdQuantity'] = helper.amountWithUnit(item.holdQuantity)
        ltgdList.append(dic)

    for item in gddQ:
        dic = item.as_dict()
        dic['reportDate'] = item.reportDate.strftime('%Y-%m-%d')
        dic['holdQuantity'] = helper.amountWithUnit(item.holdQuantity)
        # dic['isRed'] = item.change == '增加' or item.change == '新进'
        # dic['isGreen'] = item.change == '减少'
        gdList.append(dic)

    return jsonify({'ltgdList': ltgdList, 'gdList': gdList, 'reportDate': lastDate.strftime('%Y-%m-%d')})

@bprint.route('/flow_continue')
@jwt_required
def flow_continue():
    rts = []
    columns = [
         {'name': 'code',        'type': 'stockcode',  'title': '代码', 'sortable': False},
         {'name': 'stockname',     'type': 'custom',  'title': '名称'},
        #  {'name': 'holdQuantity',  'type': 'numeric',  'title': '持股量'},
         {'name': 'holdMarketValue',  'type': 'amount',  'title': '持有市值'},
         {'name': 'circularPercent', 'type': 'percent', 'title': '流通占比'},
        #  {'name': 'oneDayIncre',   'type': 'numeric',  'title': '1日增量'},
         {'name': 'oneDayAmount',    'type': 'amount',  'title': '1日增减金额'},
    ]
    direction = request.args.get('direction')
    if direction == 'buy':
        columns.append({'name': 'continueBdays',   'type': 'numeric',  'title': '连续买入(天)', 'class': 'buy'})
        columns.append({'name': 'buyChangePercent',   'type': 'percent',  'title': '期间涨跌', 'sortable': False}) 

    if direction == 'sold':
        columns.append({'name': 'continueSdays',   'type': 'numeric',  'title': '连续卖出(天)', 'class': 'sold'})
        columns.append({'name': 'soldChangePercent',   'type': 'percent',  'title': '期间涨跌', 'sortable': False}) 

    
    columns.append({'name': 'changeAmount',   'type': 'amount',  'title': '期间增减金额', 'sortable': False}) 
    columns.append({'name': 'isAttention',   'type': 'attention',  'title': '关注', 'sortable': False}) 

    current_user = db.session.query(User).filter(User.mobile == get_jwt_identity()).first()

    orderBy        = request.args.get('orderBy')
    orderDirection = request.args.get('orderDirect')
    page           = request.args.get('page')
    per_page       = request.args.get('perPage')
    days           = request.args.get('days')
    sourceValue    = request.args.get('source')

    if orderBy == None or orderBy == '':
        orderBy        = 'circularPercent'
        orderDirection = 'desc'
        if direction == 'buy':
            orderBy = 'continueBdays'

        if direction == 'sold':
            orderBy = 'continueSdays'


    if page == None or page =='':
        page = 1

    if per_page == None or per_page == '':
        per_page = 12

    if sourceValue != 'hk':
        nf = db.session.query(NorthFlow).filter(NorthFlow.source != 'hk').order_by(NorthFlow.recordDate.desc()).first()
        lastDate = nf.recordDate
        queries = db.session.query(NorthFlow).filter(NorthFlow.recordDate == lastDate, NorthFlow.astockPercent > 0, NorthFlow.source != 'hk')
    else:
        nf = db.session.query(NorthFlow).filter(NorthFlow.source == 'hk').order_by(NorthFlow.recordDate.desc()).first()
        lastDate = nf.recordDate
        queries = db.session.query(NorthFlow).filter(NorthFlow.recordDate == lastDate, NorthFlow.astockPercent > 0, NorthFlow.source == 'hk')

    if direction == 'buy'  and days != None:
        queries = queries.filter(NorthFlow.continueBdays == days)

    if direction == 'sold'  and days != None:
        queries = queries.filter(NorthFlow.continueSdays == days)

    queries = queries.order_by(getattr(getattr(NorthFlow, orderBy), orderDirection)()).order_by(NorthFlow.id.asc()).paginate(int(page), int(per_page), True)

    pageInfo = {
        'total':   queries.total,  
        'current': int(page),  
        'pagenum': int(per_page), 
        'page':    queries.pages,
        'pagegroup': 5,    
        'skin':'#00D1B2'  
    }

    for item in queries.items:
        dic = item.as_dict() 
        oneDayAmount = None 
        dic['stockname']   = dic['stockname'][:6]
        dic['circularPercent'] = item.circularPercent/100   
        dic['code'] = item.stockcode
        dic['oneDayAmount'] = helper.amountWithUnit(item.oneDayAmount)
        dic['holdMarketValue'] = helper.amountWithUnit(item.holdMarketValue)
        dic['isAttention'] = db.session.query(exists().where(AttentionStocks.code == item.stockcode).where(AttentionStocks.user_id == current_user.id)).scalar()    
        dic['buyChangePercent'] = None 
        dic['soldChangePercent'] = None 

        if direction == 'buy' and item.continueBdays != None and item.continueBdays > 0: 
            dic['buyChangePercent'] = dailytrade_service.getPastDaysChangePercent(item.stockcode, item.continueBdays, sourceValue)
            dic['changeAmount'] = helper.amountWithUnit(dailytrade_service.getPastDaysChangeAmount(item.stockcode, item.continueBdays))

        if direction == 'sold' and item.continueSdays != None and item.continueSdays > 0: 
            dic['soldChangePercent'] = dailytrade_service.getPastDaysChangePercent(item.stockcode, item.continueSdays, sourceValue)
            dic['changeAmount'] = helper.amountWithUnit(dailytrade_service.getPastDaysChangeAmount(item.stockcode, item.continueSdays))


        rts.append(dic)

     
    return jsonify({'list': rts, 'columns': columns, 'orderBy': orderBy, 'orderDirect': orderDirection, 'lastUpdate': lastDate.strftime('%Y-%m-%d'), 'pagination': pageInfo})


@bprint.route('/shareholder_relation')
@jwt_required
def shareholder_relation():
    name     = request.args.get('name')
    category = request.args.get('category')

    page           = request.args.get('page')
    per_page       = request.args.get('perPage')

    if page == None or page =='':
        page = 1

    if per_page == None or per_page == '':
        per_page = 10

    columns = [
        {'name': 'code', 'type': 'string',  'title': '代码', 'sortable': False},
        {'name': 'name', 'type': 'string',  'title': '名称', 'sortable': False},
        {'name': 'stockPercent', 'type': 'percent',  'title': '持股占比', 'sortable': False}
    ]

    queries = db.session.query(StockShareHolder).filter(StockShareHolder.holderName == name, StockShareHolder.category == category).order_by(StockShareHolder.stockPercent.desc()).order_by(StockShareHolder.id.asc()).paginate(int(page), int(per_page), True)

    pageInfo = {
        'total':   queries.total,  
        'current': int(page),  
        'pagenum': int(per_page), 
        'page':    queries.pages,
        'pagegroup': 5,    
        'skin':'#00D1B2'  
    }

    rts = [{'code': item.code, 'name': item.name, 'stockPercent': item.stockPercent/100} for item in queries.items]

    return jsonify({'list': rts, 'columns': columns, 'pagination': pageInfo})


@bprint.route('/industry_holdquantity')
@jwt_required
def industry_holdquantity():
    nf = db.session.query(NorthFlow).filter(NorthFlow.source != 'hk').order_by(NorthFlow.recordDate.desc()).first()
    lastDate = nf.recordDate    
    queries = db.session.query(NorthFlow).filter(NorthFlow.recordDate == lastDate, NorthFlow.source != 'hk')

    basicResult = db.session.query(StockBasic).with_entities(StockBasic.code, StockBasic.industry)
    industryItems = {item.code: item.industry for item in basicResult}

    rt = {}
    for item in queries:
        # basicInfo = db.session.query(StockBasic).filter(StockBasic.code == item.stockcode).first()
        key = industryItems[item.stockcode]
        if rt.get(key):
            rt[key] = rt[key] + item.circularPercent
        else:
            rt[key] = item.circularPercent

    sorted_x = sorted(rt.items(), key=operator.itemgetter(1))

    return jsonify({'stats': sorted_x})

@bprint.route('/fetch_regular_reports')
@jwt_required
def fetch_regular_reports():
    try:
        code = request.args.get('code')
        #年度报告
        ndbg_url   = 'http://www.cninfo.com.cn/disclosure/annualreport/stocks/ar1y/cninfo/%s.js?ver=201712191434' % code 
        bndbg_url  = 'http://www.cninfo.com.cn/disclosure/seannualreport/stocks/sar1y/cninfo/%s.js?ver=201712191459' % code 
        yjdbg_url  = 'http://www.cninfo.com.cn/disclosure/1qreport/stocks/1qr1y/cninfo/%s.js?ver=201712191500' % code 
        sjdbg_url  = 'http://www.cninfo.com.cn/disclosure/3qreport/stocks/3qr1y/cninfo/%s.js?ver=201712191500' % code 
        reports = []
        for url in [ndbg_url, bndbg_url, yjdbg_url, sjdbg_url]:
            res       = requests.post(url)
            res.encoding = 'gb2312'
            _, tmpData   = res.text.split('=')
            rtArray      = demjson.decode(tmpData[:-2])
            for item in rtArray:
                reports.append(item)

        st = [{'code': item[0], 'url': 'http://www.cninfo.com.cn/%s' % item[1], 'title': item[2], 'date': item[5]} for item in reports]

        return jsonify(st)

    except Exception as e:
        app.logger.error(str(e))
        return jsonify([])


@bprint.route('/wz_holders')
@jwt_required
def wz_holders():
    stockcode     = request.args.get('stockcode')
    recordDate     = request.args.get('recordDate')
    rts = []
    columns = [
        #  {'name': 'code',        'type': 'string',  'title': '编码', 'sortable': False},
         {'name': 'name',        'type': 'holder',  'title': '参与者名称', 'sortable': False},
         {'name': 'holdQuantity',  'type': 'numeric',  'title': '持股量'},
         {'name': 'holdMarketValue',  'type': 'amount',  'title': '持有市值'},
         {'name': 'stockPercent',  'type': 'percent',  'title': '占比'},
        #  {'name': 'oneDayIncre',   'type': 'numeric',  'title': '1日增量'},
         {'name': 'oneDayAmount',   'type': 'amount',  'title': '1日增额'},
        #  {'name': 'fiveDayIncre',  'type': 'numeric',  'title': '5日增量'},
         
    ]
    # if request.args.get('isLongColumn') == '1':
        # columns.append({'name': 'oneDayAmount',    'type': 'amount',  'title': '1日增额'})

    orderBy        = request.args.get('orderBy')
    orderDirection = request.args.get('orderDirect')
    page           = request.args.get('page')
    per_page       = request.args.get('perPage')

    if orderBy == None or orderBy == '':
        orderBy        = 'stockPercent'
        orderDirection = 'desc'

    if page == None or page =='':
        page = 1

    if per_page == None or per_page == '':
        per_page = 15

    if recordDate == None or recordDate == '':
        recordDate = db.session.query(Participant).order_by(Participant.recordDate.desc()).limit(1).first().recordDate.strftime("%Y-%m-%d")


    queries = db.session.query(Participant).filter(Participant.recordDate == recordDate, Participant.stockcode == stockcode)
    queries = queries.order_by(getattr(getattr(Participant, orderBy), orderDirection)()).order_by(Participant.id.asc()).paginate(int(page), int(per_page), True)

    pageInfo = {
        'total':   queries.total,  
        'current': int(page),  
        'pagenum': int(per_page), 
        'page':    queries.pages,
        'pagegroup': 5,    
        'skin':'#00D1B2'  
    }

    for item in queries.items:
        dic = item.as_dict() 
        # oneDayAmount = None 
        # # q = db.session.query(Participant).filter(Participant.code == item.code, Participant.stockcode == stockcode, Participant.recordDate == preDate).first()
        # if q != None:
        #     qtyDiff = item.holdQuantity - q.holdQuantity
        #     dic['oneDayIncre'] = qtyDiff
        #     # dic['oneDayAmount'] = helper.amountWithUnit((item.holdQuantity - q.holdQuantity) * dailytrade_service.getClosePrice(stockcode, item.source))
        # else:
        #     dic['oneDayIncre'] = item.holdQuantity
        #     dic['oneDayAmount'] = None


        dic['stockPercent'] = item.stockPercent/100   
        dic['holdMarketValue'] = helper.amountWithUnit(item.holdMarketValue)
        dic['oneDayAmount'] = helper.amountWithUnit(item.oneDayAmount) if item.oneDayAmount != None else None

        rts.append(dic)

     
    return jsonify({'list': rts, 'columns': columns, 'orderBy': orderBy, 'orderDirect': orderDirection, 'lastUpdate': recordDate, 'pagination': pageInfo})

@bprint.route('/holders_chart')
@jwt_required
def holders_chart():
    stockcode        = request.args.get('stockcode')
    code             = request.args.get('code')
    startDate     = request.args.get('start') if (request.args.get('start') != None and request.args.get('start') != '') else None
    endDate       = request.args.get('end') if (request.args.get('end') != None and request.args.get('end') != '') else None
    #默认只显示过去六个月的数据 
    today = datetime.datetime.now()
    DD = datetime.timedelta(days=180)
    earlier = (today - DD).strftime("%Y-%m-%d")

    if startDate == None:
        startDate = earlier

    if endDate == None:
        endDate = today.strftime("%Y-%m-%d")

    queries = db.session.query(Participant).filter(Participant.stockcode == stockcode, Participant.code == code, Participant.recordDate >= startDate, Participant.recordDate <= endDate).order_by(Participant.recordDate.asc())
    xData      = []
    yLineData  = []
    yBarData   = []

    for item in queries:
        xData.append(item.recordDate.strftime("%m%d"))
        yLineData.append(item.stockPercent)
        yBarData.append(item.holdQuantity)

    return jsonify({'stockName': queries[0].name, 'xData': xData, 'yBarData': yBarData, 'yLineData': yLineData, 'start': startDate, 'end': endDate})

@bprint.route('/holders_analysis')
@jwt_required
def holders_analysis():
    code           = request.args.get('code')
    recordDate     = request.args.get('recordDate')
    stocksource     = request.args.get('source')

    rts = []
    columns = [
         {'name': 'stockcode',        'type': 'stockcode',  'title': '代码', 'sortable': False},
         {'name': 'stockname',        'type': 'string',  'title': '名称', 'sortable': False},
         {'name': 'holdQuantity',  'type': 'numeric',  'title': '持股量'},
         {'name': 'holdMarketValue',  'type': 'amount',  'title': '持有市值'},
         {'name': 'stockPercent',  'type': 'percent',  'title': '占比'},
         {'name': 'oneDayIncre',   'type': 'numeric',  'title': '1日增量'},
         {'name': 'oneDayAmount',    'type': 'amount',  'title': '1日增额'}
         
    ]
    if request.args.get('isLongColumn') == '1':
        columns.append({'name': 'oneDayAmount',    'type': 'amount',  'title': '1日增额'})

    orderBy        = request.args.get('orderBy')
    orderDirection = request.args.get('orderDirect')
    page           = request.args.get('page')
    per_page       = request.args.get('perPage')

    if orderBy == None or orderBy == '':
        orderBy        = 'holdMarketValue'
        orderDirection = 'desc'

    if page == None or page =='':
        page = 1

    if per_page == None or per_page == '':
        per_page = 12

    if recordDate == None or recordDate == '':
        recordDate = db.session.query(Participant).order_by(Participant.recordDate.desc()).limit(1).first().recordDate.strftime("%Y-%m-%d")


    queries = db.session.query(Participant).filter(Participant.recordDate == recordDate, Participant.code == code)
    if stocksource != None:
        if stocksource == 'hs':
            queries = queries.filter(Participant.source != 'hk')
        elif stocksource == 'hk':
            queries = queries.filter(Participant.source == 'hk')


    queries = queries.order_by(getattr(getattr(Participant, orderBy), orderDirection)()).order_by(Participant.id.asc()).paginate(int(page), int(per_page), True)

    pageInfo = {
        'total':   queries.total,  
        'current': int(page),  
        'pagenum': int(per_page), 
        'page':    queries.pages,
        'pagegroup': 5,    
        'skin':'#00D1B2'  
    }

    for item in queries.items:
        dic = item.as_dict() 

        nf = db.session.query(NorthFlow).filter(NorthFlow.recordDate == recordDate, NorthFlow.stockcode == item.stockcode).first()

        dic['stockname'] = nf.stockname[:6]

        dic['stockPercent'] = item.stockPercent/100   
        dic['holdMarketValue'] = helper.amountWithUnit(item.holdMarketValue)
        dic['oneDayAmount'] = helper.amountWithUnit(item.oneDayAmount) if item.oneDayAmount != None else None

        rts.append(dic)

     
    return jsonify({'list': rts, 'columns': columns, 'orderBy': orderBy, 'orderDirect': orderDirection, 'lastUpdate': recordDate, 'pagination': pageInfo})


@bprint.route('/holders_query')
@jwt_required
def holders_query():
    holderName           = request.args.get('name')
    if holderName != None and holderName != '':
        lastItem = db.session.query(Participant.recordDate).order_by(Participant.recordDate.desc()).first()

        pt = db.session.query(Participant.code, Participant.name, Participant.holdMarketValue).filter(Participant.name.like('%' + holderName + '%'), Participant.recordDate == lastItem.recordDate).order_by(Participant.holdMarketValue.desc())
        # pt = db.session.query(Participant.code, Participant.name).filter(Participant.name.like('%' + holderName + '%'), Participant.recordDate == lastItem.recordDate).group_by(Participant.code, Participant.name).limit(15) 
        temp = []
        rtlist = []
        for item in pt:
            if item.code == None or item.code == '':
                continue
            key = '%s%s' % (item.code, item.name)
            if key not in temp:
                rtlist.append({'code': item.code, 'name': item.name, 'marketValue': helper.amountWithUnit(item.holdMarketValue)})
                temp.append(key)

        return jsonify({'list': rtlist})
    else:
        return jsonify({'list': []})

@bprint.route('/xueqiu_data')
@jwt_required
def xueqiu_data():
    stockcode = request.args.get('stockcode')
    
    #默认只显示过去六个月的数据 
    today = datetime.datetime.now()
    DD = datetime.timedelta(days=180)
    earlier = (today - DD).strftime("%Y-%m-%d")

    latestData = db.session.query(XueqiuStockStat.rateScore).filter(XueqiuStockStat.code == stockcode).order_by(XueqiuStockStat.recordDate.desc()).first()

    queries = db.session.query(XueqiuStockStat).filter(XueqiuStockStat.code == stockcode, XueqiuStockStat.recordDate >= earlier).order_by(XueqiuStockStat.recordDate.asc())

    xData      = []
    yLineData1  = []
    yLineData2  = []

    for item in queries:
        xData.append(item.recordDate.strftime("%m%d"))
        yLineData1.append(item.followCount)
        yLineData2.append(item.discussCount)

    return jsonify({'score': latestData and latestData.rateScore, 'xData': xData, 'yLineData1': yLineData1, 'yLineData2': yLineData2})

@bprint.route('/foreign_daily_trade')
#@jwt_required
def foreign_daily_trade():
    stockcode = request.args.get('stockcode')
    # print(stockcode)    
    #默认只显示过去一个月的数据 
    today = datetime.datetime.now()
    DD = datetime.timedelta(days=30)
    earlier = (today - DD).strftime("%Y-%m-%d")

    queries = db.session.query(NorthFlow.stockcode, NorthFlow.oneDayAmount, NorthFlow.recordDate, DailyRecord.close).outerjoin(DailyRecord, NorthFlow.stockcode == DailyRecord.code).filter(NorthFlow.source != 'hk', NorthFlow.stockcode == stockcode, NorthFlow.recordDate >= earlier, NorthFlow.recordDate <= today).order_by(NorthFlow.recordDate.asc()).all()

    xData      = []
    yLineData1  = []
    yLineData2  = []

    for item in queries:
        xData.append(item.recordDate.strftime("%m%d"))
        yLineData1.append(item.oneDayAmount)
        yLineData2.append(item.close)

    return jsonify({'xData': xData, 'yLineData1': yLineData1, 'yLineData2': yLineData2})

# # @mod_main.route('/northflow_stock_ranking')
# # def northflow_stock_ranking()
# #     direction = request.args.get('direction')
# #     if direction == None:
# #         direction = 'desc'

# #     nf = db.session.query(NorthFlow).order_by(NorthFlow.recordDate.desc()).first()
# #     lastDate = nf.recordDate
# #     if direction == 'asc':
# #         queries = db.session.query(NorthFlow).filter(NorthFlow.source != 'hk', NorthFlow.recordDate == lastDate)

# #http://www.cninfo.com.cn/information/shareholders/600690.html 十大股东
# #http://www.cninfo.com.cn/information/circulateshareholders/600690.html 流通股东
# #http://www.cninfo.com.cn/information/financialreport/shmb600690.html 财报综合实力指标