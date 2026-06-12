import psycopg2
from psycopg2.extras import execute_values
from db import connect, conn
from datetime import datetime

def silver_setup(cursor):
    create_silver_log = '''
    CREATE TABLE IF NOT EXISTS silver.load_log (
    run_id SERIAL PRIMARY KEY,
    last_bronze_load_id INTEGER REFERENCES bronze.load_log(load_id),
    loaded_at TIMESTAMP DEFAULT NOW());
    '''
    cursor.execute(create_silver_log)
    conn.commit()

    # at this layer i'm enforcing specific data types
    create_silver = '''
    CREATE TABLE IF NOT EXISTS silver."311" (
        unique_key VARCHAR PRIMARY KEY,
        created_date TIMESTAMP,
        closed_date TIMESTAMP,
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
        resolution_action_updated_date TIMESTAMP,
        community_board VARCHAR,
        police_precinct VARCHAR,
        borough VARCHAR,
        open_data_channel_type VARCHAR,
        park_facility_name VARCHAR,
        park_borough VARCHAR,
        location_type VARCHAR,
        y_coordinate_state_plane NUMERIC,
        intersection_street_1 VARCHAR,
        intersection_street_2 VARCHAR,
        landmark VARCHAR,
        council_district VARCHAR,
        bbl VARCHAR,
        x_coordinate_state_plane NUMERIC,
        latitude NUMERIC,
        longitude NUMERIC,
        location VARCHAR,
        vehicle_type VARCHAR,
        descriptor_2 VARCHAR,
        bridge_highway_name VARCHAR,
        bridge_highway_segment VARCHAR,
        road_ramp VARCHAR,
        bridge_highway_direction VARCHAR,
        taxi_company_borough VARCHAR,
        taxi_pick_up_location VARCHAR,
        due_date TIMESTAMP,
        loaded_at TIMESTAMP DEFAULT NOW(),
        silver_load INTEGER REFERENCES silver.load_log(run_id)
    )'''
    cursor.execute(create_silver)
    conn.commit()

def silver_load():
    dict_cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    last_processed = '''
    SELECT last_bronze_load_id
    FROM silver.load_log
    ORDER BY loaded_at DESC
    LIMIT 1
    '''
    dict_cursor.execute(last_processed)
    result = dict_cursor.fetchone()
    last_bronze_load_id = result['last_bronze_load_id'] if result else 0

    # Grabbing the data from bronze to be passed into silver
    dict_cursor.execute(
    '''
    SELECT *
    FROM bronze."311" 
    JOIN bronze.load_log log
    ON log.load_id = "311".load_id
    WHERE "311".load_id > %s
    ''', (last_bronze_load_id,))
    silver_data = dict_cursor.fetchall()

    rows = [
        (
            row.get('unique_key'),  # str
            datetime.strptime(row.get('created_date'), '%Y-%m-%dT%H:%M:%S.%f') if row.get('created_date') else None,  # datetime
            datetime.strptime(row.get('closed_date'), '%Y-%m-%dT%H:%M:%S.%f') if row.get('closed_date') else None,  # datetime
            row.get('agency'),  # str
            row.get('agency_name'),  # str
            row.get('complaint_type'),  # str
            row.get('descriptor'),  # str
            row.get('incident_zip'),  # str
            row.get('incident_address'),  # str
            row.get('street_name'),  # str
            row.get('cross_street_1'),  # str
            row.get('cross_street_2'),  # str
            row.get('address_type'),  # str
            row.get('city'),  # str
            row.get('facility_type'),  # str
            row.get('status'),  # str
            row.get('resolution_description'),  # str
            datetime.strptime(row.get('resolution_action_updated_date'), '%Y-%m-%dT%H:%M:%S.%f') if row.get('resolution_action_updated_date') else None,  # datetime
            row.get('community_board'),  # str
            row.get('police_precinct'),  # str
            row.get('borough'),  # str
            row.get('open_data_channel_type'),  # str
            row.get('park_facility_name'),  # str
            row.get('park_borough'),  # str
            row.get('location_type'),  # str
            float(row.get('y_coordinate_state_plane')) if row.get('y_coordinate_state_plane') else None,  # float
            row.get('intersection_street_1'),  # str
            row.get('intersection_street_2'),  # str
            row.get('landmark'),  # str
            row.get('council_district'),  # str
            row.get('bbl'),  # str
            float(row.get('x_coordinate_state_plane')) if row.get('x_coordinate_state_plane') else None,  # float
            float(row.get('latitude')) if row.get('latitude') else None,  # float
            float(row.get('longitude')) if row.get('longitude') else None,  # float
            str(row.get('location')) if row.get('location') else None,  # str
            row.get('vehicle_type'),  # str
            row.get('descriptor_2'),  # str
            row.get('bridge_highway_name'),  # str
            row.get('bridge_highway_segment'),  # str
            row.get('road_ramp'),  # str
            row.get('bridge_highway_direction'),  # str
            row.get('taxi_company_borough'),  # str
            row.get('taxi_pick_up_location'),  # str
            datetime.strptime(row.get('due_date'), '%Y-%m-%dT%H:%M:%S.%f') if row.get('due_date') else None, # datetime
        )
        for row in silver_data
    ]
    unique_keys = [row[0] for row in rows] #getting all the unique_keys in the current data load

    insert = '''
    INSERT INTO silver."311" (
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
    ON CONFLICT (unique_key) DO UPDATE SET
        status = EXCLUDED.status,
        closed_date = EXCLUDED.closed_date,
        resolution_description = EXCLUDED.resolution_description,
        resolution_action_updated_date = EXCLUDED.resolution_action_updated_date,
        due_date = EXCLUDED.due_date
    '''
    execute_values(dict_cursor, insert, rows)
    conn.commit()
    
    if silver_data:
        last_bronze_load_id = max(row['load_id'] for row in silver_data)

        dict_cursor.execute('INSERT INTO silver.load_log (last_bronze_load_id) VALUES (%s) RETURNING run_id', (last_bronze_load_id,))
        silver_run_id = dict_cursor.fetchone()['run_id']
        dict_cursor.execute('UPDATE silver."311" SET silver_load = %s WHERE unique_key = ANY(%s)', (silver_run_id, unique_keys))
        conn.commit()
