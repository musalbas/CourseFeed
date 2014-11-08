import json

from flask import render_template

from coursefeed import app

@app.route('/')
def view_index():
    feed = json.load(open('feed.json'))
    return render_template('feed.html', feed=feed)
