import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

import pandas as pd
import datetime as dt

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Global Variables
#################################################
most_recent = dt.date(2017,8,23)
year_ago = dt.date(2016,8,23)

#################################################
# Flask Routes
#################################################

# home
@app.route("/")
def home_page():
    """List all available api routes."""
    return (
        f"Welcome to the Home Page!<br/>"
        f"<br></br>"
        f"Available Routes:<br/>"
        f"<b>/api/v1.0/precipitation</b>  -  Precipitation by date<br/>"
        f"<b>/api/v1.0/stations</b>  -  List of stations</br>"
        f"<b>/api/v1.0/tobs</b>  -  List of precipitation measurements from most active station over the previous year</br>"
        f"<b>/api/v1.0/start_date</b>  -  Enter date (yyyymmdd, yyyy-mm-dd, or yyyy mm dd)</br>"
        f"<b>/api/v1.0/start_date/end_date</b>  -  Enter dates (yyyymmdd, yyyy-mm-dd, or yyyy mm dd)"
    )

@app.route("/api/v1.0/precipitation")
def precip():
    # Create session
    session = Session(engine)

    results = session.query(Measurement.date, Measurement.prcp).all()

    #close session
    session.close()

    precip_data = []
    for date, prcp in results:
        precip_dict = {}
        precip_dict[date]=prcp
        precip_data.append(precip_dict)
    
    return jsonify(precip_data)


@app.route("/api/v1.0/stations")
def stations():
    # Create session
    session = Session(engine)

    #Query
    results = session.query(Station.station).all()

    session.close()

    stations = list(np.ravel(results))
    return jsonify(stations)


@app.route("/api/v1.0/tobs")
def temps():
    session = Session(engine)

    results = session.query(Measurement.date,Measurement.prcp).filter(Measurement.station == 'USC00519281').filter(Measurement.date >= year_ago).filter(Measurement.date <= most_recent).all()
    
    session.close()

    prec = list(np.ravel(results))

    return jsonify(prec)


@app.route("/api/v1.0/<start>")
def start(start):
    session = Session(engine)

    if " " in start:
        yr = start.split(" ")[0]
        m = start.split(" ")[1]
        d = start.split(" ")[2]
    elif "-" in start:
        yr = start.split("-")[0]
        m = start.split("-")[1]
        d = start.split("-")[2]
    elif len(start) == 8:
        yr = start[0:4]
        m = start[4:6]
        d = start[6:8]
    else:
        return jsonify({"error": "Character not found. Make sure date is entered correctly (yyyymmdd, yyyy-mm-dd, or yyyy mm dd)"}), 404

    allres = []
    results = session.query(Measurement.date,func.min(Measurement.tobs).label("TMIN"),\
        func.max(Measurement.tobs).label("TMAX"),func.avg(Measurement.tobs).label("TAVG")).\
        filter(Measurement.date >= dt.date(int(yr),int(m),int(d))).group_by(Measurement.date).all()

    session.close()

    for date, tmin, tmax, tavg in results:
        temp_dict = {}
        temp_dict["date"]= date
        temp_dict["TMIN"]= tmin
        temp_dict["TMAX"]= tmax
        temp_dict["TAVG"]= tavg
        allres.append(temp_dict)
    
    return jsonify(allres)
    

  
@app.route("/api/v1.0/<start>/<end>")
def start_end(start,end):
    session = Session(engine)

    # Canonicalize user input
    if " " in start:
        syr = start.split(" ")[0]
        sm = start.split(" ")[1]
        sd = start.split(" ")[2]
    elif "-" in start:
        syr = start.split("-")[0]
        sm = start.split("-")[1]
        sd = start.split("-")[2]
    elif len(start) == 8:
        syr = start[0:4]
        sm = start[4:6]
        sd = start[6:8]
    else:
        return jsonify({"error": "Character not found. Make sure dates are entered correctly (yyyymmdd, yyyy-mm-dd, or yyyy mm dd)"}), 404

    if " " in end:
        eyr = end.split(" ")[0]
        em = end.split(" ")[1]
        ed = end.split(" ")[2]
    elif "-" in end:
        eyr = end.split("-")[0]
        em = end.split("-")[1]
        ed = end.split("-")[2]
    elif len(end) == 8:
        eyr = end[0:4]
        em = end[4:6]
        ed = end[6:8]
    else:
        return jsonify({"error": "Character not found. Make sure dates are entered correctly (yyyymmdd, yyyy-mm-dd, or yyyy mm dd)"}), 404


    # query
    allres = []
    results = session.query(Measurement.date,func.min(Measurement.tobs).label("TMIN"),\
        func.max(Measurement.tobs).label("TMAX"),func.avg(Measurement.tobs).label("TAVG")).\
        filter(Measurement.date >= dt.date(int(syr),int(sm),int(sd))).\
        filter(Measurement.date <= dt.date(int(eyr),int(em),int(ed))).\
        group_by(Measurement.date).all()

    # close session
    session.close()

    # put into dictionary and jsonify
    for date, tmin, tmax, tavg in results:
        temp_dict = {}
        temp_dict["date"]= date
        temp_dict["TMIN"]= tmin
        temp_dict["TMAX"]= tmax
        temp_dict["TAVG"]= tavg
        allres.append(temp_dict)
    
    return jsonify(allres)




if __name__ == '__main__':
    app.run(debug=True)