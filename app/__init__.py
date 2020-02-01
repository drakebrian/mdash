from quart import Quart

app = Quart(__name__, static_url_path='', static_folder='static', template_folder='templates')

from app import routes

app.run()