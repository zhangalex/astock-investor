from app import db
from app import app
from app.models.main import Simu
from . import LOGGER
from app import celery 
import csv
from datetime import datetime

@celery.task(autoretry_for=(Exception,),
          retry_kwargs={'max_retries': 3})
def run():
  peFilePath = app.config['PE_FILE_PATH']
  records =  csv.DictReader(open(peFilePath))
  with db.app.app_context():
    for row in records:
      simu = db.session.query(Simu).filter(Simu.registerNo == row['registerNo']).first()
      isNotExisted = (simu == None)
      if simu == None:
        simu = Simu()

      simu.artificialPersonName            = row['artificialPersonName']
      simu.aregisterProvince               = row['registerProvince']
      simu.subscribedCapital               = '%.4f' % float(row['subscribedCapital'])
      simu.registerAddress                 = row['registerAddress']
      simu.fundCount                       = row['fundCount']
      simu.primaryInvestType               = row['primaryInvestType']
      simu.officeCity                      = row['officeCity']
      simu.hasSpecialTips                  = row['hasSpecialTips']
      simu.officeCoordinate                = row['officeCoordinate']
      simu.establishDate                   = row['establishDate']
      simu.officeAddress                   = row['officeAddress']
      simu.fundScale                       = '%.4f' % float(row['fundScale'])
      simu.regAdrAgg                       = row['regAdrAgg']
      simu.managerHasProduct               = row['managerHasProduct']
      # simu.innerid                         = row['innerid']
      simu.registerNo                      = row['registerNo']
      simu.inBlacklist                     = row['inBlacklist']
      simu.registerDate                    = row['registerDate'] if row['registerDate'] != '' else None
      if simu.registerDate != None:
        tmpDate = datetime.strptime(simu.registerDate, "%Y-%m-%d")
        simu.registerYear                  = tmpDate.strftime("%Y")
        simu.registerYearMonth             = tmpDate.strftime("%Y%m")

      simu.registerCity                    = row['registerCity']
      simu.regCoordinate                   = row['regCoordinate']
      simu.managerName                     = row['managerName']
      simu.officeProvince                  = row['officeProvince']
      simu.hasCreditTips                   = row['hasCreditTips']
      simu.url                             = row['url']
      simu.paidInCapital                   = '%.4f' % float(row['paidInCapital'])


      if isNotExisted:
        db.session.add(simu)

    db.session.commit()





