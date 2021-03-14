from flask import Flask, render_template, session, request, redirect, url_for, flash
import dbstuff
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
            session["user"] = user
            return redirect(url_for('index'))
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
        password = request.form['password']
        zip = request.form['zipcode']
        add1 = request.form['Address']
        add2 = request.form['secondary']
        city = request.form['city']
        state = request.form['state']
        address = zip + add1 + ',' + add2 + ',' + city + state
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
    for i, j in requests.items():
        nrequests[dbstuff.uid_to_username(i)] = dbstuff.eid_to_event_name(j)

    if request.method == 'POST':
        for i in nrequests:
            if request.form[i] == "Accept":
                dbstuff.update_request(dbstuff.username_to_uid(i), 'yes')
            else:
                dbstuff.update_request(dbstuff.username_to_uid(i), 'no')
        requests_dic = dbstuff.get_requests(uid)
            
        return render_template('requests.html', nrequests=nrequests)
    else:
        return render_template('requests.html', nrequests=nrequests)


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
        address = zip + add1 + ',' + add2 + ',' + city + state
        username = session['user']
        id = dbstuff.username_to_uid(username)
        event_name = request.form['name']
        code = dbstuff.create_event(address, id, event_name)
        return render_template('eventCreated.html', code=code)
    else:
        return render_template('create.html')


if __name__ == "__main__":
    app.run(debug=True)
