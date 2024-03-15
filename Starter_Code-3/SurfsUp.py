# Import the dependencies.
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from datetime import datetime, timedelta
from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save reference to the table
Measurement = Base.classes.hawaii_measurements.csv
Station = Base.classes.hawaii_stations.csv

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
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt;<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
#Return the last 12 months of precipitation data.
    # Calculate the date 1 year ago from today
    end_date = datetime(2017,8,23)
    one_year_ago = end_date - timedelta(days=365)
    
    # Query for the last 12 months of precipitation data
    results = session.query(Measurement.date, Measurement.prcp)\
                     .filter(Measurement.date >= one_year_ago)\
                     .all()
    
    # Convert the query results to a dictionary
    precipitation_data = {}
    for date, prcp in results:
        precipitation_data[date] = prcp
    
    # Return the JSON representation of the dictionary
    return jsonify(precipitation_data)

@app.route("/api/v1.0/stations")
def get_stations():
#Return a JSON list of stations.
    # Query all stations from the database
    stations = session.query(Station).all()
    
    # Convert the list of stations to a list of dictionaries
    stations_list = []
    for station in stations:
        stations_list.append({
            "station_id": station.station,
            "name": station.name,
            "latitude": station.latitude,
            "longitude": station.longitude,
            "elevation": station.elevation
        })
    
    # Return the JSON representation of the list of stations
    return jsonify(stations_list)

@app.route("/api/v1.0/tobs")
def observation_temperature():
#Return a JSON list of temperature observations for the previous year.
    # Find the most active station
    most_active_station = session.query(Measurement.station, func.count(Measurement.station))\
                                .group_by(Measurement.station)\
                                .order_by(func.count(Measurement.station).desc())\
                                .first()[0]
    
    # Calculate the date 1 year ago from today
    end_date = datetime(2017,8,23)
    one_year_ago = end_date - timedelta(days=365)
    
    # Query temperature observations for the most active station for the previous year
    temperature_observations = session.query(Measurement.date, Measurement.tobs)\
                                      .filter(Measurement.station == most_active_station)\
                                      .filter(Measurement.date >= one_year_ago)\
                                      .all()
    
    # Convert the list of temperature observations to a list of dictionaries
    temperature_list = []
    for date, tobs in temperature_observations:
        temperature_list.append({
            'date': date,
            'temperature': tobs
        })
    
    # Return the JSON representation of the list of temperature observations
    return jsonify(temperature_list)

@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def temperature_stats(start, end=None):
#Return a JSON list of temperature statistics for the specified start and end dates."""
    # Convert start and end dates to datetime objects
    start_date = datetime.strptime(start, '%Y-%m-%d')
    end_date = datetime.strptime(end, '%Y-%m-%d') if end else None
    
    # Query temperature statistics based on start and end dates
    if end_date:
        stats = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs))\
                      .filter(Measurement.date >= start_date)\
                      .filter(Measurement.date <= end_date)\
                      .all()
    else:
        stats = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs))\
                      .filter(Measurement.date >= start_date)\
                      .all()
    
    # Extract temperature statistics
    tmin, tavg, tmax = stats[0]
    
    # Create a dictionary with temperature statistics
    temperature_stats = {
        'start_date': start_date.strftime('%Y-%m-%d'),
        'end_date': end_date.strftime('%Y-%m-%d') if end_date else None,
        'tmin': tmin,
        'tavg': tavg,
        'tmax': tmax
    }
    
    # Return the JSON representation of temperature statistics
    return jsonify(temperature_stats)

if __name__ == '__main__':
    app.run(debug=True)
