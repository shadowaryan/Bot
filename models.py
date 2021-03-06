from platform import platform
from urllib import response
from numpy import integer
from sqlalchemy import INTEGER, Column, Integer, String, Sequence, ForeignKey, Float, false
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.types import TIMESTAMP

from postgresql_json import JSON
from datetime import datetime


Base = declarative_base()

class CustomBase(Base):
    __abstract__ = True
    created_at = Column(TIMESTAMP, default=datetime.utcnow, nullable=False)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class User(CustomBase):
    __tablename__ = 'user'
    id = Column(Integer, Sequence('user_id_seq'), primary_key=True)
    user_id = Column(String(128), unique=True, nullable=False)
    platform = Column(String(32))

    telegram_user = relationship('Telegram_User', back_populates='user')
    discord_user = relationship('Discord_User', back_populates='user')
    contract = relationship('Contract', back_populates='user')
    collections = relationship('Collection', secondary = 'user_collection', back_populates='users')

class Telegram_User(CustomBase):
    __tablename__ = 'telegram_user'
    id = Column(Integer, Sequence('telegram_user_id_seq'), primary_key=True)

    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship('User', back_populates='telegram_user')

    username = Column(String(128)) #shadowaryan 
    chat_id = Column(Integer) #123456789
    chat_type = Column(String(64)) #private , group , channel
    
class Discord_User(CustomBase):
    __tablename__ = 'discord_user'
    id = Column(Integer, Sequence('discord_user_id_seq'), primary_key=True)

    user_id = Column(Integer, ForeignKey('user.id')) #4654885348666
    set_nft_channel_name = Column(String(64)) #channel name = set-nft
    set_nft_channel_id = Column(String(128)) #sales-nft = 953565311741857793
    server_id = Column(String(128)) #950674739133808690
    user = relationship('User', back_populates='discord_user')
    
    #username = Column(String(50)) #shadowaryan 
    #chat_id = Column(Integer) #123456789
    #chat_type = Column(String(50)) #private , group , channel


class User_Collection(CustomBase):
    __tablename__ = 'user_collection'
    user_id = Column(Integer, ForeignKey('user.id'),primary_key=True)
    collection_id = Column(Integer, ForeignKey('collection.id'), primary_key=True)


class Collection(CustomBase):
    __tablename__ = 'collection'
    id = Column(Integer, Sequence('collection_id_seq'), primary_key=True)
    slug = Column(String(128))
    floor_price = Column(Float(10,5))
    count = Column(Float(10,5),nullable=False)

    users = relationship('User', secondary = 'user_collection', back_populates='collections')
    contract = relationship('Contract', back_populates='collection')
    history = relationship('History', back_populates='collection')


class Contract(CustomBase):
    __tablename__ = 'contract'
    id = Column(Integer, Sequence('contract_id_seq'), primary_key=True)

    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship('User', back_populates='contract')
    collection_id = Column(Integer, ForeignKey('collection.id'))
    collection = relationship('Collection', back_populates='contract')
    channel_id = Column(String(128)) #sales-nft = 953565311741857793

    contract_address = Column(String(512), nullable=False)
    contract_type = Column(String(512)) # non-fungiable,semi-fungiable
    latest_transaction_hash = Column(String(512))
    total_transaction = Column(String(512)) #no of transaction


class History(CustomBase):
    __tablename__ = 'history'
    id = Column(Integer,Sequence('history_id_seq'), primary_key=True)

    collection_id = Column(Integer, ForeignKey('collection.id'))
    collection = relationship('Collection', back_populates='history')
    
    one_day_volume = Column(Float(10,5),nullable=False)
    one_day_change = Column(Float(10,5),nullable=False)
    one_day_sales = Column(Float(10,5),nullable=False)
    one_day_average_price = Column(Float(10,5),nullable=False)
    seven_day_volume = Column(Float(10,5),nullable=False)
    seven_day_change = Column(Float(10,5),nullable=False)
    seven_day_sales = Column(Float(10,5),nullable=False)
    seven_day_average_price = Column(Float(10,5),nullable=False)
    thirty_day_volume = Column(Float(10,5),nullable=False)
    thirty_day_change = Column(Float(10,5),nullable=False)
    thirty_day_sales = Column(Float(10,5),nullable=False)
    thirty_day_average_price = Column(Float(10,5),nullable=False)
    total_volume = Column(Float(10,5),nullable=False)
    total_sales = Column(Float(10,5),nullable=False)
    total_supply = Column(Float(10,5),nullable=False)
    count = Column(Float(10,5),nullable=False)
    num_owners = Column(Float(10,5),nullable=False)
    average_price = Column(Float(10,5),nullable=False)
    num_reports = Column(Float(10,5),nullable=False)
    market_cap = Column(Float(10,5),nullable=False)
    floor_price = Column(Float(10,5),nullable=False)
    #response_json = Column(JSON)
