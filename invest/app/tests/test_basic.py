#ref: http://www.patricksoftwareblog.com/unit-testing-a-flask-application/
import os
import unittest

from app import db 
from app.models.main import User
 
class BasicTests(unittest.TestCase):
 
  ############################
  #### setup and teardown ####
  ############################
 
  # executed prior to each test
  def setUp(self):
    pass       
 
  # executed after each test
  def tearDown(self):
    pass
 
 
  ###############
  #### tests ####
  ###############
  #nose2 -v app.tests.test_basic
  def test_add_root_users(self):
    username = '隔壁老王'
    email    = 'test@gmail.com'
    mobile   = '13219005281'
    expireTime = '2030-12-31'
    user = db.session.query(User).filter(User.mobile == mobile).first()
    if user == None:
      user = User(username, mobile, 'start@123', expireTime)
      user.roles = 'vip'
      user.email = email
      db.session.add(user)
      db.session.commit()
      db.session.close()

    # username = '这山那狐'
    # email    = 'hellolaojiang@gmail.com'
    # mobile   = '13219005280'
    # expireTime = '2030-12-31'
    # user = db.session.query(User).filter(User.mobile == mobile).first()
    # if user == None:
    #   user = User(username, mobile, 'start@123', expireTime)
    #   user.roles = 'root'
    #   db.session.add(user)
    #   db.session.commit()
    #   db.session.close()

 
if __name__ == "__main__":
  unittest.main()