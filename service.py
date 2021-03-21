from contextlib import contextmanager
import datetime
from pytz import utc
import time

from apscheduler.schedulers.background import BackgroundScheduler

# from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
# from apscheduler.executors.pool import ThreadPoolExecutor

import settings


class SubscriptionManager:
    def __init__(self):

        # jobstores = {
        #     "default": SQLAlchemyJobStore(url=f"sqlite:///{settings.SCHED_JOB_STORAGE}")
        # }
        # executors = {
        #     "default": {"type": "threadpool", "max_workers": 2},

        # }
        # job_defaults = {
        #     "coalesce": False,
        #     "max_instances": 3
        # }

        # self._scheduler = BackgroundScheduler(jobstores=jobstores,
        #                                       executors=executors,
        #                                       job_defaults=job_defaults,
        #                                       timezone=utc,)

        self._scheduler = BackgroundScheduler()

    def start(self):
        self._scheduler.start()

    def stop(self):
        self._scheduler.shutdown()

    def subscribe(self, callback):
        self._job = self._scheduler.add_job(
            callback,
            trigger="interval",
            seconds=10,
        )

    def unsubscribe(self):
        self._job.remove()


@contextmanager
def scoped_scheduler(sched):
    scheduler = sched
    try:
        scheduler.start()
        yield scheduler
    finally:
        print("shutdown scheduler")
        scheduler.shutdown()


def task():
    print("{0}: Hi!".format(datetime.datetime.now()))


def main():
    manager = SubscriptionManager()
    try:
        manager.start()
        manager.subscribe(task)

        time.sleep(60)

        manager.unsubscribe()
    finally:
        manager.stop()


if __name__ == "__main__":
    main()
