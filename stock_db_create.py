import sqlite3

conn = sqlite3.connect("stock_data.db")
c = conn.cursor()

def createTable():
    c.execute("CREATE TABLE positive (Symbol TEXT, MovingAvg REAL)")
    c.execute("CREATE TABLE negative (Symbol TEXT, MovingAvg REAL)")



conn.commit()
