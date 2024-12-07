from datetime import datetime, timedelta

from sqlalchemy import func
from sqlalchemy.orm import sessionmaker

from db_models import Message, engine

Session = sessionmaker(bind=engine)
session = Session()


class Stats:
    sended_message_count = 0
    forbidden_message_count = 0
    bad_request_message_count = 0
    flood_wait_message_count = 0
    not_sended_message_count = 0
    not_found_message_count = 0

    def stats(self, sended_message_count, forbidden_message_count, bad_request_message_count,
              flood_wait_message_count, not_sended_message_count, not_found_message_count):
        self.sended_message_count = sended_message_count
        self.forbidden_message_count = forbidden_message_count
        self.bad_request_message_count = bad_request_message_count
        self.flood_wait_message_count = flood_wait_message_count
        self.not_sended_message_count = not_sended_message_count
        self.not_found_message_count = not_found_message_count

    def get_stats_from_row(self, row):
        self.sended_message_count = row[0]
        self.forbidden_message_count = row[1]
        self.bad_request_message_count = row[2]
        self.flood_wait_message_count = row[3]
        self.not_sended_message_count = row[4]
        self.not_found_message_count = row[5]

    def get_all_message_count(self):
        return self.sended_message_count + self.forbidden_message_count + self.bad_request_message_count + \
               self.flood_wait_message_count + self.not_found_message_count + self.not_sended_message_count


async def get_full_stats_by_schedule_owner_id(schedule_owner_id):
    result = session.query(
        func.count().filter(Message.status == 0).label('sended_message_count'),
        func.count().filter(Message.status == 1).label('forbidden_message_count'),
        func.count().filter(Message.status == 2).label('bad_request_message_count'),
        func.count().filter(Message.status == 3).label('flood_wait_message_count'),
        func.count().filter(Message.status == 4).label('not_sended_message_count'),
        func.count().filter(Message.status == 5).label('not_found_message_count')
    ).filter(Message.schedule_owner_id == schedule_owner_id).one()
    stats = Stats()
    stats.get_stats_from_row(row=result)
    return stats


async def get_stats_by_schedule_uuid(schedule_uuid):
    result = session.query(
        func.count().filter(Message.status == 0).label('sended_message_count'),
        func.count().filter(Message.status == 1).label('forbidden_message_count'),
        func.count().filter(Message.status == 2).label('bad_request_message_count'),
        func.count().filter(Message.status == 3).label('flood_wait_message_count'),
        func.count().filter(Message.status == 4).label('not_sended_message_count'),
        func.count().filter(Message.status == 5).label('not_found_message_count')
    ).filter(Message.schedule_uuid == schedule_uuid).one()
    stats = Stats()
    stats.get_stats_from_row(row=result)
    return stats


async def get_stats_by_interval(schedule_owner_id, days_before: int):
    result = session.query(
        func.count().filter(Message.status == 0).label('sended_message_count'),
        func.count().filter(Message.status == 1).label('forbidden_message_count'),
        func.count().filter(Message.status == 2).label('bad_request_message_count'),
        func.count().filter(Message.status == 3).label('flood_wait_message_count'),
        func.count().filter(Message.status == 4).label('not_sended_message_count'),
        func.count().filter(Message.status == 5).label('not_found_message_count')
    ).filter(
        Message.schedule_owner_id == schedule_owner_id,
        Message.sending_date >= datetime.now() - timedelta(days=days_before)
    ).one()
    stats = Stats()
    stats.get_stats_from_row(row=result)
    return stats
