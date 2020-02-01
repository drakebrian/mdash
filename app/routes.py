from app import app
from flask import render_template

@app.route('/')
@app.route('/index')
def index():
    context = {'media_name': 'AppleTV'}
    return render_template('index.html', title='Home', context=context)