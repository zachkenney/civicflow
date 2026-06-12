import psycopg2
from psycopg2.extras import execute_values
from db import connect, conn

def gold_setup(cursor):
    create_gold_log = '''
    CREATE TABLE IF NOT EXISTS gold.load_log (
    run_id SERIAL PRIMARY KEY,
    last_silver_run_id INTEGER REFERENCES silver.load_log(run_id),
    loaded_at TIMESTAMP DEFAULT NOW());
    '''
    cursor.execute(create_gold_log)
    conn.commit()

    create_gold = '''
    CREATE TABLE IF NOT EXISTS gold."311" (
        unique_key VARCHAR PRIMARY KEY,
        created_date TIMESTAMP,
        closed_date TIMESTAMP,
        agency VARCHAR,
        agency_name VARCHAR,
        complaint_type VARCHAR,
        complaint_category VARCHAR,
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
        resolution_category VARCHAR,
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
        gold_load INTEGER REFERENCES gold.load_log(run_id)
    )'''
    cursor.execute(create_gold)
    conn.commit()

# the complaint types are incredibly granular so i think analysis would be aided by having more broad categories
complaint_category_map = {
    # Noise
    'Noise': 'Noise',
    'Noise - Commercial': 'Noise',
    'Noise - Helicopter': 'Noise',
    'Noise - House of Worship': 'Noise',
    'Noise - Park': 'Noise',
    'Noise - Residential': 'Noise',
    'Noise - Street/Sidewalk': 'Noise',
    'Noise - Vehicle': 'Noise',
    'Illegal Fireworks': 'Noise',

    # Vehicles
    'Abandoned Vehicle': 'Vehicles',
    'Blocked Driveway': 'Vehicles',
    'Broken Parking Meter': 'Vehicles',
    'E-Scooter': 'Vehicles',
    'Ferry Complaint': 'Vehicles',
    'For Hire Vehicle Complaint': 'Vehicles',
    'Illegal Parking': 'Vehicles',
    'Municipal Parking Facility': 'Vehicles',
    'Taxi Complaint': 'Vehicles',
    'Taxi Compliment': 'Vehicles',
    'Taxi Report': 'Vehicles',

    # Infrastructure
    'Curb Condition': 'Infrastructure',
    'Highway Condition': 'Infrastructure',
    'Obstruction': 'Infrastructure',
    'Root/Sewer/Sidewalk Condition': 'Infrastructure',
    'Sidewalk Condition': 'Infrastructure',
    'Street Condition': 'Infrastructure',
    'Street Light Condition': 'Infrastructure',
    'Street Sign - Damaged': 'Infrastructure',
    'Street Sign - Dangling': 'Infrastructure',
    'Street Sign - Missing': 'Infrastructure',
    'Traffic': 'Infrastructure',
    'Traffic Signal Condition': 'Infrastructure',

    # Building & Construction
    'Appliance': 'Building & Construction',
    'Asbestos': 'Building & Construction',
    'Best/Site Safety': 'Building & Construction',
    'Boilers': 'Building & Construction',
    'Building/Use': 'Building & Construction',
    'Construction Lead Dust': 'Building & Construction',
    'Door/Window': 'Building & Construction',
    'Electric': 'Building & Construction',
    'Elevator': 'Building & Construction',
    'Flooring/Stairs': 'Building & Construction',
    'General Construction/Plumbing': 'Building & Construction',
    'Heat/Hot Water': 'Building & Construction',
    'Lead': 'Building & Construction',
    'Maintenance or Facility': 'Building & Construction',
    'Outside Building': 'Building & Construction',
    'Paint/Plaster': 'Building & Construction',
    'Plumbing': 'Building & Construction',
    'Scaffold Safety': 'Building & Construction',

    # Sanitation
    'Commercial Disposal Complaint': 'Sanitation',
    'Dead Animal': 'Sanitation',
    'Dirty Condition': 'Sanitation',
    'Dumpster Complaint': 'Sanitation',
    'Graffiti': 'Sanitation',
    'Illegal Dumping': 'Sanitation',
    'Industrial Waste': 'Sanitation',
    'Litter Basket Complaint': 'Sanitation',
    'Litter Basket Request': 'Sanitation',
    'Missed Collection': 'Sanitation',
    'Residential Disposal Complaint': 'Sanitation',
    'Sanitation Worker or Vehicle Complaint': 'Sanitation',

    # Environment
    'Animal in a Park': 'Environment',
    'Beach/Pool/Sauna Complaint': 'Environment',
    'Bike/Roller/Skate': 'Environment',
    'Damaged Tree': 'Environment',
    'Dead/Dying Tree': 'Environment',
    'Illegal Tree Damage': 'Environment',
    'New Tree Request': 'Environment',
    'Outdoor Dining': 'Environment',
    'Overgrown Tree/Branches': 'Environment',
    'Plant': 'Environment',
    'Special Natural Area District (SNAD)': 'Environment',
    'Uprooted Stump': 'Environment',
    'Violation of Park Rules': 'Environment',
    'Wood Pile Remaining': 'Environment',

    # Health & Safety
    'Air Quality': 'Health & Safety',
    'Food Establishment': 'Health & Safety',
    'Food Poisoning': 'Health & Safety',
    'Hazardous Materials': 'Health & Safety',
    'Indoor Air Quality': 'Health & Safety',
    'Indoor Sewage': 'Health & Safety',
    'Rodent': 'Health & Safety',
    'Smoking or Vaping': 'Health & Safety',
    'Standing Water': 'Health & Safety',
    'Unsanitary Animal Pvt Property': 'Health & Safety',
    'Unsanitary Condition': 'Health & Safety',
    'Unsanitary Pigeon Condition': 'Health & Safety',

    # Sewer
    'Sewer': 'Sewer',
    'Water Conservation': 'Sewer',
    'Water Leak': 'Sewer',
    'Water Quality': 'Sewer',
    'Water System': 'Sewer',

    # Public Order
    'Drug Activity': 'Public Order',
    'Drinking': 'Public Order',
    'Emergency Response Team (ERT)': 'Public Order',
    'Encampment': 'Public Order',
    'Homeless Person Assistance': 'Public Order',
    'Illegal Posting': 'Public Order',
    'Investigations and Discipline (IAD)': 'Public Order',
    'Non-Emergency Police Matter': 'Public Order',
    'Panhandling': 'Public Order',
    'Real Time Enforcement': 'Public Order',
    'Safety': 'Public Order',
    'Special Projects Inspection Team (SPIT)': 'Public Order',
    'Urinating in Public': 'Public Order',

    # Animals
    'Animal-Abuse': 'Animals',
    'Illegal Animal Kept as Pet': 'Animals',
    'Pet Sale': 'Animals',
    'Unleashed Dog': 'Animals',

    # Business
    'Cannabis Retailer': 'Business',
    'Consumer Complaint': 'Business',
    'Mobile Food Vendor': 'Business',
    'Vendor Enforcement': 'Business',

    # Bikes
    'Abandoned Bike': 'Bikes',
    'Bike Rack': 'Bikes',

    # Lost & Found
    'Found Property': 'Lost & Found',
    'Lost Property': 'Lost & Found',

    # General
    'General': 'General',
}

# the resolution types are often lengthy as they are the actualy responses given so i will map them to broader categories useful for analysis.
def gold_load():
    dict_cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    last_processed = '''
    SELECT last_silver_run_id
    FROM gold.load_log
    ORDER BY loaded_at DESC
    LIMIT 1
    '''
    dict_cursor.execute(last_processed)
    result = dict_cursor.fetchone()
    last_silver_run_id = result['last_silver_run_id'] if result else 0

    # Grabbing the data from silver to be passed into gold
    dict_cursor.execute(
    '''
    SELECT *
    FROM silver."311"
    JOIN silver.load_log log
    ON log.run_id = "311".silver_load
    WHERE "311".silver_load > %s
    ''', (last_silver_run_id,))
    silver_data = dict_cursor.fetchall()

    rows = [
        (
            row.get('unique_key'),
            row.get('created_date'),
            row.get('closed_date'),
            row.get('agency'),
            row.get('agency_name'),
            row.get('complaint_type'),
            complaint_category_map.get(row.get('complaint_type'), 'Other'),
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
            map_resolution_category(row.get('resolution_description')),
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
            row.get('location'),
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
    unique_keys = [row[0] for row in rows]

    insert = '''
    INSERT INTO gold."311" (
        unique_key, created_date, closed_date, agency, agency_name,
        complaint_type, complaint_category, descriptor, incident_zip, incident_address,
        street_name, cross_street_1, cross_street_2, address_type, city,
        facility_type, status, resolution_category, resolution_action_updated_date,
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
        resolution_category = EXCLUDED.resolution_category,
        complaint_category = EXCLUDED.complaint_category,
        resolution_action_updated_date = EXCLUDED.resolution_action_updated_date,
        due_date = EXCLUDED.due_date
    '''
    execute_values(dict_cursor, insert, rows)
    conn.commit()

    if silver_data:
        last_silver_run_id = max(row['silver_load'] for row in silver_data)

        dict_cursor.execute('INSERT INTO gold.load_log (last_silver_run_id) VALUES (%s) RETURNING run_id', (last_silver_run_id,))
        gold_load_id = dict_cursor.fetchone()['run_id']
        dict_cursor.execute('UPDATE gold."311" SET gold_load = %s WHERE unique_key = ANY(%s)', (gold_load_id, unique_keys))
        conn.commit()


def map_resolution_category(description):
    if not description:
        return None
    d = description.lower()

    if any(x in d for x in ['not able to gain access', 'unable to gain entry', 'unable to complete the inspection', 'could not gain access']):
        return 'No Access'
    if any(x in d for x in ['duplicate', 'previously reported', 'already has a request', 'open service request already exists']):
        return 'Duplicate'
    if any(x in d for x in ['sufficient location', 'enough information', 'not enough', 'sufficient location or complaint']):
        return 'Insufficient Information'
    if any(x in d for x in ['administratively closed', 'devote resources to other critical']):
        return 'Administratively Closed'
    if any(x in d for x in ['outreach', 'mobile outreach response team', 'homeless services']):
        return 'Outreach / Social Services'
    if any(x in d for x in ['summons', 'arrest', 'notice of violation', 'stop work order', 'violation was issued', 'violations were issued', 'oath']):
        return 'Violation Issued'
    if any(x in d for x in ['no violation', 'did not find', 'could not find', 'no condition', 'not find the problem', 'no criminal violation', 'police action was not necessary', 'no evidence of a criminal violation', 'within acceptable parameters', 'no further action was necessary', 'did not violate']):
        return 'No Violation Found'
    if any(x in d for x in ['referred', 'out of jurisdiction', 'forwarded', 'notified the appropriate', 'another agency', 'another entity']):
        return 'Referred to Another Agency'
    if any(x in d for x in ['work order', 'will inspect', 'will visit', 'in progress', 'scheduled for', 'will be addressed', 'will repair', 'will determine', 'assigned to a unit', 'check back later', 'further investigation is required']):
        return 'Pending / In Progress'
    if any(x in d for x in ['corrected', 'repaired', 'cleaned', 'removed', 'resolved', 'collected', 'restored', 'corrected the problem', 'performed the work', 'completed the requested', 'shut the running hydrant', 'work was performed', 'accepted assistance']):
        return 'Resolved'
    return 'Other'