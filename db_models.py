from sqlalchemy import create_engine, Column, Integer, String, DateTime, BigInteger, MetaData
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine("postgresql://postgreadmin:738818@89.108.114.174:3090/sender_bot")
Base = declarative_base()


class Account(Base):
    __tablename__ = 'accounts'
    id = Column(Integer, primary_key=True)
    owner_tg_id = Column(BigInteger, index=True)
    api_code = Column(String)
    api_hash = Column(String)
    status = Column(String)
