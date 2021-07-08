from flask import Flask, render_template, session, request, redirect, url_for, flash
import distance
import classes
import datetime
import config
import smtplib, ssl

app = config.app()


def send_email(uid):
    user = classes.FunctionUser.from_db(uid)
    receiver_email = user.email
    message = f"Your code is: {uid}"
    port = 465
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
        server.login("ecogo23@gmail.com", config.password_mail)
        server.sendmail("ecogo23@gmail.com", receiver_email, message)


def clear_direction():
    session.pop('direction', None)
    session.pop('query', None)


def make_payment(type):
    pass


def logged_in():
    if 'user' in session and 'uid' in session:
        return True
    else:
        return False


def get_requests(uid):
    users = {}
    user = classes.FunctionUser.from_db(uid)
    events = user.get_events()
    for event in events:
        for id, status in event.participants.items():
            if status == 'give':
                participant = classes.FunctionUser.from_db(id)
                name = participant.first_name + ' ' + participant.last_name
                users[id] = name
    return users


def convert_to(date):
    print(date)
    temp = date.find('-')
    year = int(date[:temp])
    date = date[temp:]
    date = date[1:]
    temp = date.find('-')
    month = int(date[0:temp])
    date = date[temp:]
    date = date[1:]
    temp = date.find('-')
    day = int(date[0:])
    date1 = datetime.datetime(year, month, day)
    return date1.date()


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.route('/', methods=['POST', 'GET'])
def home():
    session.pop('direction', None)
    if request.method == 'GET':
        if logged_in():
            account = True
            if classes.unique_check(session["user"]) is True:
                session.pop("user", None)
                session.pop("uid", None)
                requests = {}
                all_events = []
            else:
                User = classes.FunctionUser.from_db(session['uid'])
                all_requests = User.get_receiving_requests()
                requests = dict()
                all_eids = User.get_events()
                all_events = []
                all_distances = []
                temp = []
                temp.append(User.address)
                for eid in all_eids:
                    Event = classes.FunctionEvents.from_db(eid)
                    all_events.append(Event)
                for current_request in all_requests:
                    if current_request.status == 'default':
                        first_name = classes.FunctionUser.from_db(current_request.requesting_id).first_name
                        last_name = classes.FunctionUser.from_db(current_request.requesting_id).last_name
                        name = first_name + ' ' + last_name
                        requests[current_request] = name
                    else:
                        all_requests.remove(current_request)
                    user = classes.FunctionUser.from_db(current_request.requesting_id)
                    temp.append(user.address)
                # if len(all_requests) > 0:
                #     all_distances = distance.all_distances(User.address, temp)
                #     counter = 0
                #     for k in requests.keys():
                #         temp = requests[k]
                #         requests[k] = [temp, all_distances[counter]]
                #         counter += 1
        else:
            requests = {}
            all_events = []
            account = False
        return render_template('home.html', requests=requests, events=all_events, logged_in=account)


@app.route('/login', methods=['POST', 'GET'])
def login():
    try:
        query = session['query']
        direction = session['direction']
    except KeyError:
        query = None
        direction = "home"
    form = 0
    try:
        form = int(request.args.get('form'))
    except:
        pass
    if request.method == 'GET' or form == 0:
        if logged_in():
            flash("You're already logged in!")
            return redirect(url_for(direction))
        else:
            return render_template('login.html')
    else:
        if form == 1:
            user = request.form['username-281b']
            password = request.form['pass-281b']
            check = classes.credential_check(user, password)
            if check == 'no username':
                flash("This username doesn't exist")
                return render_template('login.html')
            elif check is False:
                flash("Username and password don't match")
                return render_template('login.html')
            else:
                session['user'] = request.form['username-281b']
                session['uid'] = int(classes.credential_check(user, password))
                if session['uid'] != -1:
                    if direction == 'specific_requests':
                        return redirect(url_for(direction, rid=query))
                    elif direction == 'join':
                        return redirect(url_for(direction, event_code=query))
                    elif direction == 'event':
                        return redirect(url_for(direction, eid=query))
                    elif direction == 'accept' or direction == 'reject':
                        return redirect(url_for(direction, rid=query))
                    elif direction == 'send':
                        return redirect(url_for(direction, uid=query))
                    else:
                        return redirect(url_for(direction))
                else:
                    flash("This username doesn't exist")
                    return render_template('login.html')
        else:
            username = request.form['text-5']
            password = request.form['password']
            if password == request.form['password2']:
                email = request.form['email']
                phone = request.form['phone-number']
                name = str(request.form['name'])
                names = name.split(' ')
                address = request.form['text-2'] + ' ' + request.form['secondary'] + ' ' + request.form[
                    'city'] + ' ' + request.form['text-1'] + ' ' + request.form['text-4']
                print(address)
                print(request.form['text-2'])
                print(request.form['secondary'])
                print(request.form['city'])
                print(request.form['text-1'])
                print(request.form['text-4'])
                if classes.unique_check(username) is False:
                    flash('Username already exists')
                    return render_template('login.html')
                else:
                    User = classes.FunctionUser.from_new(names[0], names[1], username, password, phone,
                                                         email, address)
                    session['user'] = username
                    session['uid'] = User.uid
                    return redirect(url_for('verify'))
            else:
                print('No match')
                flash("Passwords don't match!")
                return render_template('login.html')


@app.route('/requests', methods=['POST', 'GET'])
def requests():
    clear_direction()
    if logged_in():
        if request.method == 'GET':
            requests = dict()
            user = classes.FunctionUser.from_db(session['uid'])
            all_requests = user.get_receiving_requests()
            events = user.get_events()
            event_names = {}
            users = {}
            for eid in events:
                event = classes.FunctionEvents.from_db(eid)
                event_names[eid] = event.event_name
                for uid in event.participants.keys():
                    user2 = classes.FunctionUser.from_db(int(uid))
                    for request1 in user2.get_sent_requests():
                        if request1.receiving_id == session['uid']:
                            users[request1.rid] = user2.first_name + user2.last_name
                            break
                for current_request in all_requests:
                    if current_request.status == 'default':
                        first_name = classes.FunctionUser.from_db(current_request.requesting_id).first_name
                        last_name = classes.FunctionUser.from_db(current_request.requesting_id).last_name
                        name = first_name + ' ' + last_name
                        requests[current_request] = name
                    else:
                        all_requests.remove(current_request)
            return render_template('requests.html', events=event_names, users=users, pending=requests, logged_in=logged_in())
        else:
            pass
    else:
        flash("You aren't logged in!")
        session['direction'] = 'requests'
        return redirect(url_for('login'))


@app.route('/logout')
def logout():
    session.pop('user', None)
    session.pop('uid', None)
    return redirect(url_for('login'))


@app.route('/specificRequests/<rid>')
def specific_request(rid):
    clear_direction()
    if logged_in():
        if request.method == 'GET':
            Request = classes.FunctionRequests.from_db(rid)
            receiving_id = Request.receiving_id
            id2 = Request.requesting_id
            if int(receiving_id) == int(session['uid']):
                user = classes.FunctionUser.from_db(id2)
                name = user.first_name + ' ' + user.last_name
                event = classes.FunctionEvents.from_db(Request.event_id)
                date = str(event.start_time.date()) + ' - ' + str(event.end_time.date())
                event_name = event.event_name
                address = str(user.address)
                complete_address = address.split()
                return render_template('specificrequest.html', address_list=complete_address, user_name=name, event=event_name, date=date, address=address, rid=rid)
            else:
                return redirect(url_for('home'))
    else:
        flash("You aren't logged in!")
        session['direction'] = 'specific_request'
        return redirect(url_for('login'))


@app.route("/events", methods=['POST', 'GET'])
def events():
    clear_direction()
    if logged_in():
        if 'user' in session:
            if request.method == 'GET':
                user = classes.FunctionUser.from_db(session['uid'])
                events_created = []
                events_joined = []
                all_events = user.get_events()
                for event in all_events:
                    Event = classes.FunctionEvents.from_db(event)
                    if Event.organiser_id == user.uid:
                        events_created.append(Event)
                    else:
                        events_joined.append(Event)
                return render_template('events.html', created=events_created, joined=events_joined)
            else:
                form = int(request.args.get('form'))
                if form == 1:
                    location = request.form['text-1'] + ' ' + request.form['text-2'] + ' ' + request.form['city'] + ' ' + request.form['text-5'] + ' ' + request.form['text-4']
                    uid = session["uid"]
                    name = request.form['text']
                    temp1 = request.form['date']
                    start = convert_to(temp1)
                    temp2 = request.form['date-1']
                    end = convert_to(temp2)
                    if datetime.date.today() <= start <= end:
                        checkbox = request.form.get('recurring', False)
                        if checkbox == 'On':
                            repeating = True
                        else:
                            repeating = False
                        event = classes.FunctionEvents.from_new(location, uid, name, start, end, repeating)
                        event.add_user(uid, 'none')
                        return redirect(url_for('event_created', eid=event.eid))
                    else:
                        flash("Invalid Dates!")
                        user = classes.FunctionUser.from_db(session['uid'])
                        events_created = []
                        events_joined = []
                        all_events = user.get_events()
                        for event in all_events:
                            Event = classes.FunctionEvents.from_db(event)
                            if Event.organiser_id == user.uid:
                                events_created.append(Event)
                            else:
                                events_joined.append(Event)
                        return render_template('events.html', created=events_created, joined=events_joined)
                elif form == 2:
                    event_code = request.form['text']
                    event_id = classes.code_to_eid(event_code)
                    status = request.form.get('checkbox', False)
                    if status == 'On':
                        availability = 'need'
                    else:
                        availability = 'give'
                    event = classes.FunctionEvents.from_db(event_id)
                    uid = session["uid"]
                    event.add_user(uid, availability)
                    return redirect(url_for('home'))
        else:
            return redirect(url_for('login'))
    else:
        flash("You aren't logged in!")
        return redirect(url_for('login', direction='events'))


@app.route('/creation/<eid>', methods=['POST', 'GET'])
def event_created(eid):
    clear_direction()
    if request.method == 'GET':
        specific_event = classes.FunctionEvents.from_db(eid)
        if specific_event.organiser_id == session["uid"]:
            code = specific_event.code
            return render_template("event_created.html", event_code=code)
        else:
            return redirect(url_for('events'))


@app.route('/event/join/<event_code>', methods=['GET'])
def join(event_code):
    clear_direction()
    if logged_in():
        eid = classes.code_to_eid(event_code)
        event = classes.FunctionEvents.from_db(eid=eid)
        uid = session["uid"]
        event.add_user(uid)
        return redirect(url_for('event', eid=eid))
    else:
        session['query'] = event_code
        session['direction'] = 'join'
        return redirect(url_for('login'))


@app.route('/event/<eid>/', methods=['GET', 'POST'])
@app.route('/event/<eid>', methods=['GET', 'POST'])
def event(eid):
    clear_direction()
    if request.method == 'GET':
        event = classes.FunctionEvents.from_db(int(eid))
        location = event.location
        name = event.event_name
        start = str(event.start_time.date())
        end = str(event.end_time.date())
        uids = event.participants
        all_participants = {}
        for uid in uids:
            if int(uid) != session['uid']:
                user = classes.FunctionUser.from_db(int(uid))
                first_name = user.first_name
                last_name = user.last_name
                all_participants[uid] = (first_name + ' ' + last_name)
        if session['uid'] == event.organiser_id:
            owner = True
        else:
            owner = False
        oid = event.organiser_id
        organiser = classes.FunctionUser.from_db(oid)
        organiser_name = organiser.first_name + ' ' + organiser.last_name
        complete = str(event.location).split()
        return render_template('event.html', event_location=location, event_name=name, event_start=start, event_end=end, event_participants=all_participants, eid=int(eid), all_uids=uids, owner=owner, organiser=organiser_name, code=event.code, address_list=complete)
    else:
        if logged_in():
            event = classes.FunctionEvents.from_db(int(eid))
            if event.organiser_id == session['uid']:
                form = str(request.args.get('user'))
                uids = event.participants
                for uid in uids:
                    user = classes.FunctionUser.from_db(int(uid))
                    first_name = user.first_name
                    last_name = user.last_name
                    name = first_name + ' ' + last_name
                    if name == form:
                        event.remove_user(int(uid))
            else:
                return redirect(url_for('logout'))
        else:
            session['query'] = eid
            session['direction'] = 'event'
            return redirect(url_for('login', direction='event'))


@app.route('/event/remove/<eid>/<uid>')
def remove(eid, uid):
    clear_direction()
    if logged_in():
        event = classes.FunctionEvents.from_db(eid)
        if session['uid'] == event.organiser_id:
            event.remove_user(uid)
            return redirect(url_for('event', eid=eid))
        else:
            return redirect(url_for('logout'))
    else:
        session['query'] = eid
        session['direction'] = 'remove'
        return redirect(url_for('login'))


@app.route('/request/accept/<rid>')
def accept(rid):
    clear_direction()
    if logged_in():
        Request = classes.FunctionRequests.from_db(rid)
        if Request.receiving_id == str(session['uid']):
            Request.update_request('accepted')
        return redirect(url_for('home'))
    else:
        session['query'] = rid
        session['direction'] = 'accept'
        return redirect(url_for('login'))


@app.route('/request/reject/<rid>')
def reject(rid):
    clear_direction()
    if logged_in():
        Request = classes.FunctionRequests.from_db(rid)
        if Request.receiving_id == str(session['uid']):
            Request.update_request('rejected')
        return redirect(url_for('home'))
    else:
        session['query'] = rid
        session['direction'] = 'reject'
        return redirect(url_for('login'))


@app.route('/about', methods=['GET'])
def about():
    return render_template('about.html')


@app.route('/guide', methods=["GET"])
def guide():
    return render_template('guide.html')


@app.route('/send/<uid>', methods=['POST', 'GET'])
def send(uid):
    clear_direction()
    if logged_in():
        if request.method == 'GET':
            user = classes.FunctionUser.from_db(session['uid'])
            user2 = classes.FunctionUser.from_db(uid)
            events = list(set(user.get_events()) & set(user2.get_events()))
            event_names = {}
            for eid in events:
                event = classes.FunctionEvents.from_db(eid)
                event_names[eid] = event.event_name
            return render_template('send.html', events=event_names)
        else:
            if request.form['agree'] == 'on':
                classes.FunctionRequests.from_new(session['uid'], uid, request.form['select'])
                flash('Request Sent!')
                return redirect(url_for('home'))
    else:
        flash("You aren't logged in!")
        session['direction'] = 'send'
        session['query'] = uid
        return redirect(url_for('login'))


@app.route('/terms-service', methods=['GET'])
def terms():
    return render_template('terms.html')


@app.route('/privacy-policy')
def policy():
    return render_template('privacy.html')


@app.route('/profile/<uid>', methods=['POST', 'GET'])
@app.route('/profile', methods=['POST', 'GET'])
def profile(uid=-1):
    if int(uid) == -1:
        try:
            uid = session['uid']
        except:
            flash('You are not logged in!')
            return redirect(url_for('login'))
    if request.method == 'GET':
        private = False
        if logged_in():
            if int(session['uid']) == int(uid):
                private = True
        user = classes.FunctionUser.from_db(uid)
        name = user.first_name + ' ' + user.last_name
        return render_template("Profile.html", private=private, name=name, email=user.email, password=user.password,
                               address=user.address, username=user.username, phone=user.phone_number)
    else:
        user = classes.FunctionUser.from_db(session['uid'])
        try:
            user.first_name = str(request.form['name']).split(' ')[0]
            user.last_name = str(request.form['name']).split(' ')[1]
        except:
            pass
        try:
            user.email = str(request.form['email'])
        except:
            pass
        try:
            user.phone_number = str(request.form['phone'])
        except:
            pass
        try:
            user.username = str(request.form['username'])
        except:
            pass
        try:
            user.password = str(request.form['password'])
        except:
            pass
        try:
            user.address = str(request.form['address'])
        except:
            pass
        return redirect(url_for('home'))

# @app.route('/premium', methods=['POST', 'GET'])
# def store():
#     if request.method == 'GET':
#         return render_template('store.html')
#     else:
#         if logged_in():
#             pass
#         else:
#             return redirect(url_for('login', direction='store'))


@app.route('/verify', methods=['GET', 'POST'])
def verify():
    uid = session['uid']
    if request.method == 'GET':
        user = classes.FunctionUser.from_db(uid)
        return render_template('Verify.html', email=user.email)
    else:
        if request.form['code'] == uid:
            user = classes.FunctionUser.from_db(uid)
            user.verified_email = True
        return redirect(url_for('home'))



if __name__ == "__main__":
    app.run(debug=True)
