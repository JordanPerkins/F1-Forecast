import os
import mysql.connector as mysql
import logging
import sys

SQL_USER = os.getenv('MYSQL_USER')
SQL_PASSWORD = os.getenv('MYSQL_PASSWORD')
SQL_HOST = os.getenv('MYSQL_HOST')
SQL_DATABASE = os.getenv('MYSQL_DB')

def connect():
    try:
        return mysql.connection.MySQLConnection(user=SQL_USER, password=SQL_PASSWORD, host=SQL_HOST, database=SQL_DATABASE)
    except mysql.Error as err:
        logging.error('Could not connect to database: '+str(err))
        sys.exit()

class Database:
    # Here will be the instance stored.
    __instance = None

    @staticmethod
    def get_database():
        """ Static access method. """
        if Database.__instance == None:
            Database()
        return Database.__instance

    def get_race_list(self):
        cursor = self.db.cursor()
        query = ("SELECT DISTINCT REPLACE(LOWER(name), ' grand prix', '') FROM races ORDER BY raceId;")
        cursor.execute(query)
        result = cursor.fetchall()
        return [item[0] for item in result]

    def get_next_race_id(self):
        cursor = self.db.cursor()
        query = ("SELECT MAX(raceId)+1 FROM results;")
        cursor.execute(query)
        return cursor.fetchone()[0]

    def get_race_name(self, id):
        cursor = self.db.cursor()
        query = ("SELECT REPLACE(LOWER(name), ' grand prix', '') FROM races WHERE raceId = %s;")
        cursor.execute(query, (id,))
        return cursor.fetchone()[0]

    def get_drivers_in_race(self, id):
        cursor = self.db.cursor()
        query =  ("SELECT drivers.* FROM results INNER JOIN drivers ON results.driverId=drivers.driverId WHERE results.raceId=%s ORDER BY results.driverId;")
        cursor.execute(query, (id,))
        return cursor.fetchall()

    def get_qualifying_results(self, id):
        cursor = self.db.cursor()
        query = ("SELECT COALESCE(NULLIF(q3, ''), NULLIF(q2, ''), NULLIF(q1, '')) FROM qualifying WHERE raceId=%s ORDER BY driverId;")
        cursor.execute(query, (id,))
        result = cursor.fetchall()
        return [item[0] for item in result]


    def __init__(self):
        if Database.__instance == None:
            self.db = connect()
            Database.__instance = self
