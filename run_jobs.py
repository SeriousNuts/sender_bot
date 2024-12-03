import asyncio
import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pytz import utc

from apscheduller.jobs.sending_message_job import send_messages
from apscheduller.jobs.sending_delayd_message_job import send_delayed_messages
from apscheduller.scheduler_conf import jobstores, executors, job_defaults
logging.basicConfig(level=logging.INFO, filename="py_log.log", filemode="a",
                    format="%(asctime)s %(levelname)s %(message)s")
scheduler = AsyncIOScheduler()

scheduler.add_job(send_messages, "interval", seconds=3)
scheduler.add_job(send_delayed_messages, "interval", seconds=5)
scheduler.start()
print("==jobs scheduller started==")
try:
    asyncio.get_event_loop().run_forever()
except ConnectionResetError:
    pass
scheduler.configure(jobstores=jobstores, executors=executors, job_defaults=job_defaults, timezone=utc)
