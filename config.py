import secret
from flask import Flask
import os
import binascii

apikey = secret.apikey
name = "Eco-Go"
TEMPLATE_FOLDER = "templates"
STATIC_FOLDER = "public"
STATIC_URL_PATH = "/static"

jinja_options = {'line_statement_prefix': "#"}

SQL_DEBUG = False


# flask secret key
secret_key = b''
try:
    secret_key = binascii.unhexlify(open(".secret.bin", 'rb').read())
except FileNotFoundError:
    open(".secret.bin", 'xb').write(binascii.hexlify(os.urandom(16)))
    secret_key = binascii.unhexlify(open(".secret.bin", 'rb').read())
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
