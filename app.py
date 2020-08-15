import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

import datetime as dt
import numpy as np

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
# Flask Routes
#################################################

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)

    """Convert the query results to a dictionary using date as the key and prcp as the value"""
    results = session.query(Measurement.date, Measurement.prcp).all()

    session.close()
    
    all_precip = []
    for date, prcp in results:
        prcp_dict = {}
        prcp_dict[f"{date}"] = prcp
        all_precip.append(prcp_dict)

    return jsonify(all_precip)

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)

    results = session.query(Station.station, Station.name).all()

    session.close()
    
    all_stations = []
    for station, name in results:
        station_dict = {}
        station_dict[f"{station}"] = name
        all_stations.append(station_dict)

    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)

    results = session.query(Measurement.tobs, Measurement.date).\
        filter(Measurement.date >= '2016-08-23').\
        filter(Measurement.station == "USC00519397").all()

    session.close()

    tobs_dict = []
    for tobs, date in results:
        station_dict = {}
        station_dict[f"{date}"] = tobs
        tobs_dict.append(station_dict)

    return jsonify(tobs_dict)

@app.route("/api/v1.0/<start>")
def start_func(start):
    session = Session(engine)

    results = session.query(Measurement.date).\
        group_by(Measurement.date).all()

    all_dates = list(np.ravel(results))
    
    if start in all_dates:
        tobs_results = session.query(Measurement.tobs).\
            filter(Measurement.date >= start).\
            group_by(Measurement.tobs).all()
        temps = list(np.ravel(tobs_results))
        low = min(temps)
        high = max(temps)
        average = round(sum(temps) / len(temps))
        session.close()
        return jsonify(f"Minimum temp. is : {low} Max temp is : {high} Average temp is: {average}")
        
    session.close()
    return jsonify({"error": f"{start} not found."}), 404

@app.route("/api/v1.0/<start>/<end>")
def startend_func(start, end):
    session = Session(engine)

    results = session.query(Measurement.date).\
        group_by(Measurement.date).all()

    all_dates = list(np.ravel(results))
    
    if (start) in all_dates:
        if (end) in all_dates: 
            tobs_results = session.query(Measurement.tobs).\
                filter(Measurement.date >= start).\
                filter(Measurement.date <= end).\
                group_by(Measurement.tobs).all()
            temps = list(np.ravel(tobs_results))
            low = min(temps)
            high = max(temps)
            average = round(sum(temps) / len(temps))
            session.close()
            return jsonify(f"Minimum temp. is : {low} Max temp is : {high} Average temp is: {average}")
        session.close
        return jsonify({"error": f"{end} not found."}), 404
    session.close()
    return jsonify({"error": f"{start} not found."}), 404

@app.route("/")
def welcome():
    return (
        f"Welcome to the Climate API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )


if __name__ == "__main__":
    app.run(debug=True)
