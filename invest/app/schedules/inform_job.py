import requests
from app import celery 

@celery.task(autoretry_for=(Exception,),
          retry_kwargs={'max_retries': 3})
def send_to_wx(title, desc=''):
  url = 'https://sc.ftqq.com/SCU19880Te116691c07d63925173ee3175f92533d5a55b93258cfd.send?text=%s&desp=%s' % (title, desc)
  requests.post(url)
