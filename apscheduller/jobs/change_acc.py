from sqlalchemy.orm import sessionmaker

from db_models import engine
from psql_core.utills import change_account_db

Session = sessionmaker(bind=engine)
session = Session()


# задание для смены аккаунта раз в заданный интервал
async def change_account():
    await change_account_db("send")
