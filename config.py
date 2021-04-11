import secret

apikey = secret.apikey
name = "Eco-Go"
TEMPLATE_FOLDER = "templates"
STATIC_FOLDER = "public"
STATIC_URL_PATH = "/public"

jinja_options = {'line_statement_prefix': "#"}


class FlaskConf:
    DEBUG = True
