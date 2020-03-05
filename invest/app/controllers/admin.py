from flask import Blueprint, request, jsonify
from sqlalchemy import func
from sqlalchemy.sql import exists
from flask_jwt_extended import (
    jwt_required, create_access_token,
    get_jwt_identity, get_jwt_claims
)
import datetime
import sys 
import re

from app import db
from app.models.main import User
from app.common import helper
import app.services.auth

bprint = Blueprint('admin', __name__, url_prefix='/api/v1.0/admin')

ADMIN_ROLE_NAME = 'root'
DEFAULT_USER_PWD = '111111'

@bprint.route('/users', methods=['GET'])
@jwt_required
def users():
  current_user_roles = get_jwt_claims()["roles"]
  if ADMIN_ROLE_NAME not in current_user_roles:
    return jsonify({"message": "你无权访问该资源", "code": -1}), 404

  columns = [
         {'name': 'index',      'type': 'number',  'title': 'No.', 'sortable': False},
         {'name': 'username',      'type': 'string',  'title': '用户名'},
         {'name': 'mobile',      'type': 'string',  'title': '手机号'},
         {'name': 'roles',  'type': 'string',  'title': '角色'},
         {'name': 'isFrozen',  'type': 'string',  'title': '是否冻结'},
         {'name': 'latestLoginTime',  'type': 'string',  'title': '最后登录时间'},
         {'name': 'expirationTime',  'type': 'string',  'title': '到期时间'},
         {'name': 'date_created',  'type': 'string',  'title': '创建时间'}
  ]

  orderBy        = request.args.get('orderBy')
  orderDirection = request.args.get('orderDirect')
  page           = request.args.get('page')
  per_page       = request.args.get('perPage')

  if orderBy == None or orderBy == '':
    orderBy        = 'latestLoginTime'
    orderDirection = 'desc'

  if page == None or page =='':
    page = 1

  if per_page == None or per_page == '':
    per_page = 10

  queries = db.session.query(User).order_by(getattr(getattr(User, orderBy), orderDirection)()).order_by(User.id.asc()).paginate(int(page), int(per_page), False)

  pageInfo = {
    'total':   queries.total,  
    'current': int(page),  
    'pagenum': int(per_page), 
    'page':    queries.pages,
    'pagegroup': 5,    
    'skin':'#00D1B2'  
  }
  users = []
  index = (int(page) - 1) * int(per_page)
  for item in queries.items:
    index += 1
    users.append({"index": index,  "id": item.id, "username": item.username, "mobile": item.mobile, "isFrozen": "是" if item.isFrozen else "否", "latestLoginTime": item.latestLoginTime.strftime('%Y-%m-%d %H:%M') if item.latestLoginTime != None else '', "expirationTime": item.expirationTime.strftime('%Y-%m-%d'), "roles": item.roles.upper(), "date_created": item.date_created.strftime('%Y-%m-%d %H:%M') })


  return jsonify({'list': users, 'columns': columns, 'orderBy': orderBy, 'orderDirect': orderDirection, 'pagination': pageInfo})


@bprint.route('/users', methods=['DELETE'])
@jwt_required
def delete_user():
  current_user_roles = get_jwt_claims()["roles"]
  if ADMIN_ROLE_NAME not in current_user_roles:
    return jsonify({"message": "你无权访问该资源", "code": -1}), 404

  id = request.args.get('user_id')
  if id != None and re.match("\d+", id):
    db.session.query(User).filter(User.id == id).delete()
    db.session.commit()
    db.session.close()
    return jsonify({"code": 1, "message": "删除成功"})

  else:
    return jsonify({"code": -1, "message": "无效的 id %s" % id})

@bprint.route('/user_frozen', methods=['PUT'])
@jwt_required
def frozen_user():
  current_user_roles = get_jwt_claims()["roles"]
  if ADMIN_ROLE_NAME not in current_user_roles:
    return jsonify({"message": "你无权访问该资源", "code": -1}), 404

  id = request.args.get('user_id')
  if id != None and re.match("\d+", id):
    user = db.session.query(User).filter(User.id == id).first()
    if user:
      if not user.isFrozen:
        user.isFrozen = True 
      else:
        user.isFrozen = False 

      db.session.commit()
      db.session.close()
      return jsonify({"code": 1, "message": "冻结成功"})
    else:
      return jsonify({"code": -1, "message": "无效的 id %s" % id})
  else:
    return jsonify({"code": -1, "message": "无效的 id %s" % id})

@bprint.route('/user', methods=['POST'])
@jwt_required
def add_edit_user():
  current_user_roles = get_jwt_claims()["roles"]
  if ADMIN_ROLE_NAME not in current_user_roles:
    return jsonify({"message": "你无权访问该资源", "code": -1}), 404

  content = request.get_json()  #request.get_data()
  if content["roles"] == ADMIN_ROLE_NAME:
    return jsonify({"message": "你无权更新成该角色", "code": -1})

  if content["id"] != None and content["id"] != '':
    user = db.session.query(User).filter(User.id == content["id"]).first()
    if user:
      user.roles = content["roles"]
      user.username = content["username"]
      user.expirationTime = content["expirationTime"]
      db.session.commit()
      return jsonify({"message": "成功", "code": 1})

  else:
    if db.session.query(exists().where(User.mobile == content["mobile"])).scalar() == False:
      user = User(content["username"], content["mobile"], DEFAULT_USER_PWD, content["expirationTime"])
      user.email = '%s@gmail.com' % content["mobile"]
      user.roles = content["roles"]
      db.session.add(user)
      db.session.commit()
      return jsonify({"message": "成功", "code": 1})
    else:
      return jsonify({"message": "该用户已经存在，不能重复添加", "code": -1})


  