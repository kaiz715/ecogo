from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import random


Base = declarative_base()
engine = create_engine('sqlite:///users.db', echo=True)

class User(Base):
    __tablename__="users"


    uid=Column('uid', Integer, primary_key=True)
    first_name = Column('first_name', String)
    last_name = Column('last_name', String)
    username = Column('username', String, unique = True)
    password = Column('password', String)
    phone_number = Column('phone_number', String)
    email = Column('email', String)
    address = Column('address', String)
    in_event = Column('in_event', Boolean)

class Event(Base):
    __tablename__="events"


    eid=Column('eid', Integer, primary_key=True)
    code = Column('code', Integer, unique = True)
    location = Column('location', String)
    event_name = Column('event_name', String)
    participants = Column('participants', JSON)
    organiser_id = Column('event_organiser', Integer) #user id


class Request(Base):
    __tablename__="requests"

    rid = Column('rid', Integer, primary_key=True)
    requesting_id=Column('requesting_id', String)
    receiving_id=Column('receiving_id', String)
    event_id = Column('event_id', Integer)
    status = Column('status', String)

Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)