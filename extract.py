# Extracting data from API
import requests
import json
import psycopg2

def getData(cursor):
    cursor.execute('SELECT MAX(loaded_at) FROM bronze.load_log')
    last_load = cursor.fetchone()[0]
    all_data= []
    offset = 0
    limit = 10000
    url = 'https://data.cityofnewyork.us/resource/erm2-nwe9.json'
    params = {
        '$limit': limit,
        '$offset': offset,
        '$order': 'created_date DESC'    
    }
    if last_load:
        params['$where'] = f"created_date > '{last_load.strftime('%Y-%m-%dT%H:%M:%S')}' or resolution_action_updated_date > '{last_load.strftime('%Y-%m-%dT%H:%M:%S')}'"
    else: 
        params['$where'] = "created_date > '2026-05-25T00:00:00'"

    while True:
        params['$offset'] = offset
        response = requests.get(url, params=params)

        response.raise_for_status()
        batch = response.json()
        all_data.extend(batch)

        if len(batch) < limit:
            break

        offset += limit # Pagination. offset initialized at 0, then increments by 10,000 since this API is rate limited at 10k.

    print(f'Fetched {len(all_data)} total records.') # Log
    return all_data

