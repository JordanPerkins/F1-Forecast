import os
import mysql.connector as mysql
import logging
import sys

SQL_USER = os.getenv('MYSQL_USER')
SQL_PASSWORD = os.getenv('MYSQL_PASSWORD')
SQL_HOST = os.getenv('MYSQL_HOST')
SQL_DATABASE = os.getenv('MYSQL_DB')

class Database:
    # Here will be the instance stored.
    __instance = None

    @staticmethod
    def get_database():
        """ Static access method. """
        if Database.__instance == None:
            Database()
        return Database.__instance

    def connect(self):
        try:
            connection = mysql.connection.MySQLConnection(user=SQL_USER, password=SQL_PASSWORD, host=SQL_HOST, database=SQL_DATABASE)
            self.db = connection
            logging.debug("Successfully opened MySQL connection");
        except mysql.Error as err:
            logging.error('Could not connect to database: '+str(err))
            sys.exit()

    def query(self, *args):
        try:
            cursor = self.db.cursor()
            cursor.execute(*args)
        except mysql.errors.OperationalError as err:
            logging.debug("Reconnecting to MySQL as connection lost");
            self.connect()
            cursor = self.db.cursor()
            cursor.execute(*args)
        return cursor

    def __init__(self):
        if Database.__instance == None:
            self.connect()
            Database.__instance = self

    def __list_query(self, items):
        return ','.join(['%s'] * len(items))

    def get_race_list(self):
        cursor = self.query("SELECT DISTINCT REPLACE(LOWER(name), ' grand prix', '') FROM races ORDER BY raceId;")
        result = cursor.fetchall()
        return [item[0] for item in result]

    def get_next_race_id(self):
        cursor = self.query("SELECT MAX(raceId)+1 FROM results;")
        return cursor.fetchone()[0]

    def get_next_qualifying_race_id(self):
        cursor = self.query("SELECT MAX(raceId)+1 FROM qualifying;")
        return cursor.fetchone()[0]

    def get_race_by_id(self, id):
        cursor = self.query("SELECT REPLACE(LOWER(name), ' grand prix', ''), year FROM races WHERE raceId = %s;", (id,))
        return cursor.fetchone()

    def get_drivers_in_race(self, id):
        cursor = self.query("SELECT drivers.* FROM results INNER JOIN drivers ON results.driverId=drivers.driverId WHERE results.raceId=%s;", (id,))
        return cursor.fetchall()

    def get_qualifying_results_with_driver(self, id):
        cursor = self.query("SELECT drivers.*, qualifying.position, NULLIF((LEAST(IFNULL(qualifying.q1Seconds, ~0), IFNULL(qualifying.q2Seconds, ~0), IFNULL(qualifying.q3Seconds, ~0))), ~0)-((SELECT MIN(LEAST(IFNULL(qualifying1.q1Seconds, ~0), IFNULL(qualifying1.q2Seconds, ~0), IFNULL(qualifying1.q3Seconds, ~0))) FROM qualifying qualifying1 WHERE qualifying1.raceId = qualifying.raceId)) FROM qualifying INNER JOIN drivers ON qualifying.driverId=drivers.driverId WHERE raceId=%s;", (id,))
        return cursor.fetchall()

    def get_qualifying_fastest_lap(self, id):
        cursor = self.query("SELECT MIN(LEAST(IFNULL(q1Seconds, ~0), IFNULL(q2Seconds, ~0), IFNULL(q3Seconds, ~0))) FROM qualifying WHERE raceId = %s;", (id,))
        return cursor.fetchone()[0]

    def get_previous_year_race_by_id(self, id):
        cursor = self.query("SELECT races1.raceId FROM races INNER JOIN races races1 ON races1.year=races.year-1 AND races1.circuitId=races.circuitId WHERE races.raceId = %s;", (id,))
        result = cursor.fetchone()
        return result if result is None else result[0]

    def get_qualifying_driver_replacements(self, driver_ids_present, previous_race_id, driver_ids_missing, current_race_id):
        query = ("""
            SELECT qualifying.driverId, qualifying1.driverId FROM qualifying
            INNER JOIN qualifying qualifying1 ON qualifying.constructorId=qualifying1.constructorId
            AND qualifying1.raceId=%s
            AND qualifying1.driverId NOT IN (""" + self.__list_query(driver_ids_present) + """)
            WHERE qualifying.driverId IN (""" + self.__list_query(driver_ids_missing) + """)
            AND qualifying.raceId = %s;""")
        cursor = self.query(query, (previous_race_id,) + tuple(driver_ids_present) + tuple(driver_ids_missing) + (current_race_id,))
        return cursor.fetchall()

    def get_all_laps_prior_to_race(self, id):
        cursor = self.query("SELECT qualifying.driverId,races1.circuitId,COALESCE(NULLIF(qualifying.q3, ''), NULLIF(qualifying.q2, ''), NULLIF(qualifying.q1, '')) FROM races INNER JOIN races races1 ON races1.year=races.year INNER JOIN qualifying ON qualifying.raceId=races1.raceId  WHERE races.raceId = %s AND races1.raceId<races.raceId;", (id,))
        return cursor.fetchall()

    def get_laps_in_prior_season_to_race(self, id):
        cursor = self.query("SELECT CONCAT(qualifying.driverId,races1.circuitId),COALESCE(NULLIF(qualifying.q3, ''), NULLIF(qualifying.q2, ''), NULLIF(qualifying.q1, '')) FROM races INNER JOIN races races1 ON races1.year=races.year-1 INNER JOIN qualifying ON qualifying.raceId=races1.raceId  WHERE races.raceId = %s;", (id,))
        return cursor.fetchall()

    def get_next_race_year_round(self):
        cursor = self.query("SELECT races.year, races.round, races.raceId, races.date FROM results INNER JOIN races ON results.raceId+1=races.raceId ORDER by results.raceId DESC LIMIT 1;")
        return cursor.fetchone()

    def get_next_race_year_round_qualifying(self):
        cursor = self.query("SELECT races.year, races.round, races.raceId, races.date FROM qualifying INNER JOIN races ON qualifying.raceId+1=races.raceId ORDER by qualifying.raceId DESC LIMIT 1;")
        return cursor.fetchone()

    def get_driver_references(self):
        cursor = self.query("SELECT driverRef, driverId FROM drivers;")
        return cursor.fetchall()

    def get_constructor_references(self):
        cursor = self.query("SELECT constructorRef, constructorId FROM constructors;")
        return cursor.fetchall()

    def insert_driver(self, driver_ref, number, code, forename, surname, dob, nationality, url):
        cursor = self.query("INSERT INTO drivers "
             "(driverRef, number, code, forename, surname, dob, nationality, url) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", (driver_ref, number, code, forename, surname, dob, nationality, url))
        return cursor.lastrowid

    def insert_constructor(self, constructor_ref, name, nationality, url):
        cursor = self.query("INSERT INTO constructors "
             "(constructorRef, name, nationality, url) "
            "VALUES (%s, %s, %s, %s)", (constructor_ref, name, nationality, url))
        return cursor.lastrowid

    def insert_result(
        self,
        race_id, driver_id, constructor_id, number, grid, position, position_text, position_order, points, laps, time,
        milliseconds, fastest_lap, rank, fastest_lap_ime, fastest_lap_speed, status_id
    ):
        cursor = self.query("INSERT INTO results "
             "(raceId, driverId, constructorId, number, grid, position, positionText, positionOrder, points, laps, time, "
             "milliseconds, fastestLap, rank, fastestLapTime, fastestLapSpeed, statusId) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
            (race_id, driver_id, constructor_id, number, grid, position, position_text, position_order, points, laps, time,
            milliseconds, fastest_lap, rank, fastest_lap_time, fastest_lap_speed, status_id)
        )
        return cursor.rowcount

    def insert_qualifying(self, race_id, driver_id, constructor_id, number, position, q1, q2, q3, q1Seconds, q2Seconds, q3Seconds):
        cursor = self.query("INSERT INTO qualifying "
             "(raceId, driverId, constructorId, number, position, q1, q2, q3, q1Seconds, q2Seconds, q3Seconds) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (race_id, driver_id, constructor_id, number, position, q1, q2, q3, q1Seconds, q2Seconds, q3Seconds))
        return cursor.rowcount

    def get_next_missing_season(self):
        cursor = self.query("SELECT MAX(year)+1 FROM races;")
        return cursor.fetchone()[0]

    def get_circuit_references(self):
        cursor = self.query("SELECT circuitRef, circuitId FROM circuits;")
        return cursor.fetchall()

    def insert_circuit(self, circuit_ref, circuit_name, locality, country, lat, lng, url):
        cursor = self.query("INSERT INTO circuits "
             "(circuitRef, name, location, country, lat, lng, url) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s)", (circuit_ref, circuit_name, locality, country, lat, lng, url))
        return cursor.lastrowid

    def insert_race(self, year, round_num, circuitId, name, date, time, url):
        cursor = self.query("INSERT INTO races "
             "(year, round, circuitId, name, date, time, url) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s)", (year, round_num, circuitId, name, date, time, url))
        return cursor.rowcount

    def delete_race(self, race_id):
        cursor = self.query("DELETE FROM races WHERE raceId = %s", (race_id,))
        return cursor.rowcount

    def mark_races_as_in_progress(self):
        cursor = self.query("UPDATE races SET raceTrained = FALSE WHERE raceTrained IS NULL AND evaluationRace IS NOT TRUE;")
        return cursor.rowcount

    def get_race_dataset(self):
        query = ("SELECT REPLACE(LOWER(races.name), ' grand prix', ''), results.grid, "
            "NULLIF((LEAST(IFNULL(qualifying.q1Seconds, ~0), IFNULL(qualifying.q2Seconds, ~0), IFNULL(qualifying.q3Seconds, ~0))), ~0)"
            "-((SELECT MIN(LEAST(IFNULL(qualifying1.q1Seconds, ~0), IFNULL(qualifying1.q2Seconds, ~0), IFNULL(qualifying1.q3Seconds, ~0))) "
            "FROM qualifying qualifying1 WHERE qualifying1.raceId = qualifying.raceId)), results.position FROM races "
            "INNER JOIN results ON results.raceId=races.raceId INNER JOIN qualifying ON qualifying.raceId=results.raceId AND qualifying.driverId=results.driverId "
            "WHERE raceTrained is FALSE AND evaluationRace is not TRUE AND results.position IS NOT NULL AND results.position <= 20;")
        cursor = self.query(query)
        return cursor.fetchall()

    def mark_races_as_complete(self):
        cursor = self.query("UPDATE races SET raceTrained = TRUE WHERE raceTrained IS FALSE AND evaluationRace IS NOT TRUE;")
        return cursor.rowcount

    def get_calendar(self, year):
        cursor = self.query("SELECT races.name, races.date, races.time, races.round, circuits.name, circuits.circuitRef, circuits.location, circuits.country FROM races INNER JOIN circuits ON circuits.circuitId = races.circuitId WHERE year = %s ORDER BY races.round ASC;", (year,))
        return cursor.fetchall()

    def get_last_race_id(self):
        cursor = self.query("SELECT MAX(raceId) FROM results;")
        return cursor.fetchone()[0]

    def get_last_race_id_in_year(self, year):
        cursor = self.query("SELECT MAX(results.raceId) FROM results INNER JOIN races ON races.raceId=results.raceId WHERE races.year = %s;", (year,))
        return cursor.fetchone()[0]

    def get_drivers_standings(self, race):
        cursor = self.query("SELECT drivers.*, driverStandings.points, driverStandings.wins, driverStandings.position FROM driverStandings INNER JOIN drivers ON drivers.driverId=driverStandings.driverId WHERE raceId = %s ORDER BY position ASC;", (race,))
        return cursor.fetchall()

    def get_constructors_standings(self, race):
        cursor = self.query("SELECT constructors.constructorId, constructors.constructorRef, constructors.name, constructors.nationality, constructors.url, constructorStandings.points, constructorStandings.wins, constructorStandings.position FROM constructorStandings INNER JOIN constructors ON constructors.constructorId=constructorStandings.constructorId WHERE raceId = %s ORDER BY position ASC;", (race,))
        return cursor.fetchall()
