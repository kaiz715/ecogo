from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Boolean, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from db import User, Event, Request, Session
import random, time


def create_user(first_name, last_name, username, password, address, phone_number, email):
    session = Session()
    if (session.query(User.username).filter_by(username = username).first()) == None:
        user = User()
        if session.query(func.max(User.uid)).first()[0] != None:
            user.uid = session.query(func.max(User.uid)).first()[0]+1
        else: 
            user.uid = 1
        user.username = username
        user.password = password
        user.first_name = first_name
        user.last_name = last_name
        user.phone_number = phone_number
        user.email = email
        user.address = address
        user.in_event = False
        session.add(user)
        session.commit()
        session.close()
        return True
    return False
    

def create_event(location, organiser_id, event_name): #returns the code
    session = Session()
    event = Event()
    if session.query(func.max(Event.eid)).first()[0] != None:
        event.eid = session.query(func.max(Event.eid)).first()[0]+1
    else: 
        event_id = 1
    code = random.randint(0,1000000)
    while session.query(Event.code).filter_by(code = code).first() != None:
        code = random.randint(0,1000000)
    event.code = code
    event.location = location
    event.organiser_id = organiser_id
    event.event_name = event_name
    event.participants = {}
    session.add(event)
    session.commit()
    session.close()
    return code


def create_request(requesting_id, receiving_id, event_id):
    session = Session()
    request = Request()
    if session.query(func.max(Request.rid)).first()[0] != None:
        request.rid = session.query(func.max(Request.rid)).first()[0]+1
    else:
        request.rid = 1
    request.requesting_id = requesting_id
    request.receiving_id = receiving_id
    request.event_id = event_id
    request.status = 'default'
    session.add(request)
    session.commit()
    session.close()

def check_status(rid):
    session = Session()
    request = session.query(Request).filter_by(rid = rid).first()
    return request.status

def update_request(rid, new_status): #new_status can be default, yes, no
    session = Session()
    request = session.query(Request).filter_by(rid = rid).first()
    print(rid)
    print(request)
    request.status = new_status
    session.add(request)
    session.commit()
    session.close()


def get_requests(receiving_id): #returns none if no requests
    pairs = dict()
    session = Session()
    requests = session.query(Request).filter_by(receiving_id=receiving_id).all()
    for i in requests:
        pairs[i.requesting_id] = i.event_id
    session.close()
    return pairs

def get_requestss(receiving_id): #returns none if no requests
    pairs = dict()
    session = Session()
    requests = session.query(Request).filter_by(receiving_id=receiving_id).all()
    for i in requests:
        if i.status =='default':
            pairs[i.requesting_id] = i.event_id
    session.close()
    return pairs

def add_user_to_event(uid, eid, availability): #avalibility can be need, give, filled
    #returns false if event doesnt exist
    session= Session()
    if session.query(Event).filter_by(eid = eid).first() == None:
        return False
    event = session.query(Event).filter_by(eid = eid).first()
    tdic = event.participants.copy()
    time.sleep(.05)
    tdic[uid] = availability
    time.sleep(.05)
    event.participants = tdic.copy()
    time.sleep(.05)
    session.commit()
    session.close()

def username_to_uid(username): #returns false if username doesnt exist
    session = Session()
    if session.query(User).filter_by(username = username).first() == None:
        session.close()
        return False
    user = session.query(User).filter_by(username = username).first()
    uid = user.uid
    session.close()
    return uid

def uid_to_username(uid): #returns false if username doesnt exist
    session = Session()
    if session.query(User).filter_by(uid = uid).first() == None:
        session.close()
        return False
    user = session.query(User).filter_by(uid = uid).first()
    username = user.username
    session.close()
    return username

def uid_to_name(uid): #returns false if username doesnt exist
    session = Session()
    if session.query(User).filter_by(uid = uid).first() == None:
        session.close()
        return False
    user = session.query(User).filter_by(uid = uid).first()
    name = user.first_name + ' ' + user.last_name
    session.close()
    return name

def credential_check(username, password): #returns 'no username' if username doesnt exist
    session = Session()
    if session.query(User).filter_by(username = username).first() == None:
        session.close()
        return 'no username'
    if password == session.query(User).filter_by(username = username).first().password:
        session.close()
        return True
    session.close()
    return False

def event_name_to_eid(event_name):#returns false if event_name doesnt exist
    session = Session()
    if session.query(Event).filter_by(event_name = event_name).first() == None:
        session.close()
        return False
    event = session.query(Event).filter_by(event_name = event_name).first()
    eid = event.eid
    session.close()
    return eid

def eid_to_event_name(eid):#returns false if event_name doesnt exist
    session = Session()
    if session.query(Event).filter_by(eid = eid).first() == None:
        session.close()
        return False
    event = session.query(Event).filter_by(eid = eid).first()
    name = event.event_name
    session.close()
    return name

def uid_to_stuff(uid):#returns false if event_name doesnt exist
    session = Session()
    if session.query(User).filter_by(uid = uid).first() == None:
        session.close()
        return False
    user = session.query(User).filter_by(uid = uid).first()
    ret = list()
    ret.append(user.email)
    ret.append(user.phone_number)
    ret.append(user.address)
    session.close()
    return ret #email, list, address
    
def code_to_eid(code):#returns false if code doesnt exist
    session = Session()
    if session.query(Event).filter_by(code = code).first() == None:
        session.close()
        return False
    event = session.query(Event).filter_by(code = code).first()
    eid = event.eid
    session.close()
    return eid

def username_exists(username): #returns false if username doesnt exist
    session = Session()
    if session.query(User).filter_by(username = username).first() == None:
        session.close()
        return False
    session.close()
    return True

def uid_to_events(uid):
    ret = []
    session = Session()
    events = session.query(Event).all()
    for i in events:
        try:
            if i.participants[str(uid)] != None:
                ret.append(i.eid)
        except:
            pass
    return ret

def usernames_to_rid(receiving_id, requesting_id):
    session = Session()
    a = session.query(Request).filter_by(requesting_id = requesting_id).all()
    print(requesting_id)
    print(receiving_id)
    for i in a:
        if int(i.receiving_id) == receiving_id:
            rid = i.rid
            session.close()
            return rid
    session.close()
    return "none thring"

def list_of_people(eid):
    session = Session()
    if session.query(Event).filter_by(eid = eid).first() == None:
        session.close()
        return False
    event = session.query(Event).filter_by(eid = eid).first()
    participants = event.participants
    uids = list()
    for i in list(participants.keys()):
        uids.append(int(i))
    # names = list()
    # for j in uids:
    #     names.append(uid_to_name(j))
    # session.close()
    return uids

#add_user_to_event(1233245333,1,'need')
# print(username_to_uid('hello this is meaa'))
# print(event_name_to_eid('name'))
# create_user("kai", "last","hellouser", "password sample", "address sample", "phone", 'email')
# create_event("asdhfasdf", 1, 'name')
# create_request(1, 2, 1)
