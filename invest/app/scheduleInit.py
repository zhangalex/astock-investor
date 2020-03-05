import atexit
import fcntl
from flask_apscheduler import APScheduler

#初始化，并为 schedule 添加文件锁，确保 gunicorn 启动多个worker时，只实例化一个 scheduler 实例
#ref: http://blog.csdn.net/raptor/article/details/69218271 

def init(app):
    f = open("scheduler.lock", "wb")
    try:
        fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
        scheduler = APScheduler()
        scheduler.init_app(app)
        scheduler.start()
    except:
        pass
    def unlock():
        fcntl.flock(f, fcntl.LOCK_UN)
        f.close()
    atexit.register(unlock)
