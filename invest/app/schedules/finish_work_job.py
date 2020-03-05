from app import db
from app import app
from app.models.main import Participant, HolderBase, NorthFlow
from app.common import tradeday, helper
from . import LOGGER

from app import celery
from sqlalchemy.sql import exists
from sqlalchemy import func
from datetime import datetime, timedelta
from pypinyin import pinyin, lazy_pinyin
import pypinyin
from elasticsearch import Elasticsearch

from . import inform_job

ES_CLIENT = Elasticsearch()

@celery.task(autoretry_for=(Exception,),
          retry_kwargs={'max_retries': 3})
def run():
  preDay = (datetime.today() - timedelta(days=1)).strftime('%Y-%m-%d')
  if preDay in tradeday.trade_days:
    with db.app.app_context():
      nf = db.session.query(NorthFlow).order_by(NorthFlow.recordDate.desc()).first()
      pts = db.session.query(Participant.code).filter(Participant.recordDate == nf.recordDate).distinct()
      for item in pts:
        if item.code.strip() == '':
          continue 

        if db.session.query(exists().where(HolderBase.code == item.code)).scalar() == False:
          name = db.session.query(Participant).filter(Participant.code == item.code, Participant.recordDate == nf.recordDate).first().name 
          pys = pinyin(name, style=pypinyin.FIRST_LETTER)
          pyname = ''.join([i[0] for i in pys]) 
          holder = HolderBase(item.code, name, pyname)
          db.session.add(holder)
          # warm_indexes(item.code, name)

      db.session.commit()


  else: 
    LOGGER.info('%s is not trade day.' % preDay)  

# def warm_indexes(code = None, name = None):

#   if code != None and name != None:
#     ES_CLIENT.index(index="holders", doc_type="hsgt", id=code, body={'code': code, 'name': name})

#   else:
#     records = db.session.query(HolderBase).all()
#     for item in records:
#       ES_CLIENT.index(index="holders", doc_type="hsgt", id=item.code, body={'code': item.code, 'name': item.name})

