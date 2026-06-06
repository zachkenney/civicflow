from extract import *
from load import *
import schedule
import time
from db import connect, conn

def run():
    cursor = connect()
    setup(cursor)
    data = getData(cursor)
    load(cursor,data)

schedule.every(24).hours.do(run)

run()

while True:
    schedule.run_pending()
    time.sleep(1)


