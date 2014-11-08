from coursefeed import app

@app.route('/')
def view_index():
    return 'hi'
