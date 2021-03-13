from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
Base = declarative_base()
engine = create_engine('sqlite:///users.db', echo=True)
class User(Base):
    __tablename__="users"


    uid=Column('uid', Integer, primary_key=True)
    username = Column('username', String)
    password = Column('password', String)
    #TODO: location
    in_event = Column('in_event', Boolean)

class Event(Base):
    __tablename__="events"


    eid=Column('eid', Integer, primary_key=True)
    code = Column('code', Integer)
    #TODO: location
    #TODO: list of users and if they need a ride/can give a ride (json)
    organiser_id = Column('event_organiser', Integer) #user id


class Request(Base):
    __tablename__="requests"

    rid = Column('rid', Integer, primary_key=True)
    requesting_id=Column('requesting_id', String)
    receivening_id=Column('receivening_id', String)
    event_id = Column('event_id', Integer)

engine = create_engine('sqlite:///users.db', echo=True)
Base.metadata.create_all(bind=engine)
Session = sessionmaker(bind =engine)

session = Session()
user = User()
user.uid = 0
user.username = "hello"
user.password = "passwordsample"
user.in_event = False

session.add(user)
session.commit()

session.close()