from flask import Flask
import os
import binascii

SQL_PATH = os.getenv("EG_SQL_PATH", default="sqlite:///data/ecogo.db")
SECRET_KEY_PATH = f"data/flask_secret"
SQL_DEBUG = False

apikey = open(f"data/secret/api_key",'r').read().strip()

name = "Eco-Go"
TEMPLATE_FOLDER = "templates"
STATIC_FOLDER = "public"
STATIC_URL_PATH = "/static"

jinja_options = {'line_statement_prefix': "#"}

# flask secret key
secret_key = b''
try:
    secret_key = binascii.unhexlify(open(SECRET_KEY_PATH, 'rb').read())
except FileNotFoundError as e:
    print(e, "on opening flask secret, creating it")
    open(SECRET_KEY_PATH, 'xb').write(binascii.hexlify(os.urandom(16)))
    secret_key = binascii.unhexlify(open(SECRET_KEY_PATH, 'rb').read())
assert len(secret_key) == 16

class FlaskConf:
    DEBUG = True
    SECRET_KEY = secret_key

def app():
    app = Flask(name, static_url_path = STATIC_URL_PATH)
    app.secret_key = secret_key 
    app.jinja_options = jinja_options
    import datetime
    app.permanent_session_lifetime = datetime.timedelta(days=1)
    f = FlaskConf()
    app.config.from_object(f)
    return app
