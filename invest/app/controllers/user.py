from flask import Blueprint, request, jsonify, session
from sqlalchemy import func
from sqlalchemy.sql import exists
from flask_jwt_extended import (
    jwt_required, create_access_token,
    get_jwt_identity, get_jwt_claims
)
import datetime
import sys 
import os
from PIL import Image, ImageDraw, ImageFont
from io import StringIO, BytesIO
from app import db
from app import app
from app.models.main import User
from app.common import helper
from app.common.imageChar import ImageChar 
import app.services.auth
import app.common.helper
from app.common.captcha import CaptchaGenerate
from app.services import sms
from app.services.order_service import OrderService
import app.schedules.inform_job as inform

bprint = Blueprint('user', __name__, url_prefix='/api/v1.0/user')

DEFAULT_FREE_DAYS = 5
FREE_USE_DAYS = 1
VALID_CODE_CHN_KEY = 'valid_chn_code'
VALID_CODE_LETTER_KEY = 'valid_letter_code'
MOBILE_VALID_CODE_KEY = 'mobile_%s'

@bprint.route('/login', methods=['POST'])
def login():
  try:
    # print('login: %s' % session.get(VALID_CODE_LETTER_KEY)) #这种取值方式会有异常
    mobile    = request.json.get('mobile', None)
    password = request.json.get('password', None)
    validCode = request.json.get('validCode', None)
    if session.get(VALID_CODE_LETTER_KEY) == None \
        or validCode == None or validCode == '' \
        or session[VALID_CODE_LETTER_KEY].lower() != validCode.lower():
      return jsonify({"message": "验证码错误，请重新输入", "code": -1}), 403

    if mobile == None or password == None:
      return jsonify({"message": "请填写电子邮件或者密码", "code": -1}), 403

    user = db.session.query(User).filter(User.mobile == mobile).first()
    if user:
      if user.check_password(password):
        if user.isFrozen:
          return jsonify({"message": "用户已经被冻结，请联系管理员", "code": -1}), 403

        if datetime.datetime.now() > user.expirationTime:
          return jsonify({"message": "用户已经失效，请付费", "mobile": user.mobile, "code": 1, "needPay": "true"}), 200


        user.latestLoginTime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") #now().replace(microsecond=0).isoformat(' ')
        db.session.commit()
        access_token = create_access_token(identity=user)
        ret = {"token": access_token, "code": 1}
        return jsonify(ret), 200
      else:
        return jsonify({"message": "用户名或者密码错误", "code": -1}), 403

    else:
      return jsonify({"message": "用户名或者密码错误", "code": -1}), 403

  except Exception as inst:
      print(str(inst))
      return jsonify({"message": "内部错误，请联系管理员", "code": -1}), 403

@bprint.route('/verify_chn_code', methods=['GET'])
def getVerifyChnCode():
  ic = ImageChar(fontColor=(100,211, 90), fontPath="%s/font/simhei.ttf" % app.project_root_path)
  strs, code_img = ic.randChinese(4)
  # buf = StringIO()
  buf = BytesIO()
  code_img.save(buf,'JPEG',quality=70)
  buf_str = buf.getvalue()
  response = app.make_response(buf_str)
  response.headers['Content-Type'] = 'image/jpeg'
  # print('valid code: %s' % strs)
  session[VALID_CODE_CHN_KEY] = strs 
  return response

@bprint.route('/verify_code', methods=['GET'])
def getVerifyCode():
  ic = CaptchaGenerate(font_path="%s/font/arial.ttf" % app.project_root_path)

  strs, code_img = ic.draw_code(4)
  buf = BytesIO()
  code_img.save(buf,'JPEG',quality=70)
  buf_str = buf.getvalue()
  response = app.make_response(buf_str)
  response.headers['Content-Type'] = 'image/jpeg'
  # print('valid code: %s' % strs)
  session[VALID_CODE_LETTER_KEY] = strs 
  return response

@bprint.route('/register', methods=['POST'])
def register():
  userInfo = request.get_json()
  mobile = userInfo["mobile"]
  username = userInfo["username"]
  password = userInfo["password"]
  mobileValidCode = userInfo["mobileValidCode"]
  key = MOBILE_VALID_CODE_KEY % mobile
  if session.get(key) == None \
        or mobileValidCode == None or mobileValidCode == '' \
        or str(session[key]).lower() != str(mobileValidCode).lower():
    return jsonify({"message": "手机验证码错误，请填写手机收到的数字。", "code": -1}), 403

  if helper.isEmpty(mobile) or helper.isEmpty(username) or helper.isEmpty(password):
    return jsonify({"message": "请填写完整信息", "code": -1})

  if db.session.query(exists().where(User.mobile == mobile)).scalar() == True:
    return jsonify({"message": "手机号已经存在", "code": -1})

  if db.session.query(exists().where(User.username == username)).scalar() == True:
    return jsonify({"message": "用户名已经存在", "code": -1})

  if len(password) < 6:
    return jsonify({"message": "密码长度至少6位", "code": -1})

  exipreationDate = datetime.datetime.now() + datetime.timedelta(days=DEFAULT_FREE_DAYS)

  user = User(username, mobile, password, exipreationDate.strftime('%Y-%m-%d'))
  user.email = '%s@gmail.com' % mobile
  user.roles = 'normal'
  db.session.add(user)
  db.session.commit() 
    
  inform.send_to_wx.delay('新用户注册', '手机号为: %s 的用户，注册成了新用户。' % mobile) 

  return jsonify({"message": "注册成功", "code": 1})


@bprint.route('/modifypwd', methods=['POST'])
@jwt_required
def modify_pwd():
  oldPassword = request.json.get('oldpassword', None)
  newPassword = request.json.get('newpassword', None)
  if oldPassword == None or newPassword == None or oldPassword.strip() == '' or newPassword.strip() == '':
    return jsonify({"message": "请填写完整信息", "code": -1}), 500

  if len(newPassword) < 6:
    return jsonify({"message": "密码长度不能小于6位", "code": -1}), 500

  user = db.session.query(User).filter(User.mobile == get_jwt_identity()).first()
  if user and user.check_password(oldPassword):
    user.set_password(newPassword)
    user.lastPasswordResetDate = datetime.datetime.now()
    db.session.commit()
    return jsonify({"message": "密码修改成功", "code": 1}), 200
  else:
    return jsonify({"message": "原始密码不正确", "code": -1}), 500

@bprint.route('/user_info', methods=['GET'])
@jwt_required
def user_info():
  user = db.session.query(User).filter(User.mobile == get_jwt_identity()).first()
  if datetime.datetime.now() > user.expirationTime or user.isFrozen:
    return jsonify({"message": "用户已经失效或者被冻结，请联系管理员", "code": -1}), 401
  else:
    return jsonify({"code": 1, "name": user.username, "email": user.email, "mobile": user.mobile, "avatar": user.avatar, "expireTime": user.expirationTime.strftime('%Y-%m-%d'), "role": [] if user.roles == None or user.roles == '' else user.roles.split(',')})

@bprint.route('/send_mobile_code', methods=['POST'])
def send_mobile_code():
  mobile    = request.json.get('mobile', None)
  validCode = request.json.get('validCode', None)
  if session.get(VALID_CODE_LETTER_KEY) == None \
        or validCode == None or validCode == '' \
        or session[VALID_CODE_LETTER_KEY].lower() != validCode.lower():
    return jsonify({"message": "验证码错误，请参照图片中的验证码，重新输入", "code": -1}), 403

  resultCode = sms.send(mobile)
  if resultCode > 0:
    session[MOBILE_VALID_CODE_KEY % mobile] = resultCode
    return jsonify({"message": "手机验证码发送成功", "code": 1}), 200
  else:
    return jsonify({"message": "手机验证码发送失败，请检查手机号码是否正确", "code": -1}), 500

@bprint.route('/order_product', methods=['POST'])
def order_product():
  mobile        = request.json.get('mobile', None)
  buyMonthes    = request.json.get('buyMonthes', None)
  leaveWords    = request.json.get('leaveWords', None)

  if mobile != None and buyMonthes != None and leaveWords != None:
    user = db.session.query(User).filter(User.mobile == mobile).first()
    if user != None:
      if datetime.datetime.now() > user.expirationTime:
        if not OrderService.existsUnPayOrder(user):
          OrderService.submitOrder(user, buyMonthes, leaveWords)
          user.expirationTime = datetime.datetime.now() + datetime.timedelta(days = FREE_USE_DAYS)
          print(user.expirationTime)
          db.session.commit() 

          inform.send_to_wx.delay('订购信息', '手机号为: %s 的用户，订购了 %s 个月，请查看付费情况。' % (mobile, buyMonthes)) 
          return jsonify({"message": "我们已经收到您提交的订单，在我们确认订单的时间里面，你可以免费使用该产品1天。", "code": 1}), 200
        else:
          return jsonify({"message": "你已经提交过订单，但是支付未确认，不用重复提交。", "code": -1}), 500


      else:
        return jsonify({"message": "用户有效，无需付费", "code": -1}), 500

    else:
      return jsonify({"message": "无效的数据", "code": -1}), 500


  else:
    return jsonify({"message": "无效的数据", "code": -1}), 500







