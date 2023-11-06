from apscheduler.executors.pool import ProcessPoolExecutor
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore

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
