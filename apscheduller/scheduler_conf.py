import asyncio

from apscheduler.executors.pool import ProcessPoolExecutor
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pytz import utc

from apscheduller.jobs.sending_job import get_schedules
from db_models import engine
jobstores = {
    'postgre': {'type': 'postgre'},
    'default': SQLAlchemyJobStore(engine=engine)
}
executors = {
    'default': {'type': 'threadpool', 'max_workers': 20},
    'processpool': ProcessPoolExecutor(max_workers=5)
}
job_defaults = {
    'coalesce': False,
    'max_instances': 3
}
scheduler = AsyncIOScheduler()

scheduler.add_job(get_schedules, "interval", seconds=3)

scheduler.start()

asyncio.get_event_loop().run_forever()

scheduler.configure(jobstores=jobstores, executors=executors, job_defaults=job_defaults, timezone=utc)
