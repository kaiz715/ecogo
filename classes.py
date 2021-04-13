from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Boolean, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from db import User, Event, Request, Session
from datetime import datetime
from distance import all_distances
import random, time

def code_to_eid(code):  # returns false if code doesnt exist
    session = Session()
    if session.query(Event).filter_by(code=code).first() == None:
        session.close()
        return False
    event = session.query(Event).filter_by(code=code).first()
    eid = event.eid
    session.close()
    return eid

def next_id(db):
    session = Session()
    if db == "user":
        first = session.query(func.max(User.uid)).first()[0]
    elif db == "request":
        first = session.query(func.max(Request.rid)).first()[0]
    elif db == "event":
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
    def __init__(
        self,
        uid,
        first_name,
        last_name,
        username,
        password,
        phone_number,
        email,
        address,
    ):
        self.uid = uid
        self.username = username
        self.password = password
        self.first_name = first_name
        self.last_name = last_name
        self.phone_number = phone_number
        self.email = email
        self.address = address

    @classmethod
    def from_new(  # for creating a new user
        # IMPORTANT: check if unique username first by using unique_check()
        cls,
        first_name,
        last_name,
        username,
        password,
        phone_number,
        email,
        address,
    ):
        session = Session()
        user = User()

        uid = next_id("user")
        user.uid = uid
        user.username = username
        user.password = password
        user.first_name = first_name
        user.last_name = last_name
        user.phone_number = phone_number
        user.email = email
        user.address = address
        session.add(user)
        session.commit()
        session.close()

        return cls(
            uid, first_name, last_name, username, password, phone_number, email, address
        )

    @classmethod
    def from_db(cls, uid):  # for already existing user
        session = Session()
        user = session.query(User).filter_by(uid=uid).first()
        username = user.username
        password = user.password
        first_name = user.first_name
        last_name = user.last_name
        phone_number = user.phone_number
        email = user.email
        address = user.address
        session.close()
        return cls(
            uid, first_name, last_name, username, password, phone_number, email, address
        )

    def join_event(self, eid, availability="default"):
        session = Session()
        event = FunctionEvents.from_db(eid)
        event.add_user(self.uid, availability)
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
        request = FunctionRequests.from_new(self.uid, receiving_id, event_id)
        return request.rid

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
        request = session.query(Request).filter_by(rid=rid).first()
        request.status = new_status
        session.add(request)
        session.commit()
        session.close()


class FunctionRequests:
    def __init__(self, rid, requesting_id, receiving_id, event_id, status):

        self.rid = rid
        self.requesting_id = requesting_id
        self.receiving_id = receiving_id
        self.event_id = event_id
        self.status = status

    @classmethod
    def from_new(
        cls, requesting_id, receiving_id, event_id
    ):  # you can use this or the one in the functionuser class
        session = Session()
        request = Request()

        rid = next_id("request")
        request.rid = rid
        request.requesting_id = requesting_id
        request.receiving_id = receiving_id
        request.event_id = event_id
        request.status = "default"

        session.add(request)
        session.commit()
        session.close()
        return cls(rid, requesting_id, receiving_id, event_id, "default")

    @classmethod
    def from_db(cls, rid):
        session = Session()
        request = session.query(Request).filter_by(rid=rid).first()
        requesting_id = request.requesting_id
        receiving_id = request.receiving_id
        event_id = request.event_id
        status = request.status
        session.close()
        return cls(rid, requesting_id, receiving_id, event_id, status)

    def update_request(self, new_status):
        session = Session()
        request = session.query(Request).filter_by(rid=self.rid).first()
        request.status = new_status
        session.add(request)
        session.commit()
        session.close()


class FunctionEvents:
    def __init__(
        self,
        eid,
        location,
        organiser_id,
        event_name,
        code,
        start_time,
        end_time,
        repeat,
        participants,
    ):

        self.eid = eid
        self.code = code
        self.location = location
        self.organiser_id = organiser_id
        self.event_name = event_name
        self.participants = participants
        self.start_time = start_time
        self.end_time = end_time
        self.repeat = repeat

    @classmethod
    def from_new(cls, location, organiser_id, event_name, start_time, end_time, repeat):
        session = Session()

        code = random.randint(0, 1000000)
        while session.query(Event.code).filter_by(code=code).first() != None:
            code = random.randint(0, 1000000)

        event = Event()
        eid = next_id("event")
        event.eid = eid
        event.code = code
        event.location = location
        event.organiser_id = organiser_id
        event.event_name = event_name
        event.participants = {}
        event.start_time = start_time
        event.end_time = end_time
        event.repeat = repeat

        session.add(event)
        session.commit()
        session.close()
        return cls(
            eid,
            location,
            organiser_id,
            event_name,
            code,
            start_time,
            end_time,
            repeat,
            {},
        )

    @classmethod
    def from_db(cls, eid):
        session = Session()
        event = session.query(Event).filter_by(eid=eid).first()
        code = event.code
        location = event.location
        organiser_id = event.organiser_id
        event_name = event.event_name
        participants = event.participants
        start_time = event.start_time
        end_time = event.end_time
        repeat = event.repeat

        session.close()
        return cls(
            eid,
            location,
            organiser_id,
            event_name,
            code,
            start_time,
            end_time,
            repeat,
            participants,
        )

    # use this to update user availability too
    def add_user(self, uid, availability):
        session = Session()
        if session.query(Event).filter_by(eid=self.eid).first() == None:
            return False
        event = session.query(Event).filter_by(eid=self.eid).first()
        tdic = event.participants.copy()
        time.sleep(0.05)
        tdic[uid] = availability
        time.sleep(0.05)
        event.participants = tdic.copy()
        time.sleep(0.05)
        session.commit()
        session.close()

    def find_distances(self, uid):
        session = Session()
        all_addresses = []
        for i in self.participants.keys():
            all_addresses.append(session.query(User).filter_by(uid=i).first().address)
        driver_address = session.query(User).filter_by(uid=uid).first().address
        distances = all_distances(driver_address, all_addresses)
        return distances


# # tester code:
# first_name, last_name, username, password, phone_number, email, address = (
#     "jonny",
#     "peterson",
#     "uusername",
#     "ppassword",
#     "2153234234",
#     "randemail@email.email",
#     "24958 Hazelmere Road, Beachwood, OH",
# )
# exuser = FunctionUser.from_new(
#     first_name, last_name, username, password, phone_number, email, address
# )
# print(
#     exuser.uid,
#     exuser.first_name,
#     exuser.last_name,
#     exuser.username,
#     exuser.password,
#     exuser.phone_number,
#     exuser.email,
#     exuser.address,
# )

# first_name, last_name, username, password, phone_number, email, address = (
#     "j",
#     "p",
#     "uuser",
#     "ppassw",
#     "215323",
#     "randemail@email.email",
#     "24250 Woodside Ln, Beachwood, OH 44122",
# )
# exuser2 = FunctionUser.from_new(
#     first_name, last_name, username, password, phone_number, email, address
# )
# start = datetime(2021, 4, 10)
# end = datetime(2021, 4, 11)
# exevent = FunctionEvents.from_new("24275 Woodside Ln, Beachwood, OH 44122", 0, "pool party", start, end, True)
# print(exevent.eid, exevent.location, exevent.organiser_id, exevent.event_name, exevent.start_time, exevent.end_time)
# time.sleep(0.5)
# exuser.join_event(0)
# exuser2.join_event(0)
# exuser.make_request(1, 0)
# print(exuser.get_events())
# print(exuser.get_sent_requests())
# print(exuser.get_receiving_requests())
# exuser.update_request(0, "yes")

# a = FunctionEvents.from_db(0)
# print(a.find_distances(0))