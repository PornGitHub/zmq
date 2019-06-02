

from google.transit import gtfs_realtime_pb2
import urllib
from urllib.request import urlopen
import petl


#---------------
from google.transit import gtfs_realtime_pb2
from optparse import OptionParser
import time as t
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from urllib.request import urlopen
from model import *
from datetime import datetime, timedelta
from shapely.geometry import Point
import geoalchemy2 
from geoalchemy2 import shape
import psycopg2
from sqlalchemy.orm import sessionmaker
from petl import look, todb
#-----------------------------------

feed = gtfs_realtime_pb2.FeedMessage()
# response = urlopen('http://gtfs.openov.nl/gtfs-rt/tripUpdates.pb')
# feed.ParseFromString(response.read())







con = psycopg2.connect(dbname='test', user='postgres', host='localhost', password='')

cur = con.cursor()
#constraints for vehicle_positions

# constraints = [dict(name='date_val', field='foo', test=int)]

def vehicleP():
    while True:
        feed.ParseFromString(
        urlopen('http://gtfs.openov.nl/gtfs-rt/vehiclePositions.pb').read()
        )
        data = []
        
        timer1 = datetime.now()
        timer2 = datetime.now() - timedelta(minutes=1)
        for entity in feed.entity:
            vp = entity.vehicle
            timex = datetime.fromtimestamp(vp.timestamp)
            if timex < timer1 and timex > timer2:
                x = vp.position.longitude
                y = vp.position.latitude
                time = datetime.fromtimestamp(vp.timestamp)
                geo = shape.from_shape(Point(x, y), srid=4326)
                schedule_relationship = vp.trip.schedule_relationship,
                direction_id = vp.trip.direction_id,
                current_stop_sequence = vp.current_stop_sequence,
                current_status = vp.current_status,
                trip_id = vp.trip.trip_id,
                route_id = vp.trip.route_id,
                stop_id = vp.stop_id,
                # trip_start_time = datetime.strptime(vp.trip.start_time, '%H:%M:%S').time(),
                # trip_start_date = datetime.strptime(vp.trip.start_date, "%d%m%Y").date(), 
                trip_start_time = vp.trip.start_time,
                trip_start_date = vp.trip.start_date,
                vehicle_label = vp.vehicle.label,


            data.append(
            {'time':time, 
            'geo_loc':str(geo), 
            'schedule_relationship':vp.trip.schedule_relationship, 
            'direction_id':direction_id,
            'current_stop_sequence':current_stop_sequence,
            'current_status':current_status,
            'trip_id':trip_id,
            'route_id':route_id,
            'stop_id':stop_id,
            'trip_start_time':trip_start_time,
            'trip_start_date':trip_start_date,
            'vehicle_label':vehicle_label,
            })

            
            
        table1 = petl.fromdicts(data)
        print(petl.nrows(table1))
        petl.appenddb(table1, con, 'vehicle_positions')
        t.sleep(60)
