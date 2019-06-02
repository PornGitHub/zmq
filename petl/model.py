# gtfsrdb.py: load gtfs-realtime data to a database
# recommended to have the (static) GTFS data for the agency you are connecting
# to already loaded.

# Copyright 2011 Matt Conway

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#   http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Authors:
# Matt Conway: main code

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Boolean, Float, Date, Time
from sqlalchemy.orm import relationship, backref
from geoalchemy2 import Geometry

Base = declarative_base()



# class TripUpdate(Base):
#     __tablename__ = 'trip_updates'
#     id = Column(Integer, primary_key=True)

#     # This replaces the TripDescriptor message
#     # TODO: figure out the relations
#     trip_id = Column(String(10))
#     route_id = Column(String(10))
#     trip_start_time = Column(String(8))
#     trip_start_date = Column(String(10))
#     schedule_relationship = Column(String(9))

#     vehicle_id = Column(String(10))
#     vehicle_label = Column(String(15))
#     vehicle_license_plate = Column(String(10))

#     timestamp = Column(DateTime)

#     StopTimeUpdates = relationship('StopTimeUpdate', backref='TripUpdate')
    
class StopTimeUpdate(Base):
    __tablename__ = 'stop_time_updates'
    time = Column(DateTime, primary_key = True)
    stop_sequence = Column(Integer)
    stop_id = Column(String(10))
    route_id = Column(String(10))
    trip_id = Column(String(10))
    delay = Column(Integer)
    
    stop_type = Column(Integer)

    # TODO: Add domain
    schedule_relationship_stu = Column(String(9))

    # Link it to the TripUpdate
    # trip_update_id = Column(Integer, ForeignKey('trip_updates.id'))
    
    # The .TripUpdate is done by the backref in TripUpdate

class Alert(Base):
    __tablename__ = 'alerts'

    id = Column(Integer, primary_key=True)

    # Collapsed TimeRange
    start = Column(DateTime)
    end = Column(DateTime)    

    # Add domain
    cause = Column(String(20))
    effect = Column(String(20))

    # url = Column(String(300))
    header_text = Column(String(4000))
    description_text = Column(String(4000))

    # InformedEntities = relationship('EntitySelector', backref='Alert')

# class EntitySelector(Base):
#     __tablename__ = 'entity_selectors'
#     oid = Column(Integer, primary_key=True)

#     agency_id = Column(String(15))
#     route_id = Column(String(10))
#     route_type = Column(Integer)
#     stop_id = Column(String(10))

#     # Collapsed TripDescriptor
#     trip_id = Column(String(10))
#     trip_route_id = Column(String(10))
#     trip_start_time = Column(String(8))
#     trip_start_date = Column(String(10))

#     alert_id = Column(Integer, ForeignKey('alerts.oid'))

class VehiclePosition(Base):
    __tablename__ = 'vehicle_positions'
    time = Column(DateTime, primary_key = True)
    trip_id = Column(String(10))
    route_id = Column(String(10))
    trip_start_time = Column(String(20))
    trip_start_date = Column(String(30))
    vehicle_label = Column(Integer)
    schedule_relationship = Column(Integer)
    direction_id = Column(Integer)
    current_stop_sequence = Column(String(10))
    current_status = Column(Integer)
    stop_id = Column(String(10),default=0)
    # position_latitude = Column(Float)
    # position_longitude = Column(Float)
    geo_loc = Column(Geometry('POINT'))

    
   

# So one can loop over all classes to clear them for a new load (-o option)
AllClasses = (StopTimeUpdate, VehiclePosition, Alert)
