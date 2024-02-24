import asyncio

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pytz import utc

from apscheduller.jobs.change_acc import change_account
from apscheduller.jobs.sending_job import send_messages
from apscheduller.scheduler_conf import jobstores, executors, job_defaults

scheduler = AsyncIOScheduler()

scheduler.add_job(send_messages, "interval", seconds=3)
scheduler.add_job(change_account, "interval", seconds=1800)
scheduler.start()
print("==jobs scheduller started==")
try:
    asyncio.get_event_loop().run_forever()
except ConnectionResetError:
    pass
scheduler.configure(jobstores=jobstores, executors=executors, job_defaults=job_defaults, timezone=utc)
