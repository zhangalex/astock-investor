from app import db
import time 
from werkzeug.security import generate_password_hash, \
     check_password_hash
# Define a base model for other database tables to inherit
class Base(db.Model):

    __abstract__  = True

    id            = db.Column(db.Integer, primary_key=True)
    date_created  = db.Column(db.DateTime,  default=db.func.current_timestamp())
    date_modified = db.Column(db.DateTime,  default=db.func.current_timestamp(),
                                           onupdate=db.func.current_timestamp())


class Msci(Base):
    __tablename__ = 'msci'
    code          = db.Column(db.String(20), nullable=False, unique=True, index=True)
    name          = db.Column(db.String(50), nullable=False, index=True)
    industry      = db.Column(db.String(50), nullable=False)
    pinyin        = db.Column(db.String(50), nullable=True)
    growthRate    = db.Column(db.DECIMAL(10,2), nullable=True, index=True)
    recordDate    = db.Column(db.Date, nullable=False)

    def __init__(self, code, name, industry, pinyin, growthRate = None, recordDate = None):
        self.code = code
        self.name = name 
        self.industry = industry
        self.pinyin = pinyin
        self.growthRate = growthRate
        if recordDate == None:
            self.recordDate = time.strftime("%Y-%m-%d")
        else:
            self.recordDate = recordDate

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns if c.name!='pinyin' and c.name!='id'}


class NorthFlow(db.Model):
    __tablename__ = 'northflows'

    id             = db.Column(db.BigInteger, primary_key=True)
    hkcode         = db.Column(db.String(20), nullable=False, index=True)
    stockname      = db.Column(db.String(50), nullable=False)
    stockcode      = db.Column(db.String(20))
    holdQuantity   = db.Column(db.BigInteger, nullable=True)
    astockPercent  = db.Column(db.DECIMAL(10,2), nullable=False, index=True)   #占A股总股本的比例
    circularPercent  = db.Column(db.DECIMAL(10,2), nullable=True, index=True) #占A股流通股的比例
    recordDate     = db.Column(db.Date, nullable=False)
    dayIndex       = db.Column(db.Integer, nullable=False, default=0, index=True)
    oneDayIncre    = db.Column(db.Integer, index=True)
    oneDayAmount   = db.Column(db.DECIMAL(18,4), index=True)
    fiveDayIncre   = db.Column(db.Integer, index=True)
    tenDayIncre    = db.Column(db.Integer, index=True)
    rankgrowth     = db.Column(db.Integer, nullable=True, default=0, index=True)
    source         = db.Column(db.String(20), index=True)
    continueBdays  = db.Column(db.Integer, index=True)  #持续买入的天数
    continueSdays  = db.Column(db.Integer, index=True)  #持续卖出的天数
    holdMarketValue   = db.Column(db.DECIMAL(18,4), index=True) #持有市值

    __table_args__ = (db.Index('ix_northflow_d_h_s', 'dayIndex', 'hkcode', 'source'), 
                        db.Index('ix_northflow_d_s', 'dayIndex', 'source'),
                        db.Index('ix_northflow_r_s', 'recordDate', 'source'),
                        db.Index('ix_northflow_r_s_h', 'recordDate', 'source', 'hkcode'),
                        db.Index('ix_northflow_r_h', 'recordDate', 'hkcode')
                        
                    )

    def __init__(self, hkcode=None, stockname=None, holdQuantity=None, astockPercent=None, recordDate=None, dayIndex=None, source = None, stockcode=None):
        self.hkcode         = hkcode
        self.stockname      = stockname
        self.holdQuantity   = holdQuantity
        self.astockPercent  = astockPercent
        self.stockcode      = stockcode
        self.dayIndex       = dayIndex
        self.source         = source
        if recordDate == None:
            self.recordDate = time.strftime("%Y-%m-%d")
        else:
            self.recordDate = recordDate

    def as_dict(self):
        # return {c.name: getattr(self, c.name) for c in self.__table__.columns if c.name!='stockcode' and c.name!='id'}
        return {c.name: getattr(self, c.name) for c in self.__table__.columns if  c.name!='id'}

    def __repr__(self):
        return '%s (%r, %r)' % (self.__class__.__name__, self.stockname, self.id)



class NorthStatistics(db.Model):
    __tablename__ = 'north_statistics'
    id             = db.Column(db.BigInteger, primary_key=True)
    recordDate     = db.Column(db.Date, nullable=False)
    buyCount       = db.Column(db.Integer)
    soldCount      = db.Column(db.Integer)
    buyAmount      = db.Column(db.DECIMAL(18,4))
    soldAmount     = db.Column(db.DECIMAL(18,4))
    source         = db.Column(db.String(20), index=True) 
    __table_args__ = (db.Index('ix_north_statistics_datesource', 'recordDate', 'source'),)

    def __init__(self):
        pass

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns if  c.name!='id'}

class AttentionStocks(db.Model):
    __tablename__ = 'attention_stocks'

    id             = db.Column(db.Integer, primary_key=True)
    code           = db.Column(db.String(20), nullable=False, index=True)
    user_id        = db.Column(db.Integer, nullable=True, index=True)

    def __init__(self, code, user_id):
        self.code = code
        self.user_id = user_id



class StockBasic(db.Model):
    __tablename__ = 'stock_basic'
    id                 = db.Column(db.Integer, primary_key=True)
    code               = db.Column(db.String(20), nullable=False, index=True)
    name               = db.Column(db.String(20), nullable=False, index=True)
    industry           = db.Column(db.String(20), nullable=False, index=True) #行业
    area               = db.Column(db.String(20), nullable=False, index=True) #区域
    pe                 = db.Column(db.DECIMAL(12,2), index=True)
    outstanding        = db.Column(db.DECIMAL(12,2)) #流通股本(亿)
    totals             = db.Column(db.DECIMAL(12,2)) #总股本(亿)
    totalAssets        = db.Column(db.DECIMAL(12,2)) #总资产(万)
    liquidAssets       = db.Column(db.DECIMAL(12,2)) #流动资产
    fixedAssets        = db.Column(db.DECIMAL(12,2)) #固定资产
    reserved           = db.Column(db.DECIMAL(12,2)) #公积金
    reservedPerShare   = db.Column(db.DECIMAL(12,2)) #每股公积金
    esp                = db.Column(db.DECIMAL(18,4)) #每股收益
    bvps               = db.Column(db.DECIMAL(12,2)) #每股净资
    pb                 = db.Column(db.DECIMAL(12,2)) #市净率
    timeToMarket       = db.Column(db.Date, index=True) #上市日期
    undp               = db.Column(db.DECIMAL(12,2)) #未分利润
    perundp            = db.Column(db.DECIMAL(12,2)) #每股未分配
    rev                = db.Column(db.DECIMAL(12,2)) #收入同比(%)
    profit             = db.Column(db.DECIMAL(12,2)) #利润同比(%)
    gpr                = db.Column(db.DECIMAL(12,2)) #毛利率(%)
    npr                = db.Column(db.DECIMAL(12,2)) #净利润率(%)
    holders            = db.Column(db.DECIMAL(12,2)) #股东人数
    tomarketYear       = db.Column(db.Integer, index=True)
    tomarketYearMonth       = db.Column(db.Integer, index=True)

    def __init__(self):
        pass

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns if  c.name!='id'}

class StockFinanceMain(db.Model):
    __tablename__ = 'stock_finance'
    id                 = db.Column(db.BigInteger, primary_key=True)
    code               = db.Column(db.String(20), nullable=False, index=True)
    name               = db.Column(db.String(20), nullable=False, index=True)
    year               = db.Column(db.Integer, nullable=False, index=True)
    quarter            = db.Column(db.Integer, index=True)
    esp                = db.Column(db.DECIMAL(12,2)) #每股收益
    eps_yoy            = db.Column(db.DECIMAL(12,2)) #每股收益同比(%)
    bvps               = db.Column(db.DECIMAL(12,2)) #每股净资产
    roe                = db.Column(db.DECIMAL(12,2)) #净资产收益率(%)
    epcf               = db.Column(db.DECIMAL(12,2)) #每股现金流量(元)
    net_profits        = db.Column(db.DECIMAL(16,4)) #净利润(万元)
    profits_yoy        = db.Column(db.DECIMAL(12,2)) #净利润同比(%)
    distrib            = db.Column(db.String(300)) #分配方案
    report_date        = db.Column(db.String(50)) #发布日期

    __table_args__ = (db.Index('ix_stockfinance_codeyearquarter', 'code', 'year', 'quarter'), )

    def __init__(self):
        pass

#股票十大股东
class StockShareHolder(db.Model):
    __tablename__ = 'stock_shareholder'
    id             = db.Column(db.BigInteger, primary_key=True)
    code           = db.Column(db.String(20), nullable=False, index=True)
    name           = db.Column(db.String(20), nullable=False, index=True)
    holderType     = db.Column(db.String(20), nullable=False, index=True)  #股东类型
    holderName     = db.Column(db.String(255), nullable=False, index=True)  #股东名称
    stockType      = db.Column(db.String(20), nullable=False, index=True)  #股份类型
    holdQuantity   = db.Column(db.BigInteger) #持股数
    stockPercent   = db.Column(db.DECIMAL(12,2), index=True) #占股比例 
    change         = db.Column(db.String(20), index=True) #变化，增加还是减少
    changeQuantity = db.Column(db.BigInteger)  #增加或者减少多少股
    category       = db.Column(db.Integer, nullable=False, index=True) #0 - 十大流通股东，1 - 十大股东
    reportDate     = db.Column(db.Date, nullable=False, index=True)

    __table_args__ = (db.Index('ix_stockholder_codedatecategory', 'code', 'reportDate', 'category'), db.Index('ix_stockholder_codedate', 'code', 'reportDate'))

    def __init__(self):
        pass

    # def __init__(self, code, name, holderType, holderName, stockType, holdQuantity, stockPercent, category, change, changeQuantity, reportDate):
    #     self.code = code
    #     self.name = name
    #     self.holderType = holderType
    #     self.holderName = holderName
    #     self.stockType = stockType
    #     self.holdQuantity = holdQuantity
    #     self.stockPercent = stockPercent
    #     self.category = category
    #     self.change = change
    #     self.changeQuantity = changeQuantity
    #     self.reportDate = reportDate

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns if  c.name!='id'}

class User(db.Model):
    __tablename__ = 'users'
    id              = db.Column(db.Integer, primary_key=True)
    username        = db.Column(db.String(20), nullable=False, index=True, unique=True)
    password        = db.Column(db.String(100), nullable=False)
    mobile          = db.Column(db.String(30), nullable=False, index=True, unique=True)
    email           = db.Column(db.String(50), nullable=False, index=True, unique=True)
    avatar          = db.Column(db.String(300), nullable=True)
    isFrozen        = db.Column(db.Boolean, nullable=False, default=False)
    latestLoginTime = db.Column(db.DateTime, nullable=True, index=True)
    lastPasswordResetDate = db.Column(db.DateTime, nullable=True)
    expirationTime  = db.Column(db.DateTime, nullable=False, index=True)
    roles           = db.Column(db.String(100), nullable=True) #root, vip, normal
    date_created    = db.Column(db.DateTime,  default=db.func.current_timestamp())

    def __init__(self, username, mobile, password, expirationTime):
        self.username = username
        self.mobile = mobile
        self.set_password(password)
        self.expirationTime = expirationTime
        
    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

class DailyRecord(db.Model):
    __tablename__ = 'daily_records'
    id                       = db.Column(db.BigInteger, primary_key=True)
    code                     = db.Column(db.String(20), nullable=False, index=True)
    name                     = db.Column(db.String(20), nullable=False, index=True)
    changepercent            = db.Column(db.DECIMAL(16,4), nullable=True, index=True)   #涨跌幅
    close                    = db.Column(db.DECIMAL(16,4), nullable=True, index=True)   #现价（收盘价）
    open                     = db.Column(db.DECIMAL(16,4), nullable=True)   #开盘价
    high                     = db.Column(db.DECIMAL(16,4), nullable=True)   #最高价
    low                      = db.Column(db.DECIMAL(16,4), nullable=True)   #最低价
    settlement               = db.Column(db.DECIMAL(16,4), nullable=True)   #昨日收盘价
    volume                   = db.Column(db.DECIMAL(16,4), nullable=True)   #交易量(股)
    turnoverratio            = db.Column(db.DECIMAL(16,4), nullable=True, index=True)   #换手率
    amount                   = db.Column(db.DECIMAL(16,4), nullable=True)   #交易额
    per                      = db.Column(db.DECIMAL(16,4), nullable=True)   #市盈率
    pb                       = db.Column(db.DECIMAL(16,4), nullable=True)   #市净率
    mktcap                   = db.Column(db.DECIMAL(18,4), nullable=True, index=True)   #总市值（万）
    nmc                      = db.Column(db.DECIMAL(18,4), nullable=True, index=True)   #流通市值（万）
    recordDate               = db.Column(db.Date, nullable=False, index=True)

    __table_args__ = (db.Index('ix_dailyrecords_codedate', 'code', 'recordDate'), db.Index('ix_dailyrecords_codeclose', 'code', 'close'))

    def __init__(self):
        pass

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns if  c.name!='id'}

class HkDailyRecord(db.Model):
    __tablename__ = 'hk_daily_records'
    id                       = db.Column(db.BigInteger, primary_key=True)
    code                     = db.Column(db.String(20), nullable=False, index=True)
    name                     = db.Column(db.String(20), nullable=False, index=True)
    change                   = db.Column(db.DECIMAL(16,4), nullable=True, index=True)   #涨跌额
    changepercent            = db.Column(db.DECIMAL(16,4), nullable=True, index=True)   #涨跌幅
    close                    = db.Column(db.DECIMAL(16,4), nullable=True, index=True)   #现价（收盘价）
    open                     = db.Column(db.DECIMAL(16,4), nullable=True)   #开盘价
    high                     = db.Column(db.DECIMAL(16,4), nullable=True)   #最高价
    low                      = db.Column(db.DECIMAL(16,4), nullable=True)   #最低价
    settlement               = db.Column(db.DECIMAL(16,4), nullable=True)   #昨日收盘价
    volume                   = db.Column(db.DECIMAL(16,4), nullable=True)   #交易量(股)
    turnoverratio            = db.Column(db.DECIMAL(16,4), nullable=True, index=True)   #换手率
    amount                   = db.Column(db.DECIMAL(16,4), nullable=True)   #交易额
    mktcap                   = db.Column(db.DECIMAL(18,4), nullable=True, index=True)   #总市值（万）
    nmc                      = db.Column(db.DECIMAL(18,4), nullable=True, index=True)   #流通市值（万）
    recordDate               = db.Column(db.Date, nullable=False, index=True)
    recordIndex              = db.Column(db.Integer, nullable=False, index=True)

    __table_args__ = (db.Index('ix_hkdailyrecords_codedate', 'code', 'recordDate'), db.Index('ix_hkdailyrecords_codeindex', 'code', 'recordIndex'), db.Index('ix_hkdailyrecords_codeclose', 'code', 'close'))

    def __init__(self):
        pass

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns if  c.name!='id' and c.name != 'recordIndex'}

class Order(db.Model):
    __tablename__ = 'orders'
    id                       = db.Column(db.Integer, primary_key=True)
    orderNumber              = db.Column(db.String(50), nullable=False, index=True)
    mobile                   = db.Column(db.String(20), nullable=False, index=True)
    user_id                  = db.Column(db.Integer, nullable=False, index=True)
    price                    = db.Column(db.DECIMAL(16,4), nullable=False)   #单价，元/月
    orderMonthes             = db.Column(db.Integer, nullable=True)          #付费月数
    payAmount                = db.Column(db.DECIMAL(16,4), nullable=False)   #支付总金额
    discount                 = db.Column(db.DECIMAL(16,4), nullable=False, default=1)   #折扣，默认没折扣,按月折扣如下：(1:1, 3:0.9, 6:0.85, 12:0.8)
    pay_status               = db.Column(db.Integer, nullable=False, index=True, default=0) #0,表示未支付；1，表示已经支付
    status                   = db.Column(db.Integer, nullable=False, index=True, default=0)
    leaveWords               = db.Column(db.String(200))
    pay_datetime             = db.Column(db.DateTime, index=True)
    date_created             = db.Column(db.DateTime, index=True)

    def __init__(self):
        pass

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns if  c.name!='id'}

class ShortStat(db.Model):
    __tablename__ = 'short_stats'
    id                       = db.Column(db.Integer, primary_key=True)
    content                  = db.Column(db.JSON, nullable=False)
    stype                    = db.Column(db.String(20), nullable=False, index=True) 
    recordDate               = db.Column(db.Date, nullable=False, index=True)

    __table_args__ = (db.Index('ix_short_stats_typerecorddate', 'stype', 'recordDate'),)

    def __init__(self, content, stype, recordDate):
        self.content = content
        self.stype = stype
        self.recordDate =recordDate

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns if  c.name!='id'}

class StockIndustry(db.Model):
    __tablename__ = 'stock_industry'
    id             = db.Column(db.Integer, primary_key=True) 
    code           = db.Column(db.String(20), nullable=False, index=True)
    name           = db.Column(db.String(30), nullable=False, index=True) #行业名称
    source         = db.Column(db.String(20), nullable=False)  #sw 申万 
    level          = db.Column(db.Integer, nullable=False) #1,2,3
    __table_args__ = (db.Index('ix_stock_industry_sourcelevel', 'source', 'level'),)

    def __init__(self, code, name, source, level):
        self.code = code
        self.name = name
        self.source = source
        self.level = level

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns if  c.name!='id'}

class Participant(db.Model):
    __tablename__ = 'participants'
    id                       = db.Column(db.BigInteger, primary_key=True)
    hkcode                   = db.Column(db.String(20), nullable=False, index=True)
    stockcode                = db.Column(db.String(20), nullable=False, index=True)
    code                     = db.Column(db.String(20), nullable=False, index=True)
    name                     = db.Column(db.String(100), nullable=False)
    holdQuantity             = db.Column(db.BigInteger, nullable=False, index=True) 
    stockPercent             = db.Column(db.DECIMAL(10,2), nullable=False, index=True) #占钟股份百分比 
    recordDate               = db.Column(db.Date, nullable=False, index=True)
    dayIndex                 = db.Column(db.Integer, nullable=False, default=0, index=True)
    oneDayIncre              = db.Column(db.BigInteger, index=True)
    oneDayAmount             = db.Column(db.DECIMAL(18,4))
    fiveDayIncre             = db.Column(db.Integer)
    holdMarketValue          = db.Column(db.DECIMAL(18,4), index=True) #持有市值
    source                   = db.Column(db.String(20))

    __table_args__ = (db.Index('ix_participants_d_h', 'dayIndex', 'stockcode'), 
                        db.Index('ix_participants_d_s', 'dayIndex', 'source'),
                        db.Index('ix_participants_r_s', 'recordDate', 'source'),
                        db.Index('ix_participants_r_s_h', 'recordDate', 'source', 'stockcode'),
                        db.Index('ix_participants_r_h', 'recordDate', 'stockcode'),
                        db.Index('ix_participants_r_c', 'recordDate', 'code')
                        
                    )

    def __init__(self):
        pass

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns if  c.name!='id'}

class HolderBase(db.Model):
    __tablename__ = 'holderbase'
    id                       = db.Column(db.BigInteger, primary_key=True)
    code                     = db.Column(db.String(20), nullable=False, unique=True)
    name                     = db.Column(db.String(100), nullable=False, index=True)
    pinyin                   = db.Column(db.String(200), nullable=False, index=True)

    def __init__(self, code, name, pinyin):
        self.code = code
        self.name = name
        self.pinyin = pinyin

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns if  c.name!='id'}

class Simu(db.Model):
    __tablename__ = 'simu'
    id                     = db.Column(db.BigInteger, primary_key=True)
    artificialPersonName   = db.Column(db.String(100), nullable=True)
    registerProvince       = db.Column(db.String(100), nullable=True, index=True)
    subscribedCapital      = db.Column(db.DECIMAL(18,4), nullable=True) 
    registerAddress        = db.Column(db.String(100), nullable=True)
    fundCount              = db.Column(db.Integer, nullable=True, index=True)
    primaryInvestType      = db.Column(db.String(100), nullable=True, index=True)
    officeCity             = db.Column(db.String(100), nullable=True, index=True)
    hasSpecialTips         = db.Column(db.String(100), nullable=True)
    officeCoordinate       = db.Column(db.String(100), nullable=True)
    establishDate          = db.Column(db.Date, nullable=True, index=True)
    officeAddress          = db.Column(db.String(100), nullable=True)
    fundScale              = db.Column(db.DECIMAL(18,4), nullable=True, index=True)
    regAdrAgg              = db.Column(db.String(100), nullable=True)
    managerHasProduct      = db.Column(db.String(10), nullable=True)
    innerid                = db.Column(db.String(20), nullable=True)
    registerNo             = db.Column(db.String(100), nullable=True, unique=True)
    inBlacklist            = db.Column(db.String(100), nullable=True)
    registerDate           = db.Column(db.Date, nullable=True, index=True)
    registerYear           = db.Column(db.Integer, nullable=True, index=True)
    registerYearMonth      = db.Column(db.Integer, nullable=True, index=True)
    registerCity           = db.Column(db.String(100), nullable=True)
    regCoordinate          = db.Column(db.String(100), nullable=True)
    managerName            = db.Column(db.String(100), nullable=True, index=True)
    officeProvince         = db.Column(db.String(100), nullable=True, index=True)
    hasCreditTips          = db.Column(db.String(100), nullable=True)
    url                    = db.Column(db.String(200), nullable=True)
    paidInCapital          = db.Column(db.DECIMAL(18,4), nullable=True)


    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns if  c.name !='id' and c.name != 'innerid'}

class IndustryStat(db.Model):
    __tablename__ = 'industry_stats'
    id             = db.Column(db.Integer, primary_key=True)
    name           = db.Column(db.String(30), nullable=False, index=True) #行业名称
    amount         = db.Column(db.DECIMAL(18,4))
    source         = db.Column(db.String(20)) 
    recordDate     = db.Column(db.Date, nullable=False, index=True)

    __table_args__ = (db.Index('ix_industry_stats_namesource', 'name', 'source'),)

    def __init__(self, name, amount, source, recordDate):
        self.name = name 
        self.amount = amount
        self.source = source
        self.recordDate =recordDate

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns if  c.name!='id'}

class XueqiuStockStat(db.Model):
    __tablename__ = 'xuqiu_stock_stats'
    id             = db.Column(db.Integer, primary_key=True)
    code           = db.Column(db.String(20), nullable=False, index=True)
    followCount    = db.Column(db.Integer, nullable=True)
    discussCount   = db.Column(db.Integer, nullable=True)
    rating         = db.Column(db.JSON, nullable=True)     #最新20条评级数据
    rateScore      = db.Column(db.DECIMAL(18,4), nullable=True) #评级得分
    source         = db.Column(db.String(20), nullable=True) 
    recordDate     = db.Column(db.Date, nullable=False, index=True)

    __table_args__ = (db.Index('ix_xuqiu_stock_stats_cr', 'code', 'recordDate'),)

    def __init__(self, code, followCount, discussCount, rating, rateScore, recordDate):
        self.code = code 
        self.followCount = followCount
        self.discussCount = discussCount 
        self.rating = rating 
        self.rateScore = rateScore
        self.recordDate =recordDate
        self.source = 'hs' if len(code) >5 else 'hk'

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns if  c.name!='id'}


class MainCapitalFlow(db.Model):
    __tablename__ = 'main_capital_flow'
    id             = db.Column(db.Integer, primary_key=True)
    code           = db.Column(db.String(20), nullable=False, index=True)
    price          = db.Column(db.DECIMAL(18, 4), nullable=False)
    change         = db.Column(db.DECIMAL(18, 4), nullable=False)
    netAmount      = db.Column(db.DECIMAL(18, 4), nullable=False)
    netChange      = db.Column(db.DECIMAL(18, 4), nullable=False)
    recordDate     = db.Column(db.Date, nullable=False, index=True)
    __table_args__ = (db.Index('ix_main_capital_flow_cr', 'code', 'recordDate'),)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns if  c.name!='id'}

class HkShortSell(db.Model):
    __tablename__ = 'hk_short_sell'
    id             = db.Column(db.Integer, primary_key=True)
    code           = db.Column(db.String(20), nullable=False, index=True)
    price          = db.Column(db.DECIMAL(18, 4), nullable=True)
    name           = db.Column(db.String(50), nullable=True)
    quantity       = db.Column(db.Integer, nullable=True)
    avgPrice       = db.Column(db.DECIMAL(18, 4), nullable=True)
    sellAmount     = db.Column(db.DECIMAL(18, 4), nullable=True)
    totalAmount    = db.Column(db.DECIMAL(18, 4), nullable=True)
    ratio          = db.Column(db.DECIMAL(18, 4), nullable=True)
    recordDate     = db.Column(db.Date, nullable=False, index=True)
    __table_args__ = (db.Index('ix_hk_short_sell_cr', 'code', 'recordDate'),)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns if  c.name!='id'}


