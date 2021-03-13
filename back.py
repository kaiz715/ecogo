from flask import Flask, render_template, session, request, redirect, url_for
import flask_sqlalchemy
import dbstuff
from datetime import timedelta
app = Flask('__name__')
app.secret_key = 'app'
app.permanent_session_lifetime = timedelta(seconds=1)
requests_dic = {
    'kaiz': 'HighSchool',
    'evelynz': 'Party'
            }


@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        if request.form["button"] == 'Requests':
            return redirect(url_for('requests'))
        elif request.form["button"] == 'Join Event':
            print('join')

        else:
            print('create')
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
    keys = []
    if request.method == 'POST':
        for i in requests_dic:
            keys.append(i)
        for key in keys:
            try:
                if request.form[key] == 'Accept':
                    print(f'Accepted {key}')
                else:
                    print(f'Declined {key}')
            except:
                print('Error')
        return render_template('requests.html', request=requests_dic)
    else:
        return render_template('requests.html', requests=requests_dic)


@app.route('/join', methods=['POST', 'GET'])
def join():
    if request.method == 'POST':
        code = request.form['code']
        return redirect(url_for('index'))
    else:
        return render_template('join.html')


@app.route('/create')
def create():
    return render_template('create.html')


if __name__ == "__main__":
    app.run(debug=True)
