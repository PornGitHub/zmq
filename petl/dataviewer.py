


from google.transit import gtfs_realtime_pb2
from urllib.request import urlopen
import petl
from enum import Enum
from multiprocessing import Process
import multiprocessing
from google.transit import gtfs_realtime_pb2
from optparse import OptionParser
import time as t
import sys
from datetime import datetime, timedelta, date
from shapely.geometry import Point
from geoalchemy2 import shape
import psycopg2
import psycopg2.extras
from petl import look, todb


def connection():
    con = psycopg2.connect(dbname='test', user='postgres', host='localhost', password='')
    cur = con.cursor()

    return con





class ScheduleRelationship(Enum):
    SCHEDULED = 0;
    ADDED = 1;
    UNSCHEDULED = 2;
    CANCELED = 3;


def vp():
    con = psycopg2.connect(dbname='test', user='postgres', host='localhost', password='')
    cur = con.cursor()
    feed = gtfs_realtime_pb2.FeedMessage()
    while True:
        feed.ParseFromString(
        urlopen('http://gtfs.openov.nl/gtfs-rt/vehiclePositions.pb').read()
        )
        data = []
        timer = date.today()
        for entity in feed.entity:
            vp = entity.vehicle
            timex = datetime.fromtimestamp(vp.timestamp)
            if timex.date() == timer:
                x = vp.position.longitude
                y = vp.position.latitude
                time = datetime.fromtimestamp(vp.timestamp)
                geo_loc = str(shape.from_shape(Point(x, y), srid=4326))
                schedule_relationship = vp.trip.schedule_relationship,
                direction_id = vp.trip.direction_id,
                current_stop_sequence = vp.current_stop_sequence,
                #see "enum VehicleStopStatus"
                current_status = vp.DESCRIPTOR.enum_types_by_name['VehicleStopStatus'].values_by_number[vp.current_status].name,
                trip_id = vp.trip.trip_id,
                route_id = vp.trip.route_id,
                stop_id = vp.stop_id,
                # trip_start_time = datetime.strptime(vp.trip.start_time, '%H:%M:%S').time(),
                # trip_start_date = datetime.strptime(vp.trip.start_date, "%d%m%Y").date(), 
                trip_start_time = vp.trip.start_time,
                trip_start_date = vp.trip.start_date,
                vehicle_label = vp.vehicle.label,
                
                

                data.append(
                [time, 
                geo_loc, 
                direction_id,
                current_stop_sequence,
                current_status,
                trip_id,
                stop_id,
                vehicle_label,
                ])

        qvp = """INSERT INTO vehicle_positions (time, geo_loc, direction_id, current_stop_sequence, current_status, trip_id, stop_id, vehicle_label)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING"""

        # table1 = petl.fromdicts(data)
        # print('vehicle_positions:' + str(petl.nrows(table1)))
        # petl.appenddb(table1, connection(), 'vehicle_positions')

        psycopg2.extras.execute_batch(cur,qvp,data)
        print("adding vp")
        con.commit()
        
        t.sleep(60)





def stu(sleeptime=30):
    con = psycopg2.connect(dbname='test', user='postgres', host='localhost', password='')
    cur = con.cursor()

    feed = gtfs_realtime_pb2.FeedMessage()

    datatemptu = [{'tu_id':'', 
                    'start_time':'',
                    'start_date':'',
                    'trip_id':'',
                    'route_id':'',
                    'direction_id':'',
                    'sr':''}]

    datatempstu =[{'time':'', 
                    'departure_time':'',
                    'stu_id':'',
                    'stop_sequence':'',
                    'trip_id':'',
                    'route_id':'',
                    'stop_id':'',
                    'arrival_delay':'',
                    'departure_delay':''
                    }]
    while True:
        feed.ParseFromString(
        urlopen('http://gtfs.openov.nl/gtfs-rt/trainUpdates.pb').read()
        )
        
        liststu = []
        listtu= []
        liststucompare = []
        listtucompare = []
        for entity in feed.entity:
            tu = entity.trip_update
            tu_id = entity.id
            try:
                start_time = datetime.strptime(tu.trip.start_time, '%H:%M:%S').time()
            except ValueError:
                continue
            start_date = tu.trip.start_date[:4]+"-"+tu.trip.start_date[4:6]+"-"+tu.trip.start_date[6:8]
            trip_id = tu.trip.trip_id
            route_id = tu.trip.route_id
            direction_id = tu.trip.direction_id
            schedule = ScheduleRelationship(tu.trip.schedule_relationship).name


            # data2.append({'tu_id':tu_id, 
            #         'start_time':start_time,
            #         'start_date':start_date,
            #         'trip_id':trip_id,
            #         'route_id':route_id,
            #         'direction_id':direction_id,
            #         'sr':sr
            #         })
            listtu.append([tu_id, 
                    start_time,
                    start_date,
                    trip_id,
                    route_id,
                    direction_id,
                    schedule])

            for stu in tu.stop_time_update:
                if stu.arrival.time == '':
                    time = datetime.fromtimestamp(stu.departure.time)
                else:
                    time = datetime.fromtimestamp(stu.arrival.time)
                departure_time = datetime.fromtimestamp(stu.departure.time)
                trip_id = trip_id,
                stop_sequence = stu.stop_sequence,
                stop_id = stu.stop_id,
                arrival_delay = stu.arrival.delay,
                departure_delay = stu.arrival.delay,
                stu_id = (str(tu_id) + str(stop_sequence[0]))
                tu_id = tu_id

                liststu.append([
                time, 
                departure_time,
                stop_sequence,
                trip_id,
                stop_id,
                arrival_delay,
                departure_delay,
                tu_id
                ])

                # data.append(
                # {'time':time, 
                # 'departure_time':departure_time,
                # 'stu_id':stu_id,
                # 'stop_sequence':stop_sequence,
                # 'trip_id':trip_id,
                # 'route_id':route_id,
                # 'stop_id':stop_id,
                # 'arrival_delay':arrival_delay,
                # 'departure_delay':departure_delay
                # })
                # cur.execute_batch("""
                # INSERT INTO stop_time_updates (time, departure_time, stu_id, stop_sequence, trip_id, route_id, stop_id, arrival_delay, departure_delay)
                # VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
                # """, (time, departure_time, stu_id, stop_sequence, trip_id, route_id, stop_id, arrival_delay, departure_delay))

       



        liststufilter = filter(lambda x:x not in liststucompare,liststu)
        listtufilter = filter(lambda x:x not in listtucompare,listtu)

        # qtu = """INSERT INTO tu_test (tu_id, start_time, start_date, trip_id, route_id, direction_id, sr)
        #     VALUES (%s, %s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING"""
                
        qstu = """INSERT INTO stu_trains (time, departure_time, stop_sequence, trip_id, stop_id, arrival_delay, departure_delay, tu_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING"""

        
        # psycopg2.extras.execute_batch(cur,qtu,listtufilter)
        # print('adding tu')
        psycopg2.extras.execute_batch(cur,qstu,liststufilter)
        print('adding stu')
        con.commit()
        liststucompare = liststu.copy()
        listtucompare = listtu.copy()

        # # table4 = petl.fromdicts(datatemptu)
        # table5 = petl.fromdicts(datatempstu)       
        # table1 = petl.fromdicts(data)
        # # table2 = petl.fromdicts(data2)
        # # uniquetu = petl.antijoin(table2, table4, key='tu_id')
        # uniquestu = petl.antijoin(table1, table5, key='stu_id')
        # # datatemptu = data2.copy()
        # datatempstu = data.copy()
        # print('stop_time_updates' + str(petl.nrows(uniquestu)))
        # # print('trip_updates'+str(petl.nrows(uniquetu)))
        # # petl.appenddb(uniquetu, connection(), 'tu_test')
        # petl.appenddb(uniquestu, connection(), 'stop_time_updates')
        
        
        

        t.sleep(sleeptime)


# def tstu():
#     feed.ParseFromString(
#         urlopen('http://gtfs.openov.nl/gtfs-rt/trainUpdates.pb').read()
#         )
#     for entity in feed.entity:
#         print(entity)



if __name__ == "__main__":
    
    # p1 = Process(target = stu, args=())
    # p = Process(target = vp, args=())
    # p.start()
    # p1.start()
    # p.join()
    # p1.join()
    stu()
    # p1 = Process(target =vp)
    # p2 = Process(target =stu)

    # p1.start()
    # p2.start()

   # enum VehicleStopStatus {
            # // The vehicle is just about to arrive at the stop (on a stop
            # // display, the vehicle symbol typically flashes).
            # INCOMING_AT = 0;

            # // The vehicle is standing at the stop.
            # STOPPED_AT = 1;

            # // The vehicle has departed and is in transit to the next stop.
            # IN_TRANSIT_TO = 2;
            # }


