#Import Flask
from flask import Flask, jsonify

#Import SQLite
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect
from sqlalchemy import Column, Integer, String, Float

import datetime as dt
import numpy as np

#Set Up Engine
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#Set Up Flask
app = Flask(__name__)

# Design a query to retrieve the last 12 months of precipitation data and plot the results
last_date = engine.execute('select max(date) from measurement')
    
# Calculate the date 1 year ago from the last data point in the database. Use dt to subtract 365 days from the date
last_year = dt.date(2017, 8, 23) - dt.timedelta(days = 365)

# Perform a query to retrieve the data and precipitation scores
precip = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date > last_year).all()

#Query Station Name
station = session.query(Station.station).all()

#Query Dates and Temp From Previous Year
temp_ly = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date > last_year).all()


#Move query results into a dict
precip_dict = {}

for record in precip:
    precip_dict[record[0]] = record[1]

#Create a list of stations
station_list = []
        
for record in station:
    station_list.append(record)


###########################
# App Routes
###########################
@app.route('/')
def welcome():
    return(
        f'Welcome To Precipitation API!<br/>'
        f'/api/v1.0/precipitation = Date and Precipitation<br/>'
        f'/api/v1.0/stations = Station List<br/>'
        f'/api/v1.0/tobs = Dates and Temp Observations for the previous year<br/>'
        f'/api/v1.0/start = Use (YYYY-MM-DD) to calculate MIN/AVG/MAX temperature with dates greater than the start date<br/>'
        f'/api/v1.0/start/end = Use (YYYY-MM-DD) to calculate the MIN/AVG/MAX temperature for dates between the start and end date<br/>'
    )

@app.route('/api/v1.0/precipitation')
def precipitation():
    return jsonify(precip_dict) 

@app.route('/api/v1.0/stations')
def stations():
    return jsonify(station_list)

@app.route('/api/v1.0/tobs')
def temp():
    return jsonify(temp_ly)

@app.route('/api/v1.0/<start>')
def start_only(start):
    start_date= dt.datetime.strptime(start, '%Y-%m-%d')
    last_year = dt.timedelta(days=365)
    start = start_date-last_year
    end =  dt.date(2017, 8, 23)
    trip_data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    trip = list(np.ravel(trip_data))
    return jsonify(trip)

@app.route('/api/v1.0/<start>/<end>')
def start_end(start,end):

  # go back one year from start/end date and get Min/Avg/Max temp     
    start_date= dt.datetime.strptime(start, '%Y-%m-%d')
    end_date= dt.datetime.strptime(end,'%Y-%m-%d')
    last_year = dt.timedelta(days=365)
    start = start_date-last_year
    end = end_date-last_year
    trip_data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    trip = list(np.ravel(trip_data))
    return jsonify(trip)





if __name__ == "__main__":
    app.run(debug=True)





