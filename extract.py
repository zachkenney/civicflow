# Extracting data from API
import requests
import json
import psycopg2

def getData(cursor):
    cursor.execute('SELECT MAX(loaded_at) FROM bronze.load_log')
    last_load = cursor.fetchone()[0]
    offset = 0
    limit = 10000
    total = 0
    url = 'https://data.cityofnewyork.us/resource/erm2-nwe9.json'
    params = {
        '$limit': limit,
        '$offset': offset,
        '$order': 'created_date DESC'
    }
    if last_load:
        params['$where'] = f"created_date > '{last_load.strftime('%Y-%m-%dT%H:%M:%S')}' or resolution_action_updated_date > '{last_load.strftime('%Y-%m-%dT%H:%M:%S')}'"
    else:
        params['$where'] = "created_date > '2026-06-T00:00:00'"

    while True:
        params['$offset'] = offset
        response = requests.get(url, params=params)
        response.raise_for_status()
        batch = response.json()
        total += len(batch)
        yield batch # trying to reduce large amounts of rows sitting in memory so using a generator

        if len(batch) < limit:
            break

        offset += limit # pagination. grab the limit amount, add to the offset

    print(f'Fetched {total} total records.')

