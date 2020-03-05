import requests as rq 
import json
import demjson
from bs4 import BeautifulSoup
from app.common import helper

MAIN_FOUND_URL = 'http://ff.eastmoney.com//EM_CapitalFlowInterface/api/js?type=hff&rtntype=2&js=({data:[(x)]})&cb=var aff_data=&check=TMLBMSPROCR&acces_token=1942f5da9b46b069953c873404aad4b5&id=%s&_=1532768532952'
SHORT_SELL_URL = 'http://hk.eastmoney.com/sellshort.html?code=%s&sdate=&edate='

#最近主力资金流向
def getLatestMainCapitalFlow(code):

  firstChar = str(code)[:1]
  if code == '000001' or firstChar == '5' or firstChar == '6' or firstChar == '9':
    code = '%s1' % code 
  else:
    code = '%s2' % code 

  url = MAIN_FOUND_URL % code
  headers = {'Host': 'ff.eastmoney.com', 'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'}
  # print(url)
  res = rq.get(url, headers = headers)
  _, data = res.text.split('=')
  data = data[1:-1]  #去掉首尾的()
  py_obj = demjson.decode(data) 
  records = py_obj['data'][0]
  skdata = []
  #'2018-07-27,-6085.8576,-3.01%,756.1616,0.37%,-6842.0192,-3.39%,2547.6704,1.26%,3538.187,1.75%,60.87,0.12%'
  for rd in records:
    item = rd.split(',')
    skdata.append({'date': item[0], 
                   'price': item[11], 
                   'change': helper.convertToFloat(item[12].replace('%','')),
                   'netAmount': helper.convertToFloat(item[1]),
                   'netChange': helper.convertToFloat(item[2].replace('%',''))
                  })
  return skdata

#获取港股做空数据
def getHkShortSellingData(code):
  headers = {'Host': 'hk.eastmoney.com', 'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'}
  url = SHORT_SELL_URL % code
  #print(url)
  res = rq.get(url, headers = headers)
  html_contents = res.text 
  shortSellings = []
  soup = BeautifulSoup(html_contents, 'lxml')
  items = soup.select('ul.clear')
  for item in items:
    tds = item.find_all('li')
    shortSellings.append({'code': tds[1].text, 
                          'name': tds[2].text, 
                          'quantity': tds[4].text,
                          'avgPrice': helper.convertToFloat(tds[5].text),
                          'sellAmount': helper.convertToFloat(tds[6].text.replace('万', '')),
                          'totalAmount': helper.convertToFloat(tds[7].text.replace('万', '')),
                          'ratio': helper.convertToFloat(tds[8].text.replace('%', '')),
                          'date': tds[9].text
                         })

  return shortSellings 

