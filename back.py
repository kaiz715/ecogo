from flask import Flask, render_template, session, request, redirect, url_for, flash
import dbstuff
import distance
from datetime import timedelta
app = Flask('__name__')
app.secret_key = 'app'
app.permanent_session_lifetime = timedelta(days=1)
requests_dic = dict()


@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        if request.form["button"] == 'Requests':
            return redirect(url_for('requests'))
        elif request.form["button"] == 'Join Event':
            return redirect(url_for('join'))
        else:
            return redirect(url_for('create'))
    else:
        if "user" in session:
            return render_template('home.html')
        else:
            return redirect(url_for('login'))


@app.route("/login", methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        if request.form['submit_button'] == 'Create Account':
            return redirect(url_for('signup'))
        else:
            session.permanent = True
            user = request.form['username']
            password = request.form['password']
            if dbstuff.credential_check(user, password) is True:
                session["user"] = user
                return redirect(url_for('index'))
            else:
                flash("Credentials don't match, try again or make an account!")
                return render_template('login.html')
    else:
        if "user" in session:
            return redirect(url_for('index'))
        else:
            return render_template('login.html')


@app.route("/signup", methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        first = request.form['first_name']
        last = request.form['last_name']
        username = request.form['username']
        if dbstuff.username_exists(username) is True:
            flash('Username already exists! Please select another one!')
            return render_template('signup.html')
        else:
            password = request.form['password']
            zip = request.form['zipcode']
            add1 = request.form['Address']
            add2 = request.form['secondary']
            city = request.form['city']
            state = request.form['state']
            address = zip + ' ' + add1 + ' , ' + add2 + ' , ' + city + ' ' + state
            phone_num = request.form['phone_number']
            email = request.form['email']
            dbstuff.create_user(first, last, username, password, address, phone_num, email)
            return redirect(url_for('index'))
    else:
        return render_template('signup.html')


@app.route("/logout")
def logout():
    if "user" in session:
        session.pop("user", None)
    return redirect(url_for('login'))


@app.route('/requests', methods=['POST', 'GET'])
def requests():
    uid = dbstuff.username_to_uid(session['user'])
    requests = dbstuff.get_requests(uid)
    nrequests = dict()
    email = dict()
    numbers = dict()
    distances = dict()
    user_data = dbstuff.uid_to_stuff(uid)
    user_address = user_data[2]
    address = dict()
    for i, j in requests.items():
        nrequests[dbstuff.uid_to_username(i)] = dbstuff.eid_to_event_name(j)
    for i, j in nrequests.items():
        data = dbstuff.uid_to_stuff(dbstuff.username_to_uid(i))
        email[i] = data[0]
        numbers[i] = data[1]
        address = data[2]
        distances[i] = distance.distance(user_address, address)
    if request.method == 'POST':
        for i, j in nrequests.items():
            if request.form[i] == "Accept":
                dbstuff.update_request(dbstuff.usernames_to_rid(uid, dbstuff.username_to_uid(i)), 'yes')
            else:
                dbstuff.update_request(dbstuff.usernames_to_rid(uid, dbstuff.username_to_uid(i)), 'no')
        requests_dic = dbstuff.get_requests(uid)
        return render_template('requests2.html', nrequests=nrequests, nemails=email, nphones=numbers, ndistances=distances)
    else:
        return render_template('requests2.html', nrequests=nrequests, nemails=email, nphones=numbers, ndistances=distances)


@app.route('/send', methods=['POST', 'GET'])
def make_request():
    username = session['user']
    uid = dbstuff.username_to_uid(username)
    events = dbstuff.uid_to_events(uid)
    events_users = {}
    track = {}
    fin = {}
    for i in events:
        events_users[i] = (dbstuff.list_of_people(i))
    for i, j in events_users.items():
        for k in j:
            if k != uid:
                track[i] = k
    for i, j in track.items():
        fin[dbstuff.eid_to_event_name(i)] = dbstuff.uid_to_username(j)
    if request.method == 'POST':
        for i, j in fin.items():
            try:
                if request.form[str(i) + str(j)] == 'Send Request':
                    senduid = dbstuff.username_to_uid(j)
                    event_id = dbstuff.event_name_to_eid(i)
                    dbstuff.create_request(uid, senduid, event_id)
            except:
                pass

    return render_template('create.html', fin = fin)


@app.route('/join', methods=['POST', 'GET'])
def join():
    status = ''
    if request.method == 'POST':
        if request.form['option1'] == 'Needs Ride':
            status = 'need'
        else:
            status = 'give'
        code = request.form['code']
        print(code)
        if code  == '':
            flash("Please enter a code!")
            return render_template('join.html')
        else:
            eid = dbstuff.code_to_eid(code)
            username = session['user']
            id = dbstuff.username_to_uid(username)
            dbstuff.add_user_to_event(id, eid, status)
            return redirect(url_for('index'))
    else:
        return render_template('join.html')


@app.route('/create', methods=['POST', 'GET'])
def create():
    if request.method == 'POST':
        zip = request.form['zipcode']
        add1 = request.form['Address']
        add2 = request.form['secondary']
        city = request.form['city']
        state = request.form['state']
        address = zip + ' ' + add1 + ' , ' + add2 + ' , ' + city + ' ' + state
        if 'user' in session:
            username = session['user']
            id = dbstuff.username_to_uid(username)
            event_name = request.form['name']
            code = dbstuff.create_event(address, id, event_name)
            return render_template('eventCreated.html', code=code)
        else:
            flash('You need to login!')
            return redirect(url_for('login'))
    else:
        return render_template('event.html')


if __name__ == "__main__":
    app.run(debug=True)
