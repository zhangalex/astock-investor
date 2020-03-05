# Statement for enabling the development environment
DEBUG = True

# Define the application directory
import os
import datetime
from celery.schedules import crontab

BASE_DIR = os.path.abspath(os.path.dirname(__file__))  

# Define the database - we are working with
# SQLite for this example
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:start123@127.0.0.1:3306/investor_daily?charset=utf8'
DATABASE_CONNECT_OPTIONS = {}

SQLALCHEMY_ECHO = False
SQLALCHEMY_TRACK_MODIFICATIONS = True
# Application threads. A common general assumption is
# using 2 per available processor cores - to handle
# incoming requests using one and performing background
# operations using the other.
THREADS_PER_PAGE = 2

# Enable protection agains *Cross-site Request Forgery (CSRF)*
CSRF_ENABLED     = True

# Use a secure, unique and absolutely secret key for
# signing the data. 
CSRF_SESSION_KEY = "secret-ai"

# Secret key for signing cookies
SECRET_KEY = "secret-ai-finance"

#for jwt
JWT_SECRET_KEY = "ai-finance-secret"
#JWT_ACCESS_TOKEN_EXPIRES = datetime.timedelta(days=1)  #jwt 访问失效时长
JWT_ACCESS_TOKEN_EXPIRES = False #不使用它自带的失效方式
JWT_HEADER_TYPE = "AiBearer"
CUSTOM_JWT_TOKEN_EXPIRES = 8 * 60 * 60 #seconds

#for spider
DAILY_DATA_PATH = "/var/opt/projects/daily-data/"
BACKUP_DATA_PATH = "/var/opt/projects/databackup/"
PE_FILE_PATH = "/var/opt/projects/simu/data/pp.csv"

#SMS
YUNPIAN_API_KEY = 'b9f92d502425f12a1d4b4dd4e6075404'

#For Cache
CACHE_REDIS_URL = 'redis://127.0.0.1:6379/8'

#Celery Config
CELERY_RESULT_BACKEND = 'redis://127.0.0.1:6379/5'
CELERY_BROKER_URL = 'redis://127.0.0.1:6379/6'
CELERY_TIMEZONE = 'Asia/Shanghai'
CELERYBEAT_SCHEDULE = {
    'dailyRecord_job': {
      'task': 'app.schedules.dailyRecord_job.run',
      'schedule': crontab(minute='35', hour='15'),
    },
    'hkdailyrecord_job': {
      'task': 'app.schedules.hkdailyrecord_job.run',
      'schedule': crontab(minute='40', hour='16'),
    },
    'northflow_job': {
      'task': 'app.schedules.northflow_job.run',
      'schedule': crontab(minute='10', hour='3-4'),
    },
    'shortStat_job': {
      'task': 'app.schedules.shortStat_job.run',
      'schedule': crontab(minute='40', hour='4'),
    },
    'fetchall_holders_job': {
      'task': 'app.schedules.fetchall_holders_job.run',
      'schedule': crontab(minute='1', hour='5'),
    },
    'finish_work_job': {
      'task': 'app.schedules.finish_work_job.run',
      'schedule': crontab(minute='50', hour='5'),
    },
    'fetchall_xueqiu_job': {
      'task': 'app.schedules.fetchall_xueqiu_job.run',
      'schedule': crontab(minute='30', hour='4'),
    },
    'checker_job': {
      'task': 'app.schedules.checker_job.run',
      'schedule': crontab(minute='20', hour='6,17'),
    },
    'backup_job': {
      'task': 'app.schedules.backup_job.run',
      'schedule': crontab(minute='0', hour='12'),
    },
    'fetchall_mainCapital_job': {
      'task': 'app.schedules.fetchall_mainCapital_job.run',
      'schedule': crontab(minute='0', hour='17'),
    },
    'fetchall_hkShortSell_job': {
      'task': 'app.schedules.fetchall_hkShortSell_job.run',
      'schedule': crontab(minute='30', hour='18'),
    }
}