from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Boolean, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from db import User, Event, Request, Session
import random, time

# TODO: list of users in event


def next_id(db):
    session = Session()
    if db == 'user':
        first = session.query(func.max(User.uid)).first()[0]
    elif db == 'request':
        first = session.query(func.max(Request.rid)).first()[0]
    elif db == 'event':
        first = session.query(func.max(Event.eid)).first()[0]
    session.close()
    
    if first != None:
        return first + 1
    else:
        return 0


def unique_check(username):
    session = Session()
    user = session.query(User.username).filter_by(username=username).first()
    session.close()
    if user != None:
        return False
    else:
        return True


def credential_check(username, password):  # returns -1 if username doesnt exist
    # returns uid of person
    session = Session()
    user = session.query(User).filter_by(username=username).first()
    if user == None:
        session.close()
        return -1
    if password == user.password:
        uid = user.uid
        session.close()
        return uid
    else:
        session.close()
        return False


# def create_user(
#     first_name, last_name, username, password, address, phone_number, email
# ):
#     session = Session()
#     if unique_check(username) == False:
#         return False  # if username already exists
#     user = User()
#     user.uid = next_uid()
#     user.username = username
#     user.password = password
#     user.first_name = first_name
#     user.last_name = last_name
#     user.phone_number = phone_number
#     user.email = email
#     user.address = address
#     user.in_event = False
#     session.add(user)
#     session.commit()
#     session.close()


class FunctionUser:
    def __init__( #IMPORTANT: check if unique username first by using unique_check()
        self, first_name, last_name, username, password, address, phone_number, email
    ):
        session = Session()
        user = User()

        user.uid = next_id('user')
        user.username = username
        user.password = password
        user.first_name = first_name
        user.last_name = last_name
        user.phone_number = phone_number
        user.email = email
        user.address = address

        self.uid = user.uid
        self.username = username
        self.password = password
        self.first_name = first_name
        self.last_name = last_name
        self.phone_number = phone_number
        self.email = email
        self.address = address

        session.add(user)
        session.commit()
        session.close()

    @classmethod
    def from_db(cls, uid):
        session = Session()
        user = session.query(User).filter_by(uid=uid).first()
        self.uid = user.uid
        self.username = user.username
        self.password = user.password
        self.first_name = user.first_name
        self.last_name = user.last_name
        self.phone_number = user.phone_number
        self.email = user.email
        self.address = user.address
        self.events = user.events.copy()
        session.close()

    def join_event(self, eid, availability):
        session = Session()
        event = FunctionEvents.from_db(eid)
        event.add_user(self.uid, availability)  # TODO: implement event class and add_user
        session.close()
    
    def get_events(self):
        events_list = []
        session = Session()
        events = session.query(Event).all()
        for i in events:
            try:
                if i.participants[str(uid)] != None:
                    events_list.append(i.eid)
            except Exception:
                pass
        return events_list
    
    def make_request(self, receiving_id, event_id):
        FunctionRequests(self.uid, receiving_id, event_id)
        
    def get_sent_requests(self):
        sent_requests = []
        session = Session()
        requests = session.query(Request).filter_by(requesting_id=self.uid).all()
        for request in requests:
            sent_requests.append(FunctionRequests.from_db(request.rid))
        session.close()
        return sent_requests

    def get_receiving_requests(self):
        receiving_requests = []
        session = Session()
        requests = session.query(Request).filter_by(receiving_id=self.uid).all()
        for request in requests:
            receiving_requests.append(FunctionRequests.from_db(request.rid))
        session.close()
        return receiving_requests
    
    def update_request(self, rid, new_status):
        session = Session()
        request = session.query(Request).filter_by(rid = rid).first()
        request.status = new_status
        session.add(request)
        session.commit()
        session.close()


class FunctionRequests:
    def __init__(self, requesting_id, receiving_id, event_id):
        session = Session()
        request = Request()

        request.rid = next_id('request')
        request.requesting_id = requesting_id
        request.receiving_id = receiving_id
        request.event_id = event_id
        request.status = 'default'


        self.rid = request.rid
        self.requesting_id = requesting_id
        self.receiving_id = receiving_id
        self.event_id = event_id
        self.status = 'default'

        session.add(request)
        session.commit()
        session.close()

    @classmethod
    def from_db(cls, rid):
        session = Session()
        request = session.query(Request).filter_by(rid=rid).first()
        self.rid = rid
        self.requesting_id = request.requesting_id
        self.receiving_id = request.receiving_id
        self.event_id = request.event_id
        self.status = request.status
        session.close()

    def update_request(self, new_status):
        session = Session()
        request = session.query(Request).filter_by(rid = self.rid).first()
        request.status = new_status
        session.add(request)
        session.commit()
        session.close()

class FunctionEvents:
    def __init__(self, location, organiser_id, event_name):
        session = Session()

        code = random.randint(0,1000000)
        while session.query(Event.code).filter_by(code = code).first() != None:
            code = random.randint(0,1000000)

        event = Event()
        event.eid = next_id('event')
        event.code = code
        event.location = location
        event.organiser_id = organiser_id
        event.event_name = event_name
        event.participants = {}

        self.eid = event.eid
        self.code = code
        self.location = location
        self.organiser_id = organiser_id
        self.event_name = event_name
        self.participants = {}

        session.add(event)
        session.commit()
        session.close()

    @classmethod
    def from_db(cls, eid):
        session = Session()
        event = session.query(Event).filter_by(eid=eid).first()
        self.eid = event.eid
        self.code = event.code
        self.location = event.location
        self.organiser_id = event.organiser_id
        self.event_name = event.event_name
        self.participants = event.participants
        session.close()

    #use this to update user avaliability too
    def add_user(self, uid, availability):
        session= Session()
        if session.query(Event).filter_by(eid = self.eid).first() == None:
            return False
        event = session.query(Event).filter_by(eid = self.eid).first()
        tdic = event.participants.copy()
        time.sleep(.05)
        tdic[uid] = availability
        time.sleep(.05)
        event.participants = tdic.copy()
        time.sleep(.05)
        session.commit()
        session.close()

