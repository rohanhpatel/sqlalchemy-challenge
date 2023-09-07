# Import the dependencies.
from flask import Flask, jsonify
from sqlalchemy import create_engine, func
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
import datetime as dt

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
measurement = Base.classes.measurement
station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
@app.route("/")
def main_page():
    return (
        f"Available routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&ltstart&gt/<br/>"
        f"/api/v1.0/&ltstart&gt/&ltend&gt/<br/>"
    )

@app.route("/api/v1.0/precipitation")
def get_precip_data():
    # get dates
    recent_date = dt.date.fromisoformat(session.query(func.max(measurement.date))[0][0])
    one_year = recent_date - dt.timedelta(days=365)
    # search for data, filter by after one_year
    query_res = session.query(measurement.date, measurement.prcp).filter(measurement.date >= one_year)
    prcp_dict = dict()
    for row in query_res:
        prcp_dict[row[0]] = row[1]
    return jsonify(prcp_dict)

@app.route("/api/v1.0/stations")
def list_stations():
    station_query = session.query(station.station)
    station_list = list()
    for row in station_query:
        station_list.append(row[0])
    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def get_active_station_temp_data():
    # get most active station by grouping by station and seeing which has the most data, and then selecting the station itself
    most_active_station = session.query(measurement.station, func.count(measurement.station)).group_by(measurement.station).order_by(
        func.count(measurement.station).desc())[0][0]
    # then, get the data only from the most_active_station
    active_station_temps = session.query(measurement.tobs).filter(measurement.station == most_active_station)
    temp_list = list()
    for row in active_station_temps:
        temp_list.append(row[0])
    return jsonify(temp_list)

@app.route("/api/v1.0/<start>")
def s_temp_stats(start):
    # get start date and do similar query as when getting precipitation data
    start_date = dt.date.fromisoformat(start)
    stats = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).filter(measurement.date >= start_date)
    stat_list = list()
    for row in stats:
        for elem in row:
            stat_list.append(elem)
    return jsonify(list(stat_list))

@app.route("/api/v1.0/<start>/<end>")
def se_temp_stats(start, end):
    # get start and end date, then filter twice, for greater than or equal to lower date, and less than or equal to higher date
    start_date = dt.date.fromisoformat(start)
    end_date = dt.date.fromisoformat(end)
    stats = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).filter(measurement.date >= start_date).filter(
        measurement.date <= end_date)
    stat_list = list()
    for row in stats:
        for elem in row:
            stat_list.append(elem)
    return jsonify(list(stat_list))

if __name__ == "__main__":
    app.run(debug=True)
