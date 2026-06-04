import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv
import os

load_dotenv()

conn = psycopg2.connect(
    database=os.getenv('db_name'),
    password=os.getenv('password'),
    user=os.getenv('user'),
    port=os.getenv('port'),
    host=os.getenv('host'),
    client_encoding='utf8'
)

def setup(cursor):
    create_log = '''
    CREATE TABLE IF NOT EXISTS bronze.load_log (
    loaded_at TIMESTAMP DEFAULT NOW());
    '''
    cursor.execute(create_log)
    conn.commit()
    
    create_table = '''
    CREATE TABLE IF NOT EXISTS bronze."311" (
        unique_key VARCHAR PRIMARY KEY,
        created_date VARCHAR,
        closed_date VARCHAR,
        agency VARCHAR,
        agency_name VARCHAR,
        complaint_type VARCHAR,
        descriptor VARCHAR,
        incident_zip VARCHAR,
        incident_address VARCHAR,
        street_name VARCHAR,
        cross_street_1 VARCHAR,
        cross_street_2 VARCHAR,
        address_type VARCHAR,
        city VARCHAR,
        facility_type VARCHAR,
        status VARCHAR,
        resolution_description VARCHAR,
        resolution_action_updated_date VARCHAR,
        community_board VARCHAR,
        police_precinct VARCHAR,
        borough VARCHAR,
        open_data_channel_type VARCHAR,
        park_facility_name VARCHAR,
        park_borough VARCHAR,
        location_type VARCHAR,
        y_coordinate_state_plane VARCHAR,
        intersection_street_1 VARCHAR,
        intersection_street_2 VARCHAR,
        landmark VARCHAR,
        council_district VARCHAR,
        bbl VARCHAR,
        x_coordinate_state_plane VARCHAR,
        latitude VARCHAR,
        longitude VARCHAR,
        location VARCHAR,
        vehicle_type VARCHAR,
        descriptor_2 VARCHAR,
        bridge_highway_name VARCHAR,
        bridge_highway_segment VARCHAR,
        road_ramp VARCHAR,
        bridge_highway_direction VARCHAR,
        taxi_company_borough VARCHAR,
        taxi_pick_up_location VARCHAR,
        due_date VARCHAR,
        loaded_at TIMESTAMP DEFAULT NOW()
    )'''

    cursor.execute(create_table)
    conn.commit()

def connect():
    try:
        cursor = conn.cursor()
        print('Connection to database successful.')
    except Exception:
        print('Unable to connect to database.')
    return cursor

def load(cursor, data):

    rows = [
        (
            row.get('unique_key'),
            row.get('created_date'),
            row.get('closed_date'),
            row.get('agency'),
            row.get('agency_name'),
            row.get('complaint_type'),
            row.get('descriptor'),
            row.get('incident_zip'),
            row.get('incident_address'),
            row.get('street_name'),
            row.get('cross_street_1'),
            row.get('cross_street_2'),
            row.get('address_type'),
            row.get('city'),
            row.get('facility_type'),
            row.get('status'),
            row.get('resolution_description'),
            row.get('resolution_action_updated_date'),
            row.get('community_board'),
            row.get('police_precinct'),
            row.get('borough'),
            row.get('open_data_channel_type'),
            row.get('park_facility_name'),
            row.get('park_borough'),
            row.get('location_type'),
            row.get('y_coordinate_state_plane'),
            row.get('intersection_street_1'),
            row.get('intersection_street_2'),
            row.get('landmark'),
            row.get('council_district'),
            row.get('bbl'),
            row.get('x_coordinate_state_plane'),
            row.get('latitude'),
            row.get('longitude'),
            str(row.get('location')) if row.get('location') else None,
            row.get('vehicle_type'),
            row.get('descriptor_2'),
            row.get('bridge_highway_name'),
            row.get('bridge_highway_segment'),
            row.get('road_ramp'),
            row.get('bridge_highway_direction'),
            row.get('taxi_company_borough'),
            row.get('taxi_pick_up_location'),
            row.get('due_date'),
        )
        for row in data
    ]

    insert = '''
    INSERT INTO bronze."311" (
        unique_key, created_date, closed_date, agency, agency_name,
        complaint_type, descriptor, incident_zip, incident_address, street_name,
        cross_street_1, cross_street_2, address_type, city, facility_type,
        status, resolution_description, resolution_action_updated_date,
        community_board, police_precinct, borough, open_data_channel_type,
        park_facility_name, park_borough, location_type, y_coordinate_state_plane,
        intersection_street_1, intersection_street_2, landmark, council_district,
        bbl, x_coordinate_state_plane, latitude, longitude, location,
        vehicle_type, descriptor_2, bridge_highway_name, bridge_highway_segment,
        road_ramp, bridge_highway_direction, taxi_company_borough,
        taxi_pick_up_location, due_date
    ) VALUES %s
    ON CONFLICT (unique_key) DO UPDATE
    '''

    execute_values(cursor, insert, rows)
    conn.commit()
    print(f'Loaded {len(rows)} rows into bronze.311.')

    if len(rows) > 0: ## I only want to update this table if something actually returns, otherwise, an entry is made which will stop data being gathered.
        cursor.execute("INSERT INTO bronze.load_log DEFAULT VALUES")
        conn.commit()

