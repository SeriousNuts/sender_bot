from sqlalchemy import create_engine, Column, Integer, String, BigInteger, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

engine = create_engine("postgresql://postgreadmin:738818@89.108.114.174:3090/sender_bot")
Base = declarative_base()


class Account(Base):
    __tablename__ = 'accounts'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    owner_tg_id = Column(BigInteger, index=True)
    api_code = Column(String)
    api_hash = Column(String)
    status = Column(String)

    def account(self, name, owner_tg_id, api_code, api_hash, status):
        self.name = name
        self.owner_tg_id = owner_tg_id
        self.api_code = api_code
        self.api_hash = api_hash
        self.status = status


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
    owner_tg_id = Column(String)