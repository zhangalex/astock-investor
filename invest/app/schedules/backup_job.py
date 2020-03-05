from app import db
from app import app
from . import LOGGER

from app import celery 

import os
import datetime 

@celery.task(autoretry_for=(Exception,),
          retry_kwargs={'max_retries': 3})
def run():
  backupPath = app.config['BACKUP_DATA_PATH']
  todayFilePath = '%s%s.sql' % (backupPath, datetime.datetime.now().strftime('%Y%m%d'))
  command = 'mysqldump -uroot --password="%s" investor_daily > %s' % ('start123', todayFilePath)
  os.system(command)

  #删除2天之前的备份
  preFiveDay = datetime.datetime.now() - datetime.timedelta(days=2)
  preFiveDayFile = '%s%s.sql' % (backupPath, preFiveDay.strftime('%Y%m%d'))
  if os.path.isfile(preFiveDayFile):
    os.remove(preFiveDayFile)
    
