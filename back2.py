from flask import Flask, render_template, session, request, redirect, url_for, flash
import dbstuff
import distance
import classes
from datetime import timedelta
app = Flask('__name__')
app.secret_key = 'app'
app.permanent_session_lifetime = timedelta(seconds=1)
all_events = []


@app.route('/', methods=['POST', 'GET'])
def home():
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
            check = dbstuff.credential_check(user, password)
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
            username = request.form['Username']
            password = request.form['Password']
            email = request.form['email']
            phone = request.form['phone']
            first_name = request.form['first']
            last_name = request.form['last']
            address = request.form['address'] + request.form['zip code'] + request.form['state']
            if dbstuff.username_exists(username):
                flash('Username already exists')
                return render_template('Register.html')
            else:
                User = classes.FunctionUser.from_new(first_name, last_name, username, password, phone, email, address)
                session['user'] = username
                return redirect(url_for('home'))


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'GET':
        return render_template('Register.html')
    else:
        username = request.form['text-5']
        password = request.form['password']
        email = request.form['email']
        phone = request.form['number-1358']
        first_name = request.form['name']
        last_name = request.form['text']
        address = request.form['text-2'] + request.form['text-4'] + request.form['text-1']
        User = classes.FunctionUser.from_new(first_name, last_name, username, password, phone, email, address)
        session['user'] = username
        return redirect(url_for('home'))
# @app.route("/events", methods=['POST', 'GET'])
# def events():
#     if request.method == 'GET':
#         return render_template('events.html')
#     else:
#         if request.form['Create'] == "Create":
#             #location =
#             #uid =
#             #name =
#             #start =
#             #end =
#             #repeating =
#             event = classes.FunctionEvents.from_new()
#             all_events.append(event)
#             return render_template("eventCreated.html")
#         elif request.form["Join"] == "Join":
#             name = request.form["Event Name"]
#             event_id = dbstuff.event_name_to_eid(name)
#             event = classes.FunctionEvents.from_db(event_id)
#             username = session["user"]
#             uid = dbstuff.username_to_uid(username)
#             if request.form['status']:
#                 status = 'need'
#             else:
#                 status = ''
#             event.add_user(uid, status)
#             return redirect(url_for('home'))


# @app.route('/event/<name>', methods=['POST', 'GET'])
# def event_created(name):
#     for event in all_events:
#         if event.event_name == name:
#             event_location = event.location
#             event_code = event.code
#             event_start = event.start_date
#             event_end = event.end_date
#     return render_template("event.html", event_name=)


if __name__ == "__main__":
    app.run(debug=True)
