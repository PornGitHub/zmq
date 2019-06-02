

from google.transit import gtfs_realtime_pb2
from optparse import OptionParser
import time
import sys
import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from urllib.request import urlopen
from model import *
from datetime import datetime, timedelta
import shapely
from shapely.geometry import Point, LineString, Polygon
import geoalchemy2 
from geoalchemy2 import shape
import psycopg2
from sqlalchemy.orm import sessionmaker



# con = psycopg2.connect(dbname='ov', user='postgres', host='localhost', password='test123')
# cur = con.cursor()

# try:
#     cur.execute("CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;")

#     cur.execute("CREATE EXTENSION IF NOT EXISTS postgis;")

#     print("database bevat nu timescaledb en postgis")

# except:
#     print("oops kon postgis/timescaledb niet koppelen aan de database")

# con.commit()
# cur.close()
# con.close()


# p = OptionParser()
# p.add_option('-t', '--trip-updates', dest='tripUpdates', default=None, 
#              help='The trip updates URL', metavar='URL')

# p.add_option('-a', '--alerts', default=None, dest='alerts', 
#              help='The alerts URL', metavar='URL')

# p.add_option('-p', '--vehicle-positions', dest='vehiclePositions', default=None, 
#              help='The vehicle positions URL', metavar='URL')

# p.add_option('-d', '--database', default=None, dest='dsn',
#              help='Database connection string', metavar='DSN')

# p.add_option('-o', '--discard-old', default=False, dest='deleteOld', 
#              action='store_true', 
#              help='Dicard old updates, so the database is always current')

# p.add_option('-c', '--create-tables', default=False, dest='create',
#              action='store_true', help="Create tables if they aren't found")

# p.add_option('-w', '--wait', default=30, type='int', metavar='SECS',
#              dest='timeout', help='Time to wait between requests (in seconds)')

# p.add_option('-v', '--verbose', default=False, dest='verbose', 
#              action='store_true', help='Print generated SQL')

# p.add_option('-l', '--language', default='en', dest='lang', metavar='LANG',
#              help='When multiple translations are available, prefer this language')

# p.add_option('-1', '--once',  default=False, dest='once', action='store_true',
#              help='only run the loader one time')

# opts, args = p.parse_args()

# if opts.dsn == None:
#     print('No database specified!')

#     exit(1)

# if opts.alerts == None and opts.tripUpdates == None and opts.vehiclePositions == None:
#     print('No trip updates, alerts, or vehicle positions URLs were specified!')
#     exit(1)

# if opts.alerts == None:
#     print('Warning: no alert URL specified, proceeding without alerts')

# if opts.tripUpdates == None:
#     print('Warning: no trip update URL specified, proceeding without trip updates')

# if opts.vehiclePositions == None:
#     print('Warning: no vehicle positions URL specified, proceeding without vehicle positions')
    
# Connect to the database
engine = create_engine(opts.dsn, echo=opts.verbose)
# sessionmaker returns a class
session = sessionmaker(bind=engine)()

# Check if it has the tables
# Base from model.py
for table in list(Base.metadata.tables.keys()):
    if not engine.has_table(table):
        if opts.create:
            print('Creating table %s' % table)
            Base.metadata.tables[table].create(engine)
            
            
            
        else:
            print('Missing table %s! Use -c to create it.' % table)
            # exit(1)




def getTrans(string, lang):
    untranslated = None

    if len(string.translation) == 1:
        return string.translation[0].text

    for t in string.translation:
        if t.language == lang:
            return t.text
        if t.language == None:
            untranslated = t.text
    return untranslated

try:
    keep_running = True
    while keep_running:
        try:
        
            if opts.deleteOld:
                
                for theClass in AllClasses:
                    for obj in session.query(theClass):
                        session.delete(obj)

            if opts.tripUpdates:
                fm = gtfs_realtime_pb2.FeedMessage()
                fm.ParseFromString(
                    urlopen(opts.tripUpdates).read()
                    )

                
                timestamp = datetime.utcfromtimestamp(fm.header.timestamp)

                
                if fm.header.gtfs_realtime_version != '1.0':
                    print('Warning: feed version has changed: found %s, expected 1.0' % fm.header.gtfs_realtime_version)

                print('processing %s trip updates to stop_time_updates' % len(fm.entity))
                for entity in fm.entity:

                    tu = entity.trip_update
                    trip_idtemp = tu.trip.trip_id
                    trip_routetemp = tu.trip.route_id
                    
                    # dbtu = TripUpdate(
                    #     trip_id = tu.trip.trip_id,
                    #     route_id = tu.trip.route_id,
                    #     trip_start_time = tu.trip.start_time,
                    #     trip_start_date = tu.trip.start_date,

                    #     # get the schedule relationship
                    #     # This is somewhat undocumented, but by referencing the 
                    #     # DESCRIPTOR.enum_types_by_name, you get a dict of enum types
                    #     # as described at http://code.google.com/apis/protocolbuffers/docs/reference/python/google.protobuf.descriptor.EnumDescriptor-class.html
                    #     schedule_relationship = tu.trip.DESCRIPTOR.enum_types_by_name['ScheduleRelationship'].values_by_number[tu.trip.schedule_relationship].name,

                    #     vehicle_id = tu.vehicle.id,
                    #     vehicle_label = tu.vehicle.label,
                    #     vehicle_license_plate = tu.vehicle.license_plate,
                    #     timestamp = timestamp)

                    for stu in tu.stop_time_update:
                        timex = datetime.fromtimestamp(stu.arrival.time)
                        if timex.time() < datetime.now().time() and timex > (datetime.now() - timedelta(minutes=1)):
                            dbstu = StopTimeUpdate(
                                time = datetime.fromtimestamp(stu.arrival.time),
                                trip_id = trip_idtemp,
                                route_id = trip_routetemp,
                                stop_sequence = stu.stop_sequence,
                                stop_id = stu.stop_id,
                                stop_type = 1,
                                delay = stu.arrival.delay,
                                schedule_relationship_stu = stu.schedule_relationship
                                )
                            # attempt1.append(dbstu)
                            session.add(dbstu)
                            
                        # session.add(dbstu2)
                        # dbtu.StopTimeUpdates.append(dbstu)
                        # dbtu.StopTimeUpdates.append(dbstu2)

                    # session.add(dbtu)

            if opts.alerts:
                fm = gtfs_realtime_pb2.FeedMessage()
                fm.ParseFromString(
                    urlopen(opts.alerts).read()
                    )
                # Convert this a Python object, and save it to be placed into each
                # trip_update
                # timestamp = datetime.utcfromtimestamp(fm.header.timestamp)

                # Check the feed version
                # if fm.header.gtfs_realtime_version != '1.0':
                #     print('Warning: feed version has changed: found %s, expected 1.0' % fm.header.gtfs_realtime_version)

                print('Adding %s alerts' % len(fm.entity))
                for entity in fm.entity:
                    alert = entity.alert
                    dbalert = Alert(
                        # start = alert.active_period[0].start,
                        # end = alert.active_period[0].end,
                        cause = alert.DESCRIPTOR.enum_types_by_name['Cause'].values_by_number[alert.cause].name,
                        effect = alert.DESCRIPTOR.enum_types_by_name['Effect'].values_by_number[alert.effect].name,
                        start = datetime.fromtimestamp(alert.active_period[0].start),
                        end = datetime.fromtimestamp(alert.active_period[0].end),
                        # cause = alert.cause,
                        # effect = alert.effect,
                        # url = alert.url,
                        # header_text = alert.header_text.translation.text,
                        # description_text = alert.description_text.translation.text
                        # url = getTrans(alert.url, opts.lang),
                        header_text = getTrans(alert.header_text, opts.lang),
                        description_text = getTrans(alert.description_text,
                                                    opts.lang)
                        )

                    session.add(dbalert)
                    # for ie in alert.informed_entity:
                    #     dbie = EntitySelector(
                    #         agency_id = ie.agency_id,
                    #         route_id = ie.route_id,
                    #         route_type = ie.route_type,
                    #         stop_id = ie.stop_id,

                    #         trip_id = ie.trip.trip_id,
                    #         trip_route_id = ie.trip.route_id,
                    #         trip_start_time = ie.trip.start_time,
                    #         trip_start_date = ie.trip.start_date)
                    #     session.add(dbie)
                    #     dbalert.InformedEntities.append(dbie)
            if opts.vehiclePositions:
                fm = gtfs_realtime_pb2.FeedMessage()
                fm.ParseFromString(
                    urlopen(opts.vehiclePositions).read()
                    )

                # Convert this a Python object, and save it to be placed into each
                # vehicle_position
                # timestamp = datetime.fromtimestamp(fm.header.timestamp)

                # Check the feed version
                if fm.header.gtfs_realtime_version != '1.0':
                    print('Warning: feed version has changed: found %s, expected 1.0' % fm.header.gtfs_realtime_version)

                print('Adding %s vehicle_positions' % len(fm.entity))
                for entity in fm.entity:

                    vp = entity.vehicle
                    x = vp.position.longitude
                    y = vp.position.latitude
                    dbvp = VehiclePosition(
                        time = datetime.fromtimestamp(vp.timestamp),
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
                        # position_latitude = vp.position.latitude,
                        # position_longitude = vp.position.longitude,
                        geo_loc = shape.from_shape(Point(x, y), srid=4326),
                        )
                    
                    session.add(dbvp)

            
            session.commit()
            # print(attempt1)
        except:
        #else:
            print('Exception occurred in iteration')
            print(sys.exc_info())


        if opts.once:
            print("Executed the load ONCE ... going to stop now...")
            keep_running = False
        else:
            time.sleep(opts.timeout)

finally:
    print("Closing session . . .")
    session.close()
