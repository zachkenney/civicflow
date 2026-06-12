import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv
import os
from db import connect, conn

def silver_setup(cursor):
    create_silver_log = '''
    CREATE TABLE IF NOT EXISTS silver.load_log (
    run_id SERIAL PRIMARY KEY,
    bronze_load_id INTEGER REFERENCES bronze.load_log(load_id),
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
        loaded_at TIMESTAMP DEFAULT NOW()
    )'''
    cursor.execute(create_silver)
    conn.commit()

def silver_load():
    dict_cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    last_processed = '''
    SELECT bronze_load_id
    FROM silver.load_log
    ORDER BY loaded_at DESC
    LIMIT 1
    '''
    dict_cursor.execute(last_processed)
    result = dict_cursor.fetchone()
    last_bronze_load_id = result['bronze_load_id'] if result else 0

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
        for row in silver_data
    ]

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

    dict_cursor.execute('INSERT INTO silver.load_log ')
    # need to finish this. insert bronze_load_id into load_log