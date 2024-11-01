from datetime import timedelta, datetime
from enum import Enum

from sqlalchemy import create_engine, Column, Integer, String, BigInteger, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import configparser
config = configparser.ConfigParser()
config.read('config.ini')
username = config['secrets']['username']
password = config['secrets']['password']
server_ip = config['secrets']['server_ip']
server_port = config['secrets']['server_port']
db = config['secrets']['db']
engine = create_engine(f"postgresql://{username}:{password}@{server_ip}:{server_port}/{db}")
Base = declarative_base()


class StatusMessage(Enum):
    SENDED = 0
    FORBIDDEN = 1
    BADREQUEST = 2
    FLOOD = 3
    NOTSENDED = 4
    NOTFOUND = 5


class Message(Base):
    __tablename__ = 'messages'
    id = Column(Integer, primary_key=True)
    text = Column(String)
    sending_date = Column(DateTime())
    status = Column(Integer, index=True)
    channel = Column(String)
    account_name = Column(String)
    schedule_owner_id = Column(String)
    flood_wait_time = Column(Integer)

    def set_message(self, text, sending_date, status, channel):
        self.text = text
        self.sending_date = sending_date
        self.status = status
        self.channel = channel

    def set_flood_wait_time(self, flood_wait_time):
        self.flood_wait_time = flood_wait_time


class Account(Base):
    __tablename__ = 'accounts'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    app_id = Column(Integer)
    api_hash = Column(String)
    status = Column(String)
    last_use = Column(DateTime())
    owner_id = Column(BigInteger)
    session_token = Column(String)

    def account(self, name, app_id, api_hash, status):
        self.name = name
        self.app_id = app_id
        self.api_hash = api_hash
        self.status = status

    def last_use_up(self, period):
        self.last_use = datetime.now() + timedelta(minutes=period)


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    tg_id = Column(BigInteger, index=True, unique=True)
    status = Column(String)
    last_pay_date_pay = Column(DateTime())
    subs_month = Column(Integer)
    channels = relationship("Channel")


class Channel(Base):
    __tablename__ = 'channels'
    id = Column(Integer, primary_key=True)
    url = Column(String)
    owner_tg_id = Column(BigInteger, index=True)
    author_id = Column(Integer, ForeignKey('users.id'))


class Schedule(Base):
    __tablename__ = 'schedules'
    id = Column(Integer, primary_key=True)
    period = Column(Integer)  # частота рассылки в минутах
    last_sening = Column(DateTime())
    next_sending = Column(DateTime())
    status = Column(String)
    text = Column(String)
    owner_tg_id = Column(BigInteger)


class Setting(Base):
    __tablename__ = 'settings'
    id = Column(Integer, primary_key=True)
    account = Column(String)
    max_wait_time = Column(Integer)
    type = Column(String)
