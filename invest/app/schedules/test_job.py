from app import db
from app import app
from app.models.main import User 
from . import LOGGER
from app import celery 

@celery.task
def run():
  try:
    with db.app.app_context():
      user = db.session.query(User).first()
      LOGGER.info('user: %s' % user.username)
  except Exception as e:
    LOGGER.error(e)