from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Boolean
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
    #TODO: list of users and if they need a ride/can give a ride (json)
    organiser_id = Column('event_organiser', Integer) #user id


class Request(Base):
    __tablename__="requests"

    rid = Column('rid', Integer, primary_key=True)
    requesting_id=Column('requesting_id', String)
    receivening_id=Column('receivening_id', String)
    event_id = Column('event_id', Integer)

Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
# engine = create_engine('sqlite:///users.db', echo=True)
# Base.metadata.create_all(bind=engine)
# Session = sessionmaker(bind =engine)

# session = Session()
# user = User()
# user.uid = 3
# user.username = "helloyoo"
# user.password = "passwordsample"
# user.address = "2768 Richmond Road, Beachwood, Ohio, 44122"
# user.in_event = False

# session.add(user)
# session.commit()

# session.close()

# session = Session()
# event = Event()
# event.eid = 0#session.query(func.max(event.eid)).first()[0]+1
# code = random.randint(0,1000000)
# while session.query(Event.code).filter_by(code = code).first() != None:
#     code = random.randint(0,1000000)
# event.code = code
# event.location = "location"
# event.organiser_id = 123

# session.add(event)

# session.commit()

# session.close()

