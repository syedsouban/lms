from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler

def schedule(methods, *args, **kargs):
    scheduler = BackgroundScheduler()
    for method in methods:
        scheduler.add_job(method, trigger='date', next_run_time=datetime.now(), args=args, kwargs=kargs)
    scheduler.start()