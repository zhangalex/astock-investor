from app import app 

from random import randint
from yunpian_python_sdk.model import constant as YC
from yunpian_python_sdk.ypclient import YunpianClient

def send(mobile):
  clnt = YunpianClient(app.config['YUNPIAN_API_KEY'])
  code = random_with_N_digits(6)
  param = {YC.MOBILE: mobile, YC.TEXT: '【浩然网络】您正在使用投资者助理，您的验证码是 %s' % code}
  r = clnt.sms().single_send(param)
  app.logger.info(r.code())
  if int(r.code()) == 0:
    return code 
  else:
    return 0

def random_with_N_digits(n):
  range_start = 10**(n-1)
  range_end = (10**n)-1
  return randint(range_start, range_end)