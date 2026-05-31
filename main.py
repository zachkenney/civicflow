from extract import *
from load import *

cursor = connect()
setup(cursor)
data = getData(cursor)
load(cursor,data)
