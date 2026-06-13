from extract import *
from load import *
from transform_silver import *
from transform_gold import *
import schedule
import time
from db import connect, conn

def run():
    cursor = connect()
    setup(cursor)
    for batch in getData(cursor):
        load(cursor, batch)
    silver_setup(cursor)
    silver_load()
    gold_setup(cursor)
    populate_dim_date(cursor)
    gold_load()

schedule.every(24).hours.do(run)

run()

while True:
    schedule.run_pending()
    time.sleep(1)


