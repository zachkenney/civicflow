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
    data = getData(cursor)
    load(cursor,data)
    silver_setup(cursor)
    silver_load()
    gold_setup(cursor)
    gold_load()

schedule.every(24).hours.do(run)

run()

while True:
    schedule.run_pending()
    time.sleep(1)


