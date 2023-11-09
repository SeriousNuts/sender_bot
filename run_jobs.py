import asyncio

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pytz import utc

from apscheduller.jobs.sending_job import get_schedules
from apscheduller.scheduler_conf import jobstores, executors, job_defaults

scheduler = AsyncIOScheduler()

scheduler.add_job(get_schedules, "interval", seconds=3)

scheduler.start()

asyncio.get_event_loop().run_forever()
print("==jobs scheduller started==")
scheduler.configure(jobstores=jobstores, executors=executors, job_defaults=job_defaults, timezone=utc)
