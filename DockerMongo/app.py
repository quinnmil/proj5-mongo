import os
import flask 
from flask import Flask, redirect, url_for, request, render_template
from pymongo import MongoClient
import arrow 
import acp_times # brevet time calculations
import logging

app = Flask(__name__)

client = MongoClient(os.environ['DB_PORT_27017_TCP_ADDR'], 27017)
db = client.tododb

# From my mongoDB
# Don't actually have to use. 
uri = 'mongodb://<dbuser>:<dbpassword>@ds143738.mlab.com:43738/cis322'
user = 'quinn'


@app.route("/")
@app.route("/index")
def index():
    app.logger.debug("Main page entry")
    return flask.render_template('calc.html')


@app.errorhandler(404)
def page_not_found(error):
    app.logger.debug("Page not found")
    flask.session['linkback'] = flask.url_for("index")
    return flask.render_template('404.html'), 404

# copied from flask_brevets project. 
@app.route("/_calc_times")
def _calc_times():
    """
    Calculates open/close times from miles, using rules
    described at https://rusa.org/octime_alg.html.
    Expects one URL-encoded argument, the number of miles.
    """
    app.logger.debug("Got a JSON request")

    #Get data recieved
    km = request.args.get('km', 999, type=float)
    brevet_dist = request.args.get('brevet_dist', 0, type=float)
    begin_date = request.args.get('begin_date', 0, type=str)
    begin_time = request.args.get('begin_time', 0, type=str)
    message = ""

    #Check for negative values
    if km < 0:
      message = "Control distance cannot be negative."
      km = 0

    #Control distance cannot exceed 120% brevet distance
    if km > (brevet_dist*1.2):
      message = "Control distance cannot be longer than 120% brevet distance."


    #Brevet start format
    brevet_start = begin_date + " " + begin_time + ":00"
    brevet_start_time = arrow.get(brevet_start, 'YYYY-MM-DD HH:mm:ss')

    open_time = acp_times.open_time(km, brevet_dist, brevet_start_time.isoformat())
    close_time = acp_times.close_time(km, brevet_dist, brevet_start_time.isoformat())
    result = {"open": open_time, "close": close_time, "message": message}
    return flask.jsonify(result=result)

@app.route('/result')
def todo():
    _items = db.tododb.find()
    items = [item for item in _items]

    return render_template('todo.html', items=items)

@app.route('/new', methods=['POST'])
def new():
    item_doc = {
        'open': request.form['open'],
        'close': request.form['close']
    }
    db.tododb.insert_one(item_doc)
    # redirect to something else. 
    return redirect(url_for('calc.html'))

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
