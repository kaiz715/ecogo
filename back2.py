from flask import Flask, render_template, session, request, redirect, url_for, flash
import distance
import classes
import datetime
import config

app = config.app()
query = None


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
    if request.method == 'GET':
        if logged_in():
            account = True
            if classes.unique_check(session["user"]) is True:
                session.pop("user", None)
                session.pop("uid", None)
                all_requests = []
                all_events = []
                all_names = {}
            else:
                User = classes.FunctionUser.from_db(session['uid'])
                all_requests = User.get_receiving_requests()
                all_eids = User.get_events()
                all_events = []
                all_names = {}
                for eid in all_eids:
                    Event = classes.FunctionEvents.from_db(eid)
                    all_events.append(Event)
                for current_request in all_requests:
                    if current_request.status == 'default':
                        first_name = classes.FunctionUser.from_db(current_request.requesting_id).first_name
                        last_name = classes.FunctionUser.from_db(current_request.requesting_id).last_name
                        name = first_name + ' ' + last_name
                        all_names[current_request] = name
                    else:
                        all_requests.remove(current_request)
        else:
            all_requests = []
            all_events = []
            all_names = {}
            account = False
        return render_template('home.html', requests=all_requests, events=all_events, names=all_names, logged_in=account)


@app.route('/login', methods=['POST', 'GET'])
@app.route('/login/<direction>', methods=['POST', 'GET'])
def login(direction='home'):
    global query
    if request.method == 'GET':
        if logged_in():
            flash("You're already logged in!")
            return redirect(url_for(direction))
        else:
            return render_template('login.html')
    else:
        if request.form['login-button'] == 'Login':
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
                session['uid'] = classes.credential_check(user, password)
                if int(session['uid']) != -1:
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
            return render_template('login.html')


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    else:
        if request.form['register-button'] == 'Register':
            username = request.form['text-5']
            password = request.form['password']
            if password == request.form['password2']:
                email = request.form['email']
                phone = request.form['number-1358']
                name = str(request.form['name'])
                names = name.split(' ')
                address = request.form['text-2'] + ' ' + request.form['secondary'] + ' ' + request.form['city'] + ' ' + request.form['text-1'] + ' ' +request.form['text-4']
                if classes.unique_check(username) is False:
                    flash('Username already exists')
                    return render_template('register.html')
                else:
                    User = classes.FunctionUser.from_new(names[0], names[1], username, password, phone, email, address)
                    session['user'] = username
                    session['uid'] = User.uid
                    return redirect(url_for('home'))
            else:
                flash("Passwords don't match")
                return render_template('register.html')
        else:
            return render_template('register.html')


@app.route('/requests', methods=['POST', 'GET'])
def requests():
    if logged_in():
        if request.method == 'GET':
            user = classes.FunctionUser.from_db(session['uid'])
            events = user.get_events()
            event_names = []
            for eid in events:
                event = classes.FunctionEvents.from_db(eid)
                event_names.append(event.event_name)
            return render_template('requests.html', events=event_names)
        else:
            pass
    else:
        flash("You aren't logged in!")
        return redirect(url_for('login'))


@app.route('/logout')
def logout():
    session.pop('user', None)
    session.pop('uid', None)
    return redirect(url_for('login'))


@app.route('/specificRequests/<rid>')
def specific_request(rid):
    global query
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
        query = rid
        return redirect(url_for('login', direction='specific_request'))


@app.route("/events", methods=['POST', 'GET'])
def events():
    if logged_in():
        if 'user' in session:
            if request.method == 'GET':
                return render_template('events.html')
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
                    checkbox = request.form.get('recurring', False)
                    if checkbox == 'On':
                        repeating = True
                    else:
                        repeating = False
                    event = classes.FunctionEvents.from_new(location, uid, name, start, end, repeating)
                    event.add_user(uid, 'none')
                    return redirect(url_for('event_created', eid=event.eid))
                elif form == 2:
                    availability = ''
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
    if request.method == 'GET':
        specific_event = classes.FunctionEvents.from_db(eid)
        if specific_event.organiser_id == session["uid"]:
            code = specific_event.code
            return render_template("event_created.html", event_code=code)
        else:
            return redirect(url_for('events'))


@app.route('/event/join/<event_code>', methods=['GET'])
def join(event_code):
    global query
    if logged_in():
        eid = classes.code_to_eid(event_code)
        event = classes.FunctionEvents.from_db(eid=eid)
        uid = session["uid"]
        event.add_user(uid)
        return redirect(url_for('event', eid=eid))
    else:
        query = event_code
        return redirect(url_for('login', direction='join'))


@app.route('/event/<eid>/', methods=['GET', 'POST'])
@app.route('/event/<eid>', methods=['GET', 'POST'])
def event(eid):
    global query
    if request.method == 'GET':
        username = session['user']
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
            if int(event.organiser_id) == int(session['uid']):
                form = str(request.args.get('user'))
                uids = event.participants
                for uid in uids:
                    user = classes.FunctionUser.from_db(int(uid))
                    first_name = user.first_name
                    last_name = user.last_name
                    name = first_name + ' ' + last_name
                    if name == form:
                        event.remove_user(uid)
            else:
                return redirect(url_for('logout'))
        else:
            query = eid
            return redirect(url_for('login', direction='event'))


@app.route('/event/remove/<eid>/<uid>')
def remove(eid, uid):
    global query
    if logged_in():
        try:
            event = classes.FunctionEvents.from_db(eid)
            if session['uid'] == event.organiser_id:
                event.remove_user(uid)
                return redirect(url_for('event', eid=eid))
            else:
                return redirect(url_for('logout'))
        except:
            return redirect(url_for('home'))
    else:
        query = eid
        return redirect(url_for('login', direction='event'))


@app.route('/request/accept/<rid>')
def accept(rid):
    global query
    if logged_in():
        Request = classes.FunctionRequests.from_db(rid)
        if Request.receiving_id == str(session['uid']):
            Request.update_request('accepted')
        return redirect(url_for('home'))
    else:
        query = rid
        return redirect(url_for('login', direction='accept'))


@app.route('/request/reject/<rid>')
def reject(rid):
    global query
    if logged_in():
        Request = classes.FunctionRequests.from_db(rid)
        if Request.receiving_id == str(session['uid']):
            Request.update_request('rejected')
            return redirect(url_for('home'))
    else:
        query = rid
        return redirect(url_for('login', direction='reject'))


@app.route('/about', methods=['GET'])
def about():
    return render_template('about.html')
@app.route('/guide', methods=["GET"])
def guide():
    return render_template('guide.html')


@app.route('/send/<uid>', methods=['POST', 'GET'])
def send(uid):
    global query
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
                Request = classes.FunctionRequests.from_new(session['uid'], uid, request.form['select'])
                flash('Request Sent!')
                return redirect(url_for('home'))
    else:
        flash("You aren't logged in!")
        query = uid
        return redirect(url_for('login', direction='send'))


@app.route('/premium', methods=['POST', 'GET'])
def store():
    if request.method == 'GET':
        pass
    else:
        if logged_in():
            pass
        else:
            return redirect(url_for('login', direction='store'))


if __name__ == "__main__":
    app.run(debug=True)
