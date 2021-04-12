from flask import Flask, render_template, session, request, redirect, url_for, flash
import dbstuff
import distance
import classes
import datetime
app = Flask('__name__')
app.secret_key = 'app'
app.permanent_session_lifetime = datetime.timedelta(days=1)
all_events = []


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


def separate_address(address):
    num1 = address.find(' ')
    num = address[:num1]
    address = address[num1:]
    temp2 = address.find(' ')
    add1 = address[:temp2]
    address = address[temp2:]
    temp3 = address.find(' ')
    add2 = address[:temp3]
    address = address[temp3:]
    temp4 = address.find(' ')
    add3 = address[:temp4]
    address = address[temp4:]
    temp5 = address.find(' ')
    add4 = address[:temp5]
    seperated = [num, add1, add2, add3, add4]
    return seperated


@app.route('/', methods=['POST', 'GET'])
def home():
    if request.method == 'GET':
        return render_template('Home.html')


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'GET':
        if 'user' in session:
            return redirect(url_for('home'))
        else:
            return render_template('Login.html')
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
                return redirect(url_for('home'))
        else:
            return render_template('Login.html')


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'GET':
        return render_template('Register.html')
    else:
        if request.form['register-button'] == 'register':
            username = request.form['text-5']
            password = request.form['password']
            email = request.form['email']
            phone = request.form['number-1358']
            name = str(request.form['name'])
            names = name.split(' ')
            address = request.form['text-2'] + ' ' + request.form['secondary'] + ' ' + request.form['city'] + ' ' + request.form['text-1'] + ' ' +request.form['text-4']
            if dbstuff.username_exists(username):
                flash('Username already exists')
                return render_template('Register.html')
            else:
                User = classes.FunctionUser.from_new(names[0], names[1], username, password, phone, email, address)
                session['user'] = username
                return redirect(url_for('home'))
        else:
            return render_template('Register.html')


@app.route('/requests', methods=['POST', 'GET'])
def requests():
    if request.method == 'GET':
        return render_template('Requests.html')
    else:
        pass


@app.route('/customRequests/<rid>')
def specific_request(rid):
    if request.method == 'GET':
        Request = classes.FunctionRequests.from_db(rid)
        id = Request.receiving_id()
        User = classes.FunctionUser.from_db(id)
        address = str(User.address)
        complete = separate_address(address)
        return render_template('SpecificRequests.html', address_list=complete)


@app.route("/events", methods=['POST', 'GET'])
def events():
    if request.method == 'GET':
        return render_template('events.html')
    else:
        form = int(request.args.get('form'))
        if form == 1:
            location = request.form['text-1'] + ' ' + request.form['text-2'] + ' ' + request.form['city'] + ' ' + request.form['text-5'] + ' ' + request.form['text-4']
            uid = dbstuff.username_to_uid(session['user'])
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
            return redirect(url_for('event_created', eid=event.eid))
            #return redirect('/eventCreated/' + str(event.eid))
        elif form == 2:
            availability = ''
            event_id = request.form['text']
            status = request.form['checkbox']
            if status:
                availability = 'Need'
            else:
                availability = 'Give'
            event = classes.FunctionEvents.from_db(event_id)
            username = session["user"]
            uid = dbstuff.username_to_uid(username)
            event.add_user(uid, availability)
            return redirect(url_for('home'))


@app.route('/eventCreated/<eid>', methods=['GET'])
def event_created(eid):
    print('a')
    specific_event = classes.FunctionEvents.from_db(eid)
    print('b')
    code = specific_event.code
    print('c')
    return render_template("EventCreated.html", event_code=code)


@app.route('/event/<eid>', methods=['GET', 'POST'])
def event(eid):
    username = session['user']
    event = classes.FunctionEvents.from_db(eid)
    if event.organiser_id == (dbstuff.username_to_uid(username)):
        location = event.location
        name = event.event_name
        start = event.start_time
        end = event.end_time
        users = event
        return render_template('Event.html')
    else:
        return redirect(url_for(events))


if __name__ == "__main__":
    app.run(debug=True)
