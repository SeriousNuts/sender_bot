from sqlalchemy.orm import sessionmaker

from db_models import engine
from psql_core.utills import change_account_db

Session = sessionmaker(bind=engine)
session = Session()


async def change_account():
    await change_account_db("send")

