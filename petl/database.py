import psycopg2

con = psycopg2.connect(dbname='test', user='postgres', host='localhost', password='')



cur = con.cursor()
try:
    cur.execute("CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;")

    cur.execute("CREATE EXTENSION IF NOT EXISTS postgis;")

    print("database bevat nu timescaledb en postgis")

except:
    print("oops kon postgis/timescaledb niet koppelen aan de database")

    
#--
cur.execute("""CREATE TABLE IF NOT EXISTS vehicle_positions( 
time timestamp,
trip_id varchar(10),
current_stop_sequence varchar(10),
vehicle_label integer,
direction_id integer,
current_status varchar(20),
stop_id varchar(10),
geo_loc geometry(Point);""")

cur.execute("""create unique index if not exists vehicle_positions_time_uindex
	on vehicle_positions (time);""")

cur.execute("""create unique index if not exists vehicle_positions_trip_id_uindex
	on vehicle_positions (trip_id);""")

#--
cur.execute("""CREATE TABLE IF NOT EXISTS stop_time_updates (
    time timestamp,
	stop_sequence integer,
	stop_id varchar(10),
	trip_id varchar(10),
	arrival_delay integer,
	departure_delay integer,
	departure_time time,
	tu_id varchar(40)
	constraint stop_time_updates_tu_test1_tu_id_fk
	references trip_updates (tu_id)
	on delete cascade

);""")


cur.execute("""create unique index if not exists stop_time_updates_stop_sequence_uindex
	on stop_time_updates (stop_sequence);""")

cur.execute("""create unique index if not exists stop_time_updates_tu_id_uindex
	on stop_time_updates (tu_id);""")
    
#--
cur.execute("""CREATE TABLE IF NOT EXISTS alerts (
    active_period_start timestamp,
	active_period_end timestamp,
	route_id varchar(10),
	stop_id varchar(10),
	cause varchar(30),
	effect varchar(30),
	message text,
	description text
);""")

#--
cur.execute("""CREATE TABLE IF NOT EXISTS trip_updates (
    tu_id varchar,
	start_time time,
	start_date date,
	trip_id integer,
	route_id integer,
	direction_id integer,
	schedule varchar(30)
);""")

cur.execute("""create unique index if not exists trip_updates_tu_id_uindex
	on trip_updates (tu_id);""")





# cur.execute("SELECT create_hypertable(%s, %s)", ("vehicle_positions", "time"))
# cur.execute("SELECT create_hypertable(%s, %s)", ("stop_time_updates", "time"))


con.commit()
cur.close()
con.close()

