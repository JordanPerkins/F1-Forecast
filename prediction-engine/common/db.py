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

    def __list_query(self, items):
        return ','.join(['%s'] * len(items))

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

    def get_next_qualifying_race_id(self):
        cursor = self.db.cursor()
        query = ("SELECT MAX(raceId)+1 FROM qualifying;")
        cursor.execute(query)
        return cursor.fetchone()[0]

    def get_race_name(self, id):
        cursor = self.db.cursor()
        query = ("SELECT REPLACE(LOWER(name), ' grand prix', '') FROM races WHERE raceId = %s;")
        cursor.execute(query, (id,))
        return cursor.fetchone()[0]

    def get_drivers_in_race(self, id):
        cursor = self.db.cursor()
        query =  ("SELECT drivers.* FROM results INNER JOIN drivers ON results.driverId=drivers.driverId WHERE results.raceId=%s;")
        cursor.execute(query, (id,))
        return cursor.fetchall()

    def get_qualifying_results_with_driver(self, id):
        cursor = self.db.cursor()
        query = ("SELECT drivers.*, COALESCE(NULLIF(qualifying.q3, ''), NULLIF(qualifying.q2, ''), NULLIF(qualifying.q1, '')) FROM qualifying INNER JOIN drivers ON qualifying.driverId=drivers.driverId WHERE raceId=%s;")
        cursor.execute(query, (id,))
        return cursor.fetchall()

    def get_previous_year_race_by_id(self, id):
        cursor = self.db.cursor()
        query = ("SELECT races1.raceId FROM races INNER JOIN races races1 ON races1.year=races.year-1 AND races1.circuitId=races.circuitId WHERE races.raceId = %s;")
        cursor.execute(query, (id,))
        result = cursor.fetchone()
        return result if result is None else result[0]

    def get_qualifying_driver_replacements(self, driver_ids_present, previous_race_id, driver_ids_missing, current_race_id):
        cursor = self.db.cursor()
        query = ("""
            SELECT qualifying.driverId, qualifying1.driverId FROM qualifying
            INNER JOIN qualifying qualifying1 ON qualifying.constructorId=qualifying1.constructorId
            AND qualifying1.raceId=%s
            AND qualifying1.driverId NOT IN (""" + self.__list_query(driver_ids_present) + """)
            WHERE qualifying.driverId IN (""" + self.__list_query(driver_ids_missing) + """)
            AND qualifying.raceId = %s;""")
        cursor.execute(query, (previous_race_id,) + tuple(driver_ids_present) + tuple(driver_ids_missing) + (current_race_id,))
        return cursor.fetchall()

    def get_all_laps_prior_to_race(self, id):
        cursor = self.db.cursor()
        query = ("SELECT qualifying.driverId,races1.circuitId,COALESCE(NULLIF(qualifying.q3, ''), NULLIF(qualifying.q2, ''), NULLIF(qualifying.q1, '')) FROM races INNER JOIN races races1 ON races1.year=races.year INNER JOIN qualifying ON qualifying.raceId=races1.raceId  WHERE races.raceId = %s AND races1.raceId<races.raceId;")
        cursor.execute(query, (id,))
        return cursor.fetchall()

    def get_laps_in_prior_season_to_race(self, id):
        cursor = self.db.cursor()
        query = ("SELECT CONCAT(qualifying.driverId,races1.circuitId),COALESCE(NULLIF(qualifying.q3, ''), NULLIF(qualifying.q2, ''), NULLIF(qualifying.q1, '')) FROM races INNER JOIN races races1 ON races1.year=races.year-1 INNER JOIN qualifying ON qualifying.raceId=races1.raceId  WHERE races.raceId = %s;")
        cursor.execute(query, (id,))
        return cursor.fetchall()

    def __init__(self):
        if Database.__instance == None:
            self.db = connect()
            Database.__instance = self
