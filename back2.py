from flask import Flask, render_template, session, request, redirect, url_for, flash
import distance
import classes
import datetime
import config

app = config.app()


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


@app.route('/', methods=['POST', 'GET'])
def home():
    if request.method == 'GET':
        if 'user' in session:
            if 'uid' in session:
                uid = session["uid"]
                User = classes.FunctionUser.from_db(uid)
                all_requests = User.get_receiving_requests()
                all_eids = User.get_events()
                all_events = []
                all_names = {}
                for eid in all_eids:
                    Event = classes.FunctionEvents.from_db(eid)
                    all_events.append(Event)
                for current_request in all_requests:
                    if current_request.status == 'Default':
                        first_name = classes.FunctionUser.from_db(current_request.requesting_id).first_name
                        last_name = classes.FunctionUser.from_db(current_request.requesting_id).last_name
                        name = first_name + ' ' + last_name
                        all_names[current_request] = name
                    else:
                        all_requests.remove(current_request)
            else:
                session.pop("user", None)
                all_requests = []
                all_events = []
                all_names = {}
        else:
            all_requests = []
            all_events = []
            all_names = {}
        return render_template('home.html', requests=all_requests, events=all_events, names=all_names)


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'GET':
        if 'user' in session:
            return redirect(url_for('home'))
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
                    return redirect(url_for('home'))
                else:
                    flash("This username doesn't exist")
                    return render_template('login.html')
        else:
            return render_template('Login.html')


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
    if request.method == 'GET':
        user = classes.FunctionUser.from_db(session['uid'])
        return render_template('requests.html', events=user.get_events())
    else:
        pass


@app.route('/logout')
def logout():
    session.pop('user', None)
    session.pop('uid', None)
    return redirect(url_for('login'))


@app.route('/specificRequests/<rid>')
def specific_request(rid):
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


@app.route("/events", methods=['POST', 'GET'])
def events():
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
                event.add_user(uid)
                return redirect(url_for('event_created', eid=event.eid))
            elif form == 2:
                availability = ''
                event_code = request.form['text']
                event_id = classes.code_to_eid(event_code)
                status = request.form.get('checkbox', False)
                if status == 'On':
                    availability = 'Need'
                else:
                    availability = 'Give'
                event = classes.FunctionEvents.from_db(event_id)
                uid = session["uid"]
                event.add_user(uid, availability)
                return redirect(url_for('home'))
    else:
        return redirect(url_for('login'))


@app.route('/creation/<eid>', methods=['POST', 'GET'])
def event_created(eid):
    if request.method == 'GET':
        specific_event = classes.FunctionEvents.from_db(eid)
        if specific_event.organiser_id == session["uid"]:
            code = specific_event.code
            return render_template("eventcreated.html", event_code=code)
        else:
            return redirect(url_for('events'))


@app.route('/event/join/<event_code>')
def join(event_code):
    if 'user' in session:
        eid = classes.code_to_eid(event_code)
        event = classes.FunctionEvents.from_db(eid=eid)
        uid = session["uid"]
        event.add_user(uid)
        return redirect(url_for('event', eid=eid))


@app.route('/event/<eid>/', methods=['GET', 'POST'])
@app.route('/event/<eid>', methods=['GET', 'POST'])
def event(eid):
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
            user = classes.FunctionUser.from_db(int(uid))
            first_name = user.first_name
            last_name = user.last_name
            all_participants[uid] = (first_name + ' ' + last_name)
        if session['uid'] == event.organiser_id:
            owner = True
        else:
            owner = False
        return render_template('event.html', event_location=location, event_name=name, event_start=start, event_end=end, event_participants=all_participants, eid=int(eid), all_uids=uids, owner=owner)
    else:
        form = str(request.args.get('user'))
        event = classes.FunctionEvents.from_db(int(eid))
        uids = event.participants
        for uid in uids:
            user = classes.FunctionUser.from_db(int(uid))
            first_name = user.first_name
            last_name = user.last_name
            name = first_name + ' ' + last_name
            if name == form:
                event.remove_user(uid)


@app.route('/event/remove/<eid>/<uid>')
def remove(eid, uid):
    try:
        event = classes.FunctionEvents.from_db(eid)
        if session['uid'] == event.organiser_id:
            event.remove_user(uid)
            return redirect(url_for('event', eid=eid))
        else:
            return redirect(url_for('home'))
    except:
        return redirect(url_for('home'))


@app.route('/request/accept/<rid>')
def accept(rid):
    Request = classes.FunctionRequests.from_db(rid)
    Request.update_request('Accepted')
    return redirect(url_for('home'))


@app.route('/request/reject/<rid>')
def reject(rid):
    Request = classes.FunctionRequests.from_db(rid)
    Request.update_request('Declined')
    return redirect(url_for('home'))


@app.route('/about', methods=['GET'])
def about():
    return render_template('about.html')


@app.route('/send/{{uid}}', methods=['POST', 'GET'])
def send(uid):
    if request.method == 'GET':
        return render_template('send.html')


if __name__ == "__main__":
    app.run(debug=True)
