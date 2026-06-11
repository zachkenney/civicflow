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

    last_processed = '''
    SELECT bronze_load_id
    FROM silver.load_log
    ORDER BY loaded_at DESC
    LIMIT 1
    '''
    cursor.execute(last_processed)
    result = cursor.fetchone()
    last_bronze_load_id = result[0] if result else 0

# Grabbing the data from bronze to be passed into silver
    cursor.execute(
    '''
    SELECT *
    FROM bronze."311" 
    JOIN bronze.load_log log
    ON log.load_id = "311".load_id
    WHERE "311".load_id > %s
    ''', (last_bronze_load_id,))
    silver_data = cursor.fetchall()