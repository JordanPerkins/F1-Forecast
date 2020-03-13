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

    def get_race_by_id(self, id):
        cursor = self.db.cursor()
        query = ("SELECT REPLACE(LOWER(name), ' grand prix', ''), year FROM races WHERE raceId = %s;")
        cursor.execute(query, (id,))
        return cursor.fetchone()

    def get_drivers_in_race(self, id):
        cursor = self.db.cursor()
        query =  ("SELECT drivers.* FROM results INNER JOIN drivers ON results.driverId=drivers.driverId WHERE results.raceId=%s;")
        cursor.execute(query, (id,))
        return cursor.fetchall()

    def get_qualifying_results_with_driver(self, id):
        cursor = self.db.cursor()
        query = ("SELECT drivers.*, qualifying.position, NULLIF((LEAST(IFNULL(qualifying.q1Seconds, ~0), IFNULL(qualifying.q2Seconds, ~0), IFNULL(qualifying.q3Seconds, ~0))), ~0)-((SELECT MIN(LEAST(IFNULL(qualifying1.q1Seconds, ~0), IFNULL(qualifying1.q2Seconds, ~0), IFNULL(qualifying1.q3Seconds, ~0))) FROM qualifying qualifying1 WHERE qualifying1.raceId = qualifying.raceId)) FROM qualifying INNER JOIN drivers ON qualifying.driverId=drivers.driverId WHERE raceId=%s;")
        cursor.execute(query, (id,))
        return cursor.fetchall()

    def get_qualifying_fastest_lap(self, id):
        cursor = self.db.cursor()
        query = ("SELECT MIN(LEAST(IFNULL(q1Seconds, ~0), IFNULL(q2Seconds, ~0), IFNULL(q3Seconds, ~0))) FROM qualifying WHERE raceId = %s;")
        cursor.execute(query, (id,))
        return cursor.fetchone()[0]

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

    def get_next_race_year_round(self):
        cursor = self.db.cursor()
        query = ("SELECT races.year, races.round, races.raceId, races.date FROM results INNER JOIN races ON results.raceId+1=races.raceId ORDER by results.raceId DESC LIMIT 1;")
        cursor.execute(query)
        return cursor.fetchone()

    def get_next_race_year_round_qualifying(self):
        cursor = self.db.cursor()
        query = ("SELECT races.year, races.round, races.raceId, races.date FROM qualifying INNER JOIN races ON qualifying.raceId+1=races.raceId ORDER by qualifying.raceId DESC LIMIT 1;")
        cursor.execute(query)
        return cursor.fetchone()

    def get_driver_references(self):
        cursor = self.db.cursor()
        query = ("SELECT driverRef, driverId FROM drivers;")
        cursor.execute(query)
        return cursor.fetchall()

    def get_constructor_references(self):
        cursor = self.db.cursor()
        query = ("SELECT constructorRef, constructorId FROM constructors;")
        cursor.execute(query)
        return cursor.fetchall()

    def insert_driver(self, driver_ref, number, code, forename, surname, dob, nationality, url):
        cursor = self.db.cursor()
        query = ("INSERT INTO drivers "
             "(driverRef, number, code, forename, surname, dob, nationality, url) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)")
        cursor.execute(query, (driver_ref, number, code, forename, surname, dob, nationality, url))
        return cursor.lastrowid

    def insert_constructor(self, constructor_ref, name, nationality, url):
        cursor = self.db.cursor()
        query = ("INSERT INTO constructors "
             "(constructorRef, name, nationality, url) "
            "VALUES (%s, %s, %s, %s)")
        cursor.execute(query, (constructor_ref, name, nationality, url))
        return cursor.lastrowid

    def insert_result(
        self,
        race_id, driver_id, constructor_id, number, grid, position, position_text, position_order, points, laps, time,
        milliseconds, fastest_lap, rank, fastest_lap_ime, fastest_lap_speed, status_id
    ):
        cursor = self.db.cursor()
        query = ("INSERT INTO results "
             "(raceId, driverId, constructorId, number, grid, position, positionText, positionOrder, points, laps, time, "
             "milliseconds, fastestLap, rank, fastestLapTime, fastestLapSpeed, statusId) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")
        cursor.execute(query,
            (race_id, driver_id, constructor_id, number, grid, position, position_text, position_order, points, laps, time,
            milliseconds, fastest_lap, rank, fastest_lap_time, fastest_lap_speed, status_id)
        )
        return cursor.rowcount

    def insert_qualifying(self, race_id, driver_id, constructor_id, number, position, q1, q2, q3, q1Seconds, q2Seconds, q3Seconds):
        cursor = self.db.cursor()
        query = ("INSERT INTO qualifying "
             "(raceId, driverId, constructorId, number, position, q1, q2, q3, q1Seconds, q2Seconds, q3Seconds) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")
        cursor.execute(query, (race_id, driver_id, constructor_id, number, position, q1, q2, q3, q1Seconds, q2Seconds, q3Seconds))
        return cursor.rowcount

    def get_next_missing_season(self):
        cursor = self.db.cursor()
        query = ("SELECT MAX(year)+1 FROM races;")
        cursor.execute(query)
        return cursor.fetchone()[0]

    def get_circuit_references(self):
        cursor = self.db.cursor()
        query = ("SELECT circuitRef, circuitId FROM circuits;")
        cursor.execute(query)
        return cursor.fetchall()

    def insert_circuit(self, circuit_ref, circuit_name, locality, country, lat, lng, url):
        cursor = self.db.cursor()
        query = ("INSERT INTO circuits "
             "(circuitRef, name, location, country, lat, lng, url) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s)")
        cursor.execute(query, (circuit_ref, circuit_name, locality, country, lat, lng, url))
        return cursor.lastrowid

    def insert_race(self, year, round_num, circuitId, name, date, time, url):
        cursor = self.db.cursor()
        query = ("INSERT INTO races "
             "(year, round, circuitId, name, date, time, url) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s)")
        cursor.execute(query, (year, round_num, circuitId, name, date, time, url))
        return cursor.rowcount

    def delete_race(self, race_id):
        cursor = self.db.cursor()
        query = ("DELETE FROM races WHERE raceId = %s")
        cursor.execute(query, (race_id,))
        return cursor.rowcount

    def mark_races_as_in_progress(self):
        cursor = self.db.cursor()
        query = ("UPDATE races SET raceTrained = FALSE WHERE raceTrained IS NULL AND evaluationRace IS NOT TRUE;")
        cursor.execute(query)
        return cursor.rowcount

    def get_race_dataset(self):
        cursor = self.db.cursor()
        query = ("SELECT REPLACE(LOWER(races.name), ' grand prix', ''), results.grid, "
            "NULLIF((LEAST(IFNULL(qualifying.q1Seconds, ~0), IFNULL(qualifying.q2Seconds, ~0), IFNULL(qualifying.q3Seconds, ~0))), ~0)"
            "-((SELECT MIN(LEAST(IFNULL(qualifying1.q1Seconds, ~0), IFNULL(qualifying1.q2Seconds, ~0), IFNULL(qualifying1.q3Seconds, ~0))) "
            "FROM qualifying qualifying1 WHERE qualifying1.raceId = qualifying.raceId)), results.position FROM races "
            "INNER JOIN results ON results.raceId=races.raceId INNER JOIN qualifying ON qualifying.raceId=results.raceId AND qualifying.driverId=results.driverId "
            "WHERE raceTrained is FALSE AND evaluationRace is not TRUE AND results.position IS NOT NULL AND results.position <= 20;")
        cursor.execute(query)
        return cursor.fetchall()

    def mark_races_as_complete(self):
        cursor = self.db.cursor()
        query = ("UPDATE races SET raceTrained = TRUE WHERE raceTrained IS FALSE AND evaluationRace IS NOT TRUE;")
        cursor.execute(query)
        return cursor.rowcount

    def __init__(self):
        if Database.__instance == None:
            self.db = connect()
            Database.__instance = self
