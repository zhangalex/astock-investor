from app import db 
from app import app 
from app.services import sms
from app.models.main import User, Order
from datetime import datetime
from sqlalchemy.sql import exists
from sqlalchemy import func

class OrderService(object):
  monthlyFee = 20.0
  discount   = {"1": "1", "3": "0.95", "6": "0.88", "12": "0.833"} 

  @classmethod
  def submitOrder(cls_obj, user, buyMonthes, leaveWords):
    order = Order()
    order.orderNumber = cls_obj.__generateOrderNumber(user.mobile)
    order.mobile = user.mobile 
    order.user_id = user.id 
    order.price = cls_obj.monthlyFee 
    order.orderMonthes = buyMonthes
    order.payAmount = cls_obj.__calculateFee(buyMonthes)
    order.discount = cls_obj.discount.get(buyMonthes)
    order.pay_status = 0
    order.status  = 0
    order.leaveWords = leaveWords 
    order.date_created = datetime.now()
    db.session.add(order)
    db.session.commit()

  @classmethod
  def existsUnPayOrder(cls_obj, user):
    return db.session.query(exists().where(Order.user_id == user.id).where(Order.pay_status == 0)).scalar() 

  @classmethod
  def __calculateFee(cls_obj, buyMonthes):
    if buyMonthes == '12':
      return 200.0
    else:
      return (cls_obj.monthlyFee * float(cls_obj.discount.get(buyMonthes))) * float(buyMonthes)

  @classmethod
  def __generateOrderNumber(cls_obj, mobile):
    return "%s%s%s" % (datetime.now().strftime('%Y%m%d%H%S'), sms.random_with_N_digits(4), mobile)
