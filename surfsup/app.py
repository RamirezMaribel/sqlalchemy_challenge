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
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement=Base.classes.measurement
Station=Base.classes.station

# Create our session (link) from Python to the DB

session = Session(engine)
#################################################
# Flask Setup
#################################################

app = Flask(__name__)


#################################################
# Flask Routes
#################################################
#1 of part 2 of homework
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start> enter a date here YYYY-MM-DD<br/>"
        f"/api/v1.0/<start>/<end><br/>"
    )
#2 of part 2 of homework
 # Convert the query results from your precipitation analysis 
    # (i.e. retrieve only the last 12 months of data) to a dictionary using date as the key and prcp as the value.
    
@app.route("/api/v1.0/precipitation")
def precipitation():
   
    recentdate=session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    year=datetime.strptime(recentdate,'%Y-%m-%d') - timedelta(days=366)
    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date>=year).all()

    #creating the dictionary
    precipitation_dict={}
    for result in results:
        date=result[0]
        prcp=result[1]
        precipitation_dict[date]=prcp
    #Return the JSON representation of your dictionary
    return jsonify(precipitation_dict)


#3 of part 2 of homework

@app.route("/api/v1.0/stations")
def stations():
    
    stations=session.query(Station).group_by(Station.station).all()

    #creating the dictionary
    stations_list=[]
    for result in stations:
        station_dict={}
        station_dict['station']=result.station
        station_dict['name']=result.name
        stations_list.append(station_dict)

    #Return a JSON list of stations from the dataset
    return jsonify(stations_list)

#4 of paret 2 of homework

#Query the dates and temperature observations of htem ost-active station for the previous year of data


@app.route("/api/v1.0/tobs")
def tobs():

    latestdate=session.query(func.max(Measurement.date)).scalar()
    latest=datetime.strptime(latestdate,'%Y-%m-%d')
    prioryear=latest-timedelta(days=365)
    prioryear_str=prioryear.strftime('%Y-%m-%d')
    activestation=session.query(Measurement.date,Measurement.tobs).filter(Measurement.station=='USC00519281').filter(Measurement.date>=prioryear_str).filter(Measurement.date<=latest).all()

    #creating the dictionary
    activestation_list=[]
    for result in activestation:
        USC00519281_dict={}
        USC00519281_dict['date']=result[0]
        USC00519281_dict['temperature']=result[1]
        activestation_list.append(USC00519281_dict)

  #Return a JSON list of temperature observations for the previous year   
    return jsonify(activestation_list)

#5 of part 2 of homework

#Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature fora specified start or start-end range.
#For a specified start, calculate TMIN, TAVG, and TMAX for all the dates greater than or equal to the start date.
#For a specified start date and end date, calculate TMIN, TAVG, and TMAX for the dates from the start date to the end date, inclusive.

@app.route('/api/v1.0/<start>')
def calc_temps_start(start):
    min_temp=session.query(func.min(Measurement.tobs)).filter(Measurement.date>=start).scalar()
    avg_temp=session.query(func.avg(Measurement.tobs)).filter(Measurement.date>=start).scalar()
    max_temp=session.query(func.max(Measurement.tobs)).filter(Measurement.date>=start).scalar()

   #creating a dictionary
    calc_results_dict = {"min_temp": min_temp,
                        "avg_temp": avg_temp,
                        "max_temp": max_temp}
    
#turning dictionary into list to jsonify it
    calc_results_list=list(calc_results_dict.values())

    return jsonify(calc_results_list)


@app.route('/api/v1.0/<start>/<end>')
def calc_temps_start_end(start, end):
    min_temp = session.query(func.min(Measurement.tobs)).filter(Measurement.date >= start, Measurement.date <= end).scalar()
    avg_temp = session.query(func.avg(Measurement.tobs)).filter(Measurement.date >= start, Measurement.date <= end).scalar()
    max_temp = session.query(func.max(Measurement.tobs)).filter(Measurement.date >= start, Measurement.date <= end).scalar()




if __name__ == '__main__':
    app.run(debug=True)