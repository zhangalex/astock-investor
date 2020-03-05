from celery import Celery

def make_celery(app):
    jobs = ['app.schedules.%s_job' % name for name in ['backup', 
                                                        'channel_holders', 
                                                        'dailyRecord', 
                                                        'hkdailyrecord', 
                                                        'northflow', 
                                                        'shortStat',
                                                        'fetchall_holders',
                                                        'inform','test', 
                                                        'checker',
                                                        'finish_work',
                                                        'pe', 
                                                        'notify', 
                                                        'hkShortSell', 
                                                        'mainCapitalFlow', 
                                                        'fetchall_hkShortSell', 
                                                        'fetchall_mainCapital', 
                                                        'fetchall_xueqiu']]
    celery = Celery(app.import_name, backend=app.config['CELERY_RESULT_BACKEND'],
                    broker=app.config['CELERY_BROKER_URL'], include=jobs)
    celery.conf.update(app.config)
    TaskBase = celery.Task
    class ContextTask(TaskBase):
        abstract = True
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)
    celery.Task = ContextTask
    return celery