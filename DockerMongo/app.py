import os
import sys
import flask 
from flask import Flask, redirect, url_for, request, render_template
from pymongo import MongoClient
import arrow 
import acp_times # brevet time calculations
import logging
import random




app = Flask(__name__)
app.secret_key = 'al;sdjf;wiejrtwkf'

# client = MongoClient(os.environ['DB_PORT_27017_TCP_ADDR'], 27017)
# db = client.tododb

# db.tododb.delete_many{}
# From my mongoDB
# Don't actually have to use. 

try:
    client = MongoClient(os.environ['DB_PORT_27017_TCP_ADDR'], 27017)
    db = client.tododb
    collection = db.control

except:
    print("failure opening database. is mongo running? correct password?")
    sys.exit(1)

@app.route("/")
@app.route("/index")
def index():
    app.logger.debug("Main page entry")
    if 'id' not in flask.session:    
        flask.session['id'] = random.randint(1,21)*5

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

@app.route('/display')
def display():
    """
    Display opening and closing times from
    database.
    """
    app.logger.debug("Displaying times.")

    for entry in collection.find():
        if entry['session_token'] == flask.session['id']:
            # needed if multiple users are accessing the page at the same time 
            flask.g.dist = entry['brevet_dist']
            flask.g.kms = entry['km_list']
            flask.g.open = entry['open_list']
            flask.g.close = entry['close_list']

    return flask.render_template("display.html")

@app.route('/new', methods=['POST'])
def new():
    open_times = request.form.getlist("open")
    close_times = request.form.getlist("close")
    kms = request.form.getlist("km")
    distance = request.form.get("distance")

    if kms[0] == '':
        flask.flash("Table is empty!")
        return flask.redirect(flask.url_for("index"))

    # app.logger.debug("PRINTING OPENS:", opens)
    # app.logger.debug(opens)
    record = {
        'session_token': flask.session['id'],
        'brevet_dist' : distance,
        'km_list' : kms,
        'open_list' : open_times,
        'close_list' : close_times
    }


    collection.insert(record)

    flask.flash("The controle times were saved.")
    
    return flask.redirect(flask.url_for("index"))

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
