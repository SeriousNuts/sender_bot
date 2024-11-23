from sqlalchemy import func
from sqlalchemy.orm import sessionmaker
from db_models import Message, engine

Session = sessionmaker(bind=engine)
session = Session()

class Stats:
    schedule_uuid = ""
    sended_message_count = 0
    bad_request_message_count = 0
    forbidden_message_count = 0
    flood_wait_message_count = 0
    not_sended_message_count = 0
    not_found_message_count = 0



