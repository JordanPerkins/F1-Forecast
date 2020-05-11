import os
import unittest
import datetime
import mysql.connector as mysql

from ..update.update_database import check_for_calendar_updates

SQL_USER = os.getenv('MYSQL_USER')
SQL_PASSWORD = os.getenv('MYSQL_PASSWORD')
SQL_HOST = os.getenv('MYSQL_HOST')
SQL_DATABASE = os.getenv('MYSQL_DB')

db = mysql.connection.MySQLConnection(
    user=SQL_USER,
    password=SQL_PASSWORD,
    host=SQL_HOST,
    database=SQL_DATABASE
)
db.autocommit = True

class TestUpdateDatabase(unittest.TestCase):

    def setUp(self):
        truncateTable('races')
        truncateTable('circuits')

    def test_check_for_calendar_updates(self):
        insertInitialData(2018)
        result = check_for_calendar_updates()
        self.assertEqual(result, 21)
        data = getRaceData()
        self.assertEqual(len(data), 21)
        self.assertEqual(data[0], (2, 2019, 1, 2, 'Australian Grand Prix', datetime.date(2019, 3, 17), datetime.timedelta(seconds=18600),
                                   'https://en.wikipedia.org/wiki/2019_Australian_Grand_Prix', None, None, None, 2, 'albert_park',
                                   'Albert Park Grand Prix Circuit', 'Melbourne', 'Australia', -37.8497, 144.968, None,
                                   'http://en.wikipedia.org/wiki/Melbourne_Grand_Prix_Circuit'))
        self.assertEqual(data[1], (3, 2019, 2, 1, 'Bahrain Grand Prix', datetime.date(2019, 3, 31), datetime.timedelta(seconds=54600),
                                   'https://en.wikipedia.org/wiki/2019_Bahrain_Grand_Prix', None, None, None, 1, 'bahrain',
                                   'Bahrain International Circuit', None, None, None, None, None, ''))

    def test_check_for_calendar_updates_with_missing_season(self):
        insertInitialData(2050)
        result = check_for_calendar_updates()
        self.assertEqual(result, 0)
        data = getRaceData()
        self.assertEqual(len(data), 0)

def truncateTable(table):
    cursor = db.cursor()
    cursor.execute("TRUNCATE TABLE "+table+";")
    db.commit()
    cursor.close()

def insertInitialData(year):
    cursor = db.cursor()
    cursor.execute("INSERT INTO races (year, round) VALUES (%s, 1)", (year,))
    db.commit()
    cursor.close()

    cursor = db.cursor()
    cursor.execute("INSERT INTO circuits (circuitRef, name) VALUES ('bahrain', 'Bahrain International Circuit')")
    db.commit()
    cursor.close()

def getRaceData():
    cursor = db.cursor()
    cursor.execute("SELECT * FROM races INNER JOIN circuits ON circuits.circuitId=races.circuitId;")
    result = cursor.fetchall()
    cursor.close()
    return result

if __name__ == '__main__':
    unittest.main()