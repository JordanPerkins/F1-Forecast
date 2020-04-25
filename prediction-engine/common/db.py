""" Contain the MySQL database class """
import os
import logging
import sys
import mysql.connector as mysql

SQL_USER = os.getenv('MYSQL_USER')
SQL_PASSWORD = os.getenv('MYSQL_PASSWORD')
SQL_HOST = os.getenv('MYSQL_HOST')
SQL_DATABASE = os.getenv('MYSQL_DB')

def create_list_query(items):
    """ Creates a query string for a long list of items. """
    return ','.join(['%s'] * len(items))

class Database:
    """ Singleton class for managing DB and queries. """
    # Here will be the instance stored.
    __instance = None

    @staticmethod
    def get_database():
        """ Return existing database method if it exists """
        if Database.__instance is None:
            Database()
        return Database.__instance

    def connect(self):
        """ Attempts to open a connection to the database """
        try:
            self.database = mysql.connection.MySQLConnection(
                user=SQL_USER,
                password=SQL_PASSWORD,
                host=SQL_HOST,
                database=SQL_DATABASE
            )
            logging.debug("Successfully opened MySQL connection")
        except mysql.Error as err:
            logging.error("Could not connect to database: %s", str(err))
            sys.exit()

    def query(self, *args):
        """ Attempts to query database, reopening the connection
            if it has dropped for any reason. """
        try:
            cursor = self.database.cursor()
            cursor.execute(*args)
        except mysql.errors.OperationalError:
            logging.debug("Reconnecting to MySQL as connection lost")
            self.connect()
            cursor = self.database.cursor()
            cursor.execute(*args)
        return cursor

    def __init__(self):
        """ Constructor, opening a connection and setting instance. """
        if Database.__instance is None:
            self.connect()
            Database.__instance = self

    def get_race_list(self):
        """ Gets full list of races for use in the model. """
        cursor = self.query(
            "SELECT DISTINCT REPLACE(LOWER(name), ' grand prix', '') FROM races ORDER BY raceId;"
        )
        result = cursor.fetchall()
        return [item[0] for item in result]

    def get_race_by_id(self, race_id):
        """ Gets the name of a race using the ID. """
        cursor = self.query(
            "SELECT REPLACE(LOWER(name), ' grand prix', ''), year FROM races WHERE raceId = %s;",
            (race_id,)
        )
        return cursor.fetchone()

    def get_drivers_in_race(self, race_id):
        """ Gets the info of a driver that participated in a given race. """
        cursor = self.query(
            """
                SELECT drivers.*
                FROM results
                INNER JOIN drivers ON results.driverId=drivers.driverId
                WHERE results.raceId=%s;""",
            (race_id,)
        )
        return cursor.fetchall()

    def get_qualifying_results_with_driver(self, race_id):
        """ Gets driver info as well as qualifying delta result for given race. """
        cursor = self.query(
            """
                SELECT
                    drivers.*,
                    constructors.constructorRef,
                    qualifying.position,
                    NULLIF((LEAST(IFNULL(qualifying.q1Seconds, ~0),
                        IFNULL(qualifying.q2Seconds, ~0),
                        IFNULL(qualifying.q3Seconds, ~0))), ~0)
                        -((SELECT MIN(LEAST(IFNULL(qualifying1.q1Seconds, ~0),
                            IFNULL(qualifying1.q2Seconds, ~0),
                            IFNULL(qualifying1.q3Seconds, ~0)))
                            FROM qualifying qualifying1
                            WHERE qualifying1.raceId = qualifying.raceId))
                FROM qualifying
                INNER JOIN drivers ON qualifying.driverId=drivers.driverId
                INNER JOIN constructors ON qualifying.constructorId=constructors.constructorId
                WHERE raceId=%s;""",
            (race_id,)
        )
        return cursor.fetchall()

    def get_qualifying_fastest_lap(self, race_id):
        """ Gets the fastest lap in qualifying for a given race. """
        cursor = self.query(
            """
            SELECT
                MIN(LEAST(IFNULL(q1Seconds, ~0),
                    IFNULL(q2Seconds, ~0),
                    IFNULL(q3Seconds, ~0)))
            FROM qualifying WHERE raceId = %s;""",
            (race_id,)
        )
        return cursor.fetchone()[0]

    def get_all_laps_prior_to_race(self, race_id):
        """ Gets all qualifying results before a given race. """
        cursor = self.query(
            """
                SELECT
                    qualifying.driverId,
                    races1.circuitId,
                    COALESCE(NULLIF(qualifying.q3, ''),
                        NULLIF(qualifying.q2, ''),
                        NULLIF(qualifying.q1, ''))
                FROM races
                INNER JOIN races races1 ON races1.year=races.year
                INNER JOIN qualifying ON qualifying.raceId=races1.raceId
                WHERE races.raceId = %s AND races1.raceId<races.raceId;""",
            (race_id,)
        )
        return cursor.fetchall()

    def get_laps_in_prior_season_to_race(self, race_id):
        """ Gets all laps in the season before the given race. """
        cursor = self.query(
            """
                SELECT
                    CONCAT(qualifying.driverId,races1.circuitId),
                    COALESCE(NULLIF(qualifying.q3, ''),
                        NULLIF(qualifying.q2, ''),
                        NULLIF(qualifying.q1, ''))
                FROM races
                INNER JOIN races races1 ON races1.year=races.year-1
                INNER JOIN qualifying ON qualifying.raceId=races1.raceId
                WHERE races.raceId = %s;""",
            (race_id,)
        )
        return cursor.fetchall()

    def get_next_race_year_round(self):
        """ Gets the race ID, round, date and year for the
            next race without any recorded results. """
        cursor = self.query(
            """
                SELECT
                    races.year,
                    races.round,
                    races.raceId,
                    races.date
                FROM results
                INNER JOIN races ON results.raceId<races.raceId
                ORDER by results.raceId DESC
                LIMIT 1;"""
        )
        return cursor.fetchone()

    def get_next_race_year_round_qualifying(self):
        """ Gets the race ID, round, date and year for the
            next qualifying session without any recorded results. """
        cursor = self.query(
            """
                SELECT
                    races.year,
                    races.round,
                    races.raceId,
                    races.date
                FROM qualifying
                INNER JOIN races ON qualifying.raceId<races.raceId
                ORDER BY qualifying.raceId DESC
                LIMIT 1;"""
        )
        return cursor.fetchone()

    def get_driver_references(self):
        """ Get a list of driver references with corresponding ID's. """
        cursor = self.query("SELECT driverRef, driverId FROM drivers;")
        return cursor.fetchall()

    def get_constructor_references(self):
        """ Get a list of constructor references with corresponding ID's. """
        cursor = self.query("SELECT constructorRef, constructorId FROM constructors;")
        return cursor.fetchall()

    def insert_driver(self, driver_ref, number, code, forename, surname, dob, nationality, url):
        """ Insert a new driver with the provided information. """
        cursor = self.query(
            """
                INSERT INTO drivers
                    (driverRef, number, code, forename, surname, dob, nationality, url)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
            (driver_ref, number, code, forename, surname, dob, nationality, url)
        )
        self.database.commit()
        return cursor.lastrowid

    def insert_constructor(self, constructor_ref, name, nationality, url):
        """ Insert a new constructor with the provided information. """
        cursor = self.query(
            """
            INSERT INTO constructors
                (constructorRef, name, nationality, url)
                VALUES (%s, %s, %s, %s)""",
            (constructor_ref, name, nationality, url)
        )
        self.database.commit()
        return cursor.lastrowid

    def insert_result(
            self,
            race_id, driver_id, constructor_id, number, grid,
            position, position_text, position_order, points,
            laps, time, milliseconds, fastest_lap,
            rank, fastest_lap_time, fastest_lap_speed, status_id
    ):
        """ Insert a new race result with the provided information. """
        cursor = self.query(
            """
                INSERT INTO results
                    (raceId, driverId, constructorId, number, grid, position,
                        positionText,positionOrder, points, laps, time,
                        milliseconds, fastestLap, rank, fastestLapTime,
                        fastestLapSpeed, statusId)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s, %s, %s)""",
            (
                race_id, driver_id, constructor_id, number, grid, position,
                position_text, position_order, points, laps, time,
                milliseconds, fastest_lap, rank, fastest_lap_time,
                fastest_lap_speed, status_id
            )
        )
        self.database.commit()
        return cursor.rowcount

    def insert_qualifying(
            self,
            race_id, driver_id, constructor_id, number, position,
            q1, q2, q3, q1_seconds, q2_seconds, q3_seconds
    ):
        """ Insert a new qualifying result with the provided information. """
        cursor = self.query(
            """
                INSERT INTO qualifying
                    (raceId, driverId, constructorId, number, position,
                    q1, q2, q3, q1Seconds, q2Seconds, q3Seconds)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            (
                race_id, driver_id, constructor_id, number, position,
                q1, q2, q3, q1_seconds, q2_seconds, q3_seconds
            )
        )
        self.database.commit()
        return cursor.rowcount

    def get_next_missing_season(self):
        """ Gets the next season year which requires a calendar. """
        cursor = self.query("SELECT MAX(year)+1 FROM races;")
        return cursor.fetchone()[0]

    def get_circuit_references(self):
        """ Gets a list of circuit references with corresponding ID's. """
        cursor = self.query("SELECT circuitRef, circuitId FROM circuits;")
        return cursor.fetchall()

    def insert_circuit(self, circuit_ref, circuit_name, locality, country, lat, lng, url):
        """ Insert a new circuit with the provided information. """
        cursor = self.query(
            """
                INSERT INTO circuits
                (circuitRef, name, location, country, lat, lng, url)
                VALUES (%s, %s, %s, %s, %s, %s, %s)""",
            (circuit_ref, circuit_name, locality, country, lat, lng, url)
        )
        self.database.commit()
        return cursor.lastrowid

    def insert_race(self, year, round_num, circuit_id, name, date, time, url):
        """ Insert a new race with the provided information. """
        cursor = self.query(
            """
                INSERT INTO races
                (year, round, circuitId, name, date, time, url)
                VALUES (%s, %s, %s, %s, %s, %s, %s)""",
            (year, round_num, circuit_id, name, date, time, url)
        )
        self.database.commit()
        return cursor.rowcount

    def delete_race(self, race_id):
        """ Deletes the race with the given ID. """
        cursor = self.query("DELETE FROM races WHERE raceId = %s", (race_id,))
        return cursor.rowcount

    def mark_races_as_in_progress(self, last_race_id):
        """ Marks all untrained races as now in progress. """
        cursor = self.query(
            """UPDATE
                races SET raceTrained = FALSE
            WHERE raceTrained IS NULL
                AND evaluationRace IS NOT TRUE
                AND raceId <= %s;""",
            (last_race_id,)
        )
        return cursor.rowcount

    def mark_qualifiyng_as_in_progress(self, last_race_id):
        """ Marks all untrained races as now in progress. """
        cursor = self.query(
            """UPDATE
                races SET qualifyingTrained = FALSE
            WHERE qualifyingTrained IS NULL
                AND evaluationRace IS NOT TRUE
                AND raceId <= %s;""",
            (last_race_id,)
        )
        return cursor.rowcount

    def get_race_dataset(self):
        """ Gets the race dataset for training. """
        cursor = self.query(
            """
            SELECT
                REPLACE(LOWER(races.name), ' grand prix', ''),
                results.grid,
                NULLIF((LEAST(IFNULL(qualifying.q1Seconds, ~0),
                    IFNULL(qualifying.q2Seconds, ~0),
                    IFNULL(qualifying.q3Seconds, ~0))), ~0)
                    -((SELECT MIN(LEAST(IFNULL(qualifying1.q1Seconds, ~0),
                        IFNULL(qualifying1.q2Seconds, ~0),
                        IFNULL(qualifying1.q3Seconds, ~0)))
                            FROM qualifying qualifying1
                            WHERE qualifying1.raceId = qualifying.raceId)),
                results.position,
                (SELECT
                    driverRef
                    FROM drivers
                    WHERE driverId=qualifying.driverId
                ),
                (SELECT
                    constructorRef
                    FROM constructors
                    WHERE constructorId=qualifying.constructorId
                )
            FROM races
            INNER JOIN results ON results.raceId=races.raceId
            INNER JOIN qualifying ON qualifying.raceId=results.raceId
            AND qualifying.driverId=results.driverId
            WHERE raceTrained is FALSE AND evaluationRace is not TRUE
                AND results.position IS NOT NULL AND results.position <= 20
                AND races.year >= 2000
                AND results.grid <= 20
                AND (qualifying.q1Seconds IS NOT NULL
                    OR qualifying.q2Seconds IS NOT NULL
                    OR qualifying.q3Seconds IS NOT NULL)
            ORDER BY results.resultId ASC;"""
        )
        return cursor.fetchall()

    def get_qualifying_dataset(self):
        """ Gets the qualifying dataset for training. """
        cursor = self.query(
            """
            SELECT
                REPLACE(LOWER(races.name), ' grand prix', ''),
                NULLIF((LEAST(IFNULL(qualifying.q1Seconds, ~0),
                    IFNULL(qualifying.q2Seconds, ~0),
                    IFNULL(qualifying.q3Seconds, ~0))), ~0)
                    -((SELECT MIN(LEAST(IFNULL(qualifying1.q1Seconds, ~0),
                        IFNULL(qualifying1.q2Seconds, ~0),
                        IFNULL(qualifying1.q3Seconds, ~0)))
                            FROM qualifying qualifying1
                            WHERE qualifying1.raceId = qualifying.raceId)),
                (SELECT
                    driverRef
                    FROM drivers
                    WHERE driverId=qualifying.driverId
                ),
                (SELECT
                    constructorRef
                    FROM constructors
                    WHERE constructorId=qualifying.constructorId
                )
            FROM races
            INNER JOIN qualifying ON qualifying.raceId=races.raceId
            WHERE qualifyingTrained is FALSE AND evaluationRace is not TRUE
            AND races.year >= 2000
            AND (qualifying.q1Seconds IS NOT NULL OR qualifying.q2Seconds IS NOT NULL
                OR qualifying.q3Seconds IS NOT NULL)
            ORDER BY qualifying.qualifyId ASC;"""
        )
        return cursor.fetchall()

    def get_race_dataset_form(self):
        """ Gets the form averages for the training set. """
        cursor = self.query(
            """
            SELECT
                (SELECT AVG(position)
                    FROM
                        (SELECT position
                            FROM results results1
                            WHERE results1.raceId < results.raceId
                            AND results.driverId = results1.driverId
                            AND position IS NOT NULL
                            ORDER BY raceId DESC
                            LIMIT 3)
                            results2)
                    as avg
            FROM races
            INNER JOIN results ON results.raceId=races.raceId
            INNER JOIN qualifying ON qualifying.raceId=results.raceId
            AND qualifying.driverId=results.driverId
            WHERE raceTrained is FALSE AND evaluationRace is not TRUE
                AND results.position IS NOT NULL AND results.position <= 20
                AND races.year >= 2000
                AND results.grid <= 20
                AND (qualifying.q1Seconds IS NOT NULL
                    OR qualifying.q2Seconds IS NOT NULL
                    OR qualifying.q3Seconds IS NOT NULL)
            ORDER BY results.resultId ASC;"""
        )
        return cursor.fetchall()

    def get_qualifying_dataset_form(self):
        """ Gets the pace averages for the qualifying training set. """
        cursor = self.query(
            """
            SELECT
                (SELECT AVG(delta)
                    FROM
                        (SELECT
                            (NULLIF((LEAST(IFNULL(qualifying1.q1Seconds, ~0),
                            IFNULL(qualifying1.q2Seconds, ~0),
                            IFNULL(qualifying1.q3Seconds, ~0))), ~0)
                            -((SELECT MIN(LEAST(IFNULL(qualifying2.q1Seconds, ~0),
                                IFNULL(qualifying2.q2Seconds, ~0),
                                IFNULL(qualifying2.q3Seconds, ~0)))
                                    FROM qualifying qualifying2
                                    WHERE qualifying2.raceId = qualifying1.raceId)))
                                as delta
                            FROM qualifying qualifying1
                            WHERE qualifying1.raceId < qualifying.raceId
                            AND qualifying.driverId = qualifying1.driverId
                            AND (qualifying1.q1Seconds IS NOT NULL
                                OR qualifying1.q2Seconds IS NOT NULL
                                OR qualifying1.q3Seconds IS NOT NULL)
                            ORDER BY qualifyId DESC
                            LIMIT 3)
                            results2)
                    as avg
            FROM races
            INNER JOIN qualifying ON qualifying.raceId=races.raceId
            WHERE qualifyingTrained is FALSE AND evaluationRace is not TRUE
            AND races.year >= 2000
            AND (qualifying.q1Seconds IS NOT NULL OR qualifying.q2Seconds IS NOT NULL
                OR qualifying.q3Seconds IS NOT NULL)
            ORDER BY qualifying.qualifyId ASC;"""
        )
        return cursor.fetchall()

    def get_race_dataset_form_circuit(self):
        """ Gets the circuit averages for the training set. """
        cursor = self.query(
            """
            SELECT
                (SELECT AVG(position)
                    FROM
                        (SELECT position
                            FROM results results1
                            INNER JOIN races races1
                            ON races1.raceId=results1.raceId
                            WHERE results1.raceId < results.raceId
                            AND results.driverId = results1.driverId
                            AND position IS NOT NULL
                            AND races1.circuitId=races.circuitId
                            ORDER BY results1.raceId DESC
                            LIMIT 3)
                            results2)
                    as avg
            FROM races
            INNER JOIN results ON results.raceId=races.raceId
            INNER JOIN qualifying ON qualifying.raceId=results.raceId
            AND qualifying.driverId=results.driverId
            WHERE raceTrained is FALSE AND evaluationRace is not TRUE
                AND results.position IS NOT NULL AND results.position <= 20
                AND races.year >= 2000
                AND results.grid <= 20
                AND (qualifying.q1Seconds IS NOT NULL
                    OR qualifying.q2Seconds IS NOT NULL
                    OR qualifying.q3Seconds IS NOT NULL)
            ORDER BY results.resultId ASC;"""
        )
        return cursor.fetchall()

    def get_qualifying_dataset_form_circuit(self):
        """ Gets the pace averages at the particular circuit for the qualifying training set. """
        cursor = self.query(
            """
            SELECT
                (SELECT AVG(delta)
                    FROM
                        (SELECT
                            (NULLIF((LEAST(IFNULL(qualifying1.q1Seconds, ~0),
                            IFNULL(qualifying1.q2Seconds, ~0),
                            IFNULL(qualifying1.q3Seconds, ~0))), ~0)
                            -((SELECT MIN(LEAST(IFNULL(qualifying2.q1Seconds, ~0),
                                IFNULL(qualifying2.q2Seconds, ~0),
                                IFNULL(qualifying2.q3Seconds, ~0)))
                                    FROM qualifying qualifying2
                                    WHERE qualifying2.raceId = qualifying1.raceId)))
                                as delta
                            FROM qualifying qualifying1
                            INNER JOIN races races1 ON qualifying1.raceId = races1.raceId
                            WHERE qualifying1.raceId < qualifying.raceId
                            AND qualifying.driverId = qualifying1.driverId
                            AND (qualifying1.q1Seconds IS NOT NULL
                                OR qualifying1.q2Seconds IS NOT NULL
                                OR qualifying1.q3Seconds IS NOT NULL)
                            AND races.circuitId=races1.circuitId
                            ORDER BY qualifyId DESC
                            LIMIT 3)
                            results2)
                    as avg
            FROM races
            INNER JOIN qualifying ON qualifying.raceId=races.raceId
            WHERE qualifyingTrained is FALSE AND evaluationRace is not TRUE
            AND races.year >= 2000
            AND (qualifying.q1Seconds IS NOT NULL OR qualifying.q2Seconds IS NOT NULL
                OR qualifying.q3Seconds IS NOT NULL)
            ORDER BY qualifying.qualifyId ASC;"""
        )
        return cursor.fetchall()

    def get_race_dataset_standings(self):
        """ Gets the championship standings for the training set. """
        cursor = self.query(
            """
            SELECT
                (SELECT position
                    FROM driverStandings
                    WHERE driverStandings.raceId<results.raceId
                    AND driverStandings.driverId=results.driverId
                    ORDER BY driverStandingsId DESC
                    LIMIT 1)
                    as standing
            FROM races
            INNER JOIN results ON results.raceId=races.raceId
            INNER JOIN qualifying ON qualifying.raceId=results.raceId
            AND qualifying.driverId=results.driverId
            WHERE raceTrained is FALSE AND evaluationRace is not TRUE
                AND results.position IS NOT NULL AND results.position <= 20
                AND races.year >= 2000
                AND results.grid <= 20
                AND (qualifying.q1Seconds IS NOT NULL
                    OR qualifying.q2Seconds IS NOT NULL
                    OR qualifying.q3Seconds IS NOT NULL)
            ORDER BY results.resultId ASC;"""
        )
        return cursor.fetchall()

    def get_qualifying_dataset_standings(self):
        """ Gets the championship standings for the qualifying training set. """
        cursor = self.query(
            """
            SELECT
                (SELECT position
                    FROM driverStandings
                    WHERE driverStandings.raceId<qualifying.raceId
                    AND driverStandings.driverId=qualifying.driverId
                    ORDER BY driverStandingsId DESC
                    LIMIT 1)
                    as standing
            FROM races
                INNER JOIN qualifying ON qualifying.raceId=races.raceId
                WHERE qualifyingTrained is FALSE AND evaluationRace is not TRUE
                AND races.year >= 2000
                AND (qualifying.q1Seconds IS NOT NULL OR qualifying.q2Seconds IS NOT NULL
                    OR qualifying.q3Seconds IS NOT NULL)
                ORDER BY qualifying.qualifyId ASC;"""
        )
        return cursor.fetchall()


    def get_race_dataset_position_changes(self):
        """ Gets the championship standings for the training set. """
        cursor = self.query(
            """
            SELECT
                (SELECT AVG(diff)
                    FROM
                        (SELECT grid-position AS diff
                            FROM results results1
                            WHERE results1.raceId < results.raceId
                            AND results.driverId = results1.driverId
                            AND position IS NOT NULL
                            AND grid IS NOT NULL
                            ORDER BY raceId DESC
                            LIMIT 3)
                            results2)
                    as avg
            FROM races
            INNER JOIN results ON results.raceId=races.raceId
            INNER JOIN qualifying ON qualifying.raceId=results.raceId
            AND qualifying.driverId=results.driverId
            WHERE raceTrained is FALSE AND evaluationRace is not TRUE
                AND results.position IS NOT NULL AND results.position <= 20
                AND races.year >= 2000
                AND results.grid <= 20
                AND (qualifying.q1Seconds IS NOT NULL
                    OR qualifying.q2Seconds IS NOT NULL
                    OR qualifying.q3Seconds IS NOT NULL)
            ORDER BY results.resultId ASC;"""
        )
        return cursor.fetchall()

    def get_race_dataset_form_team(self):
        """ Gets the form averages for the team for the training set. """
        cursor = self.query(
            """
            SELECT
                (SELECT AVG(position)
                    FROM
                        (SELECT position
                            FROM results results1
                            WHERE results1.raceId < results.raceId
                            AND results.constructorId = results1.constructorId
                            AND position IS NOT NULL
                            ORDER BY raceId DESC
                            LIMIT 6)
                            results2)
                    as avg
            FROM races
            INNER JOIN results ON results.raceId=races.raceId
            INNER JOIN qualifying ON qualifying.raceId=results.raceId
            AND qualifying.driverId=results.driverId
            WHERE raceTrained is FALSE AND evaluationRace is not TRUE
                AND results.position IS NOT NULL AND results.position <= 20
                AND races.year >= 2000
                AND results.grid <= 20
                AND (qualifying.q1Seconds IS NOT NULL
                    OR qualifying.q2Seconds IS NOT NULL
                    OR qualifying.q3Seconds IS NOT NULL)
            ORDER BY results.resultId ASC;"""
        )
        return cursor.fetchall()

    def get_race_dataset_form_team_circuit(self):
        """ Gets the team circuit averages for the training set. """
        cursor = self.query(
            """
            SELECT
                (SELECT AVG(position)
                    FROM
                        (SELECT position
                            FROM results results1
                            INNER JOIN races races1
                            ON races1.raceId=results1.raceId
                            WHERE results1.raceId < results.raceId
                            AND results.constructorId = results1.constructorId
                            AND position IS NOT NULL
                            AND races1.circuitId=races.circuitId
                            ORDER BY results1.raceId DESC
                            LIMIT 6)
                            results2)
                    as avg
            FROM races
            INNER JOIN results ON results.raceId=races.raceId
            INNER JOIN qualifying ON qualifying.raceId=results.raceId
            AND qualifying.driverId=results.driverId
            WHERE raceTrained is FALSE AND evaluationRace is not TRUE
                AND results.position IS NOT NULL AND results.position <= 20
                AND races.year >= 2000
                AND results.grid <= 20
                AND (qualifying.q1Seconds IS NOT NULL
                    OR qualifying.q2Seconds IS NOT NULL
                    OR qualifying.q3Seconds IS NOT NULL)
            ORDER BY results.resultId ASC;"""
        )
        return cursor.fetchall()

    def get_qualifying_dataset_form_team(self):
        """ Gets the team pace averages for the qualifying training set. """
        cursor = self.query(
            """
            SELECT
                (SELECT AVG(delta)
                    FROM
                        (SELECT
                            (NULLIF((LEAST(IFNULL(qualifying1.q1Seconds, ~0),
                            IFNULL(qualifying1.q2Seconds, ~0),
                            IFNULL(qualifying1.q3Seconds, ~0))), ~0)
                            -((SELECT MIN(LEAST(IFNULL(qualifying2.q1Seconds, ~0),
                                IFNULL(qualifying2.q2Seconds, ~0),
                                IFNULL(qualifying2.q3Seconds, ~0)))
                                    FROM qualifying qualifying2
                                    WHERE qualifying2.raceId = qualifying1.raceId)))
                                as delta
                            FROM qualifying qualifying1
                            WHERE qualifying1.raceId < qualifying.raceId
                            AND qualifying.constructorId = qualifying1.constructorId
                            AND (qualifying1.q1Seconds IS NOT NULL
                                OR qualifying1.q2Seconds IS NOT NULL
                                OR qualifying1.q3Seconds IS NOT NULL)
                            ORDER BY qualifyId DESC
                            LIMIT 6)
                            results2)
                    as avg
            FROM races
            INNER JOIN qualifying ON qualifying.raceId=races.raceId
            WHERE qualifyingTrained is FALSE AND evaluationRace is not TRUE
            AND races.year >= 2000
            AND (qualifying.q1Seconds IS NOT NULL OR qualifying.q2Seconds IS NOT NULL
                OR qualifying.q3Seconds IS NOT NULL)
            ORDER BY qualifying.qualifyId ASC;"""
        )
        return cursor.fetchall()

    def get_qualifying_dataset_form_team_circuit(self):
        """ Gets the circuit team pace averages for the qualifying training set. """
        cursor = self.query(
            """
            SELECT
                (SELECT AVG(delta)
                    FROM
                        (SELECT
                            (NULLIF((LEAST(IFNULL(qualifying1.q1Seconds, ~0),
                            IFNULL(qualifying1.q2Seconds, ~0),
                            IFNULL(qualifying1.q3Seconds, ~0))), ~0)
                            -((SELECT MIN(LEAST(IFNULL(qualifying2.q1Seconds, ~0),
                                IFNULL(qualifying2.q2Seconds, ~0),
                                IFNULL(qualifying2.q3Seconds, ~0)))
                                    FROM qualifying qualifying2
                                    WHERE qualifying2.raceId = qualifying1.raceId)))
                                as delta
                            FROM qualifying qualifying1
                            INNER JOIN races races1 ON qualifying1.raceId = races1.raceId
                            WHERE qualifying1.raceId < qualifying.raceId
                            AND qualifying.constructorId = qualifying1.constructorId
                            AND (qualifying1.q1Seconds IS NOT NULL
                                OR qualifying1.q2Seconds IS NOT NULL
                                OR qualifying1.q3Seconds IS NOT NULL)
                            AND races.circuitId=races1.circuitId
                            ORDER BY qualifyId DESC
                            LIMIT 6)
                            results2)
                    as avg
            FROM races
            INNER JOIN qualifying ON qualifying.raceId=races.raceId
            WHERE qualifyingTrained is FALSE AND evaluationRace is not TRUE
            AND races.year >= 2000
            AND (qualifying.q1Seconds IS NOT NULL OR qualifying.q2Seconds IS NOT NULL
                OR qualifying.q3Seconds IS NOT NULL)
            ORDER BY qualifying.qualifyId ASC;"""
        )
        return cursor.fetchall()

    def mark_races_as_complete(self):
        """ Mark all in progress races as trained. """
        cursor = self.query(
            """
                UPDATE
                    races SET raceTrained = TRUE
                WHERE raceTrained IS FALSE
                    AND evaluationRace IS NOT TRUE;"""
        )
        return cursor.rowcount

    def mark_qualifying_as_complete(self):
        """ Mark all in progress races as qualifying trained. """
        cursor = self.query(
            """
                UPDATE
                    races SET qualifyingTrained = TRUE
                WHERE qualifyingTrained IS FALSE
                    AND evaluationRace IS NOT TRUE;"""
        )
        return cursor.rowcount

    def get_calendar(self, year):
        """ Gets the race calendar for the given year. """
        cursor = self.query(
            """
                SELECT
                    races.name,
                    races.date,
                    races.time,
                    races.round,
                    circuits.name,
                    circuits.circuitRef,
                    circuits.location,
                    circuits.country
                FROM races
                INNER JOIN circuits ON circuits.circuitId = races.circuitId
                WHERE year = %s
                ORDER BY races.round ASC;""",
            (year,)
        )
        return cursor.fetchall()

    def get_last_race_id(self):
        """ Gets the last race with a result. """
        cursor = self.query("SELECT MAX(raceId) FROM results;")
        return cursor.fetchone()[0]

    def get_last_race_id_in_year(self, year):
        """ Gets the last race ID in a given season year. """
        cursor = self.query(
            """
                SELECT
                    MAX(results.raceId)
                FROM results
                INNER JOIN races ON races.raceId=results.raceId
                WHERE races.year = %s;""",
            (year,)
        )
        return cursor.fetchone()[0]

    def get_drivers_standings(self, race):
        """ Gets the driver's standings at the given race. """
        cursor = self.query(
            """
                SELECT
                    drivers.*,
                    driverStandings.points,
                    driverStandings.wins,
                    driverStandings.position
                FROM driverStandings
                INNER JOIN drivers ON drivers.driverId=driverStandings.driverId
                WHERE raceId = %s
                ORDER BY position ASC;""",
            (race,)
        )
        return cursor.fetchall()

    def get_constructors_standings(self, race):
        """ Gets the constructor's standings at the given race. """
        cursor = self.query(
            """
                SELECT
                    constructors.constructorId,
                    constructors.constructorRef,
                    constructors.name,
                    constructors.nationality,
                    constructors.url,
                    constructorStandings.points,
                    constructorStandings.wins,
                    constructorStandings.position
                FROM constructorStandings
                INNER JOIN constructors
                    ON constructors.constructorId=constructorStandings.constructorId
                WHERE raceId = %s
                ORDER BY position ASC;""",
            (race,)
        )
        return cursor.fetchall()

    def get_race_results(self, race):
        """ Gets the result's of a given race, including laps, points, position. """
        cursor = self.query(
            """
                SELECT
                    drivers.driverId,
                    resultId,
                    driverRef,
                    drivers.number,
                    drivers.code,
                    forename,
                    surname,
                    dob,
                    nationality,
                    url,
                    grid,
                    position,
                    points,
                    laps
                FROM results
                INNER JOIN status ON status.statusId=results.statusId
                INNER JOIN drivers ON drivers.driverId=results.driverId
                WHERE raceId = %s
                ORDER BY -position DESC;""",
            (race,)
        )
        return cursor.fetchall()

    def get_last_qualifying_race_id(self):
        """ Gets the raceId of the last qualifying session. """
        cursor = self.query("SELECT MAX(raceId) FROM qualifying;")
        return cursor.fetchone()[0]

    def get_qualifying_results(self, race):
        """ Gets the qualifying results of a given session, including all laps. """
        cursor = self.query(
            """
                SELECT
                    drivers.driverId,
                    qualifyId,
                    driverRef,
                    drivers.number,
                    drivers.code,
                    forename,
                    surname,
                    dob,
                    nationality,
                    url,
                    position,
                    q1,
                    q2,
                    q3
                FROM qualifying
                INNER JOIN drivers ON drivers.driverId=qualifying.driverId
                WHERE raceId = %s
                ORDER BY -position DESC;""",
            (race,)
        )
        return cursor.fetchall()

    def insert_race_log(self, driver_id, position, feature_hash, time, feature_string):
        """ Insert a result into the race prediction log. """
        cursor = self.query(
            """
            INSERT INTO racePredictionLog
                (driverId, position, featureHash, time, features)
                VALUES (%s, %s, %s, %s, %s);""",
            (driver_id, position, feature_hash, time, feature_string)
        )
        self.database.commit()
        return cursor.rowcount

    def get_race_log(self, feature_hash):
        """ Fetch a result from the log, using feature hash. """
        cursor = self.query(
            """
                SELECT drivers.*
                FROM racePredictionLog
                INNER JOIN drivers ON drivers.driverId=racePredictionLog.driverId
                WHERE featureHash = %s AND time >= (NOW() - INTERVAL 2 WEEK)
                ORDER BY position ASC;""",
            (feature_hash,))
        return cursor.fetchall()

    def insert_qualifying_log(self, driver_id, constructor_id, position, feature_hash, time, delta, feature_string):
        """ Insert a result into the qualifying prediction log. """
        cursor = self.query(
            """
                INSERT INTO qualifyingPredictionLog
                    (driverId, constructorId, position, featureHash, time, delta, features)
                    VALUES (%s, %s, %s, %s, %s, %s, %s);""",
            (driver_id, constructor_id, position, feature_hash, time, delta, feature_string)
        )
        self.database.commit()
        return cursor.rowcount

    def get_qualifying_log(self, feature_hash):
        """ Fetch a result from the log, using feature hash. """
        cursor = self.query(
            """
                SELECT
                    drivers.*,
                    constructors.constructorRef,
                    constructors.constructorId,
                    delta
                FROM qualifyingPredictionLog
                INNER JOIN drivers ON drivers.driverId=qualifyingPredictionLog.driverId
                INNER JOIN constructors ON
                constructors.constructorId=qualifyingPredictionLog.constructorId
                WHERE featureHash = %s AND time >= (NOW() - INTERVAL 2 WEEK)
                ORDER BY position ASC;""",
            (feature_hash,)
        )
        return cursor.fetchall()

    def get_next_race_year_round_driver_standings(self):
        """ Gets the next race/year/round based on driver standing records. """
        cursor = self.query(
            """
                SELECT
                    races.year,
                    races.round,
                    races.raceId,
                    races.date
                FROM driverStandings
                INNER JOIN races ON driverStandings.raceId<races.raceId
                ORDER BY driverStandings.raceId DESC
                LIMIT 1;"""
            )
        return cursor.fetchone()

    def insert_driver_standing(self, race_id, driver_id, points, position, position_text, wins):
        """ Insert a driver standing record with the given information. """
        cursor = self.query(
            """
                INSERT INTO driverStandings
                    (raceId, driverId, points, position, positionText, wins)
                    VALUES (%s, %s, %s, %s, %s, %s);""",
            (race_id, driver_id, points, position, position_text, wins)
        )
        self.database.commit()
        return cursor.rowcount

    def get_next_race_year_round_constructor_standings(self):
        """ Gets the next race/year/round based on constructor standing records. """
        cursor = self.query(
            """
                SELECT
                    races.year,
                    races.round,
                    races.raceId,
                    races.date
                FROM constructorStandings
                INNER JOIN races ON constructorStandings.raceId<races.raceId
                ORDER BY constructorStandings.raceId DESC
                LIMIT 1;""")
        return cursor.fetchone()

    def insert_constructor_standing(
            self,
            race_id, constructor_id, points, position, position_text, wins
    ):
        """ Insert a constructor standing record with the given information. """
        cursor = self.query(
            """
                INSERT INTO constructorStandings
                    (raceId, constructorId, points, position, positionText, wins)
                    VALUES (%s, %s, %s, %s, %s, %s);""",
            (
                race_id, constructor_id, points, position,
                position_text, wins
            )
        )
        self.database.commit()
        return cursor.rowcount

    def get_evaluation_races(self):
        """ Gets the full list of evaluation raceId's. """
        cursor = self.query("SELECT raceId FROM races WHERE evaluationRace IS TRUE;")
        return cursor.fetchall()

    def mark_all_races_as_untrained(self):
        """ Marks all races as untrained. """
        cursor = self.query(
            """UPDATE
                races SET raceTrained = NULL;"""
        )
        return cursor.rowcount

    def mark_all_qualifying_as_untrained(self):
        """ Marks all races as qualifying untrained. """
        cursor = self.query(
            """UPDATE
                races SET qualifyingTrained = NULL;"""
        )
        return cursor.rowcount

    def get_race_averages(self, race):
        """ Fetches the last averages for each driver. """
        cursor = self.query(
            """
                SELECT
                    driverId,
                    (SELECT AVG(position)
                        FROM
                            (SELECT position
                                FROM results results1
                                WHERE results1.raceId <= results.raceId
                                AND results.driverId = results1.driverId
                                AND position IS NOT NULL
                                ORDER BY raceId DESC
                                LIMIT 3)
                                results2)
                        as avg
                FROM results
                WHERE raceId = (SELECT MAX(raceId)
                    FROM races races1
                    WHERE races1.raceId < %s);
            """,
            (race,)
        )
        return cursor.fetchall()

    def get_race_averages_team(self, race):
        """ Fetches the last averages for each driver based on team. """
        cursor = self.query(
            """
                SELECT
                    driverId,
                    (SELECT AVG(position)
                        FROM
                            (SELECT position
                                FROM results results1
                                WHERE results1.raceId <= results.raceId
                                AND results.constructorId = results1.constructorId
                                AND position IS NOT NULL
                                ORDER BY raceId DESC
                                LIMIT 3)
                                results2)
                        as avg
                FROM results
                WHERE raceId = (SELECT MAX(raceId)
                    FROM races races1
                    WHERE races1.raceId < %s);
            """,
            (race,)
        )
        return cursor.fetchall()

    def get_circuit_averages(self, race):
        """ Fetches averages for driver at this circuit. """
        cursor = self.query(
            """
                SELECT
                    driverId,
                    (SELECT AVG(position)
                        FROM
                            (SELECT position
                                FROM results results1
                                INNER JOIN races
                                ON races.raceId=results1.raceId
                                WHERE results1.raceId <= results.raceId
                                AND results.driverId = results1.driverId
                                AND position IS NOT NULL
                                AND races.circuitId=(SELECT circuitId
                                    FROM races WHERE raceId = %s)
                                ORDER BY results1.raceId DESC
                                LIMIT 3)
                                results2)
                        as avg
                FROM results
                WHERE results.raceId = (SELECT MAX(raceId)
                    FROM races races1
                    WHERE races1.raceId < %s);
            """,
            (race, race)
        )
        return cursor.fetchall()

    def get_circuit_averages_team(self, race):
        """ Fetches averages for driver at this circuit per team. """
        cursor = self.query(
            """
                SELECT
                    driverId,
                    (SELECT AVG(position)
                        FROM
                            (SELECT position
                                FROM results results1
                                INNER JOIN races
                                ON races.raceId=results1.raceId
                                WHERE results1.raceId <= results.raceId
                                AND results.constructorId = results1.constructorId
                                AND position IS NOT NULL
                                AND races.circuitId=(SELECT circuitId
                                    FROM races WHERE raceId = %s)
                                ORDER BY results1.raceId DESC
                                LIMIT 6)
                                results2)
                        as avg
                FROM results
                WHERE results.raceId = (SELECT MAX(raceId)
                    FROM races races1
                    WHERE races1.raceId < %s);
            """,
            (race, race)
        )
        return cursor.fetchall()

    def get_championship_positions(self, race):
        """ Fetches current championship positions. """
        cursor = self.query(
            """
                SELECT
                    results.driverId,
                    driverStandings.position
                FROM results
                INNER JOIN driverStandings
                ON driverStandings.driverId=results.driverId
                AND driverStandings.raceId=results.raceId
                WHERE results.raceId =
                    (SELECT MAX(raceId)
                        FROM races
                        WHERE raceId < %s);
            """,
            (race,)
        )
        return cursor.fetchall()

    def get_position_changes(self, race):
        """ Fetches the last averages for each driver. """
        cursor = self.query(
            """
                SELECT
                    driverId,
                    (SELECT AVG(diff)
                        FROM
                            (SELECT grid-position AS diff
                                FROM results results1
                                WHERE results1.raceId <= results.raceId
                                AND results.driverId = results1.driverId
                                AND position IS NOT NULL
                                AND grid IS NOT NULL
                                ORDER BY raceId DESC
                                LIMIT 3)
                                results2)
                        as avg
                FROM results
                WHERE raceId = (SELECT MAX(raceId)
                    FROM races races1
                    WHERE races1.raceId < %s);
            """,
            (race,)
        )
        return cursor.fetchall()

    def get_qualifying_form_with_drivers(self, race_id):
        """ Gets the pace averages for the qualifying at the given race. """
        cursor = self.query(
            """
            SELECT
                drivers.*,
                constructors.constructorRef,
                constructors.constructorId,
                (SELECT AVG(delta)
                    FROM
                        (SELECT
                            (NULLIF((LEAST(IFNULL(qualifying1.q1Seconds, ~0),
                            IFNULL(qualifying1.q2Seconds, ~0),
                            IFNULL(qualifying1.q3Seconds, ~0))), ~0)
                            -((SELECT MIN(LEAST(IFNULL(qualifying2.q1Seconds, ~0),
                                IFNULL(qualifying2.q2Seconds, ~0),
                                IFNULL(qualifying2.q3Seconds, ~0)))
                                    FROM qualifying qualifying2
                                    WHERE qualifying2.raceId = qualifying1.raceId)))
                                as delta
                            FROM qualifying qualifying1
                            WHERE qualifying1.raceId <= qualifying.raceId
                            AND qualifying.driverId = qualifying1.driverId
                            AND (qualifying1.q1Seconds IS NOT NULL
                                OR qualifying1.q2Seconds IS NOT NULL
                                OR qualifying1.q3Seconds IS NOT NULL)
                            ORDER BY qualifyId DESC
                            LIMIT 3)
                            results2)
                    as avg
            FROM qualifying
            INNER JOIN drivers ON drivers.driverId = qualifying.driverId
            INNER JOIN constructors ON constructors.constructorId=qualifying.constructorId
            WHERE qualifying.raceId = (
                SELECT MAX(raceId)
                FROM qualifying
                WHERE raceId < %s);""",
            (race_id,)
        )
        return cursor.fetchall()

    def get_qualifying_form_circuit(self, race_id):
        """ Gets the pace averages at the circuit for the qualifying at the given race. """
        cursor = self.query(
            """
            SELECT
                driverId,
                (SELECT AVG(delta)
                    FROM
                        (SELECT
                            (NULLIF((LEAST(IFNULL(qualifying1.q1Seconds, ~0),
                            IFNULL(qualifying1.q2Seconds, ~0),
                            IFNULL(qualifying1.q3Seconds, ~0))), ~0)
                            -((SELECT MIN(LEAST(IFNULL(qualifying2.q1Seconds, ~0),
                                IFNULL(qualifying2.q2Seconds, ~0),
                                IFNULL(qualifying2.q3Seconds, ~0)))
                                    FROM qualifying qualifying2
                                    WHERE qualifying2.raceId = qualifying1.raceId)))
                                as delta
                            FROM qualifying qualifying1
                            INNER JOIN races ON qualifying1.raceId=races.raceId
                            WHERE qualifying1.raceId <= qualifying.raceId
                            AND qualifying.driverId = qualifying1.driverId
                            AND (qualifying1.q1Seconds IS NOT NULL
                                OR qualifying1.q2Seconds IS NOT NULL
                                OR qualifying1.q3Seconds IS NOT NULL)
                            AND races.circuitId = (SELECT circuitId
                                FROM races WHERE raceId = %s)
                            ORDER BY qualifyId DESC
                            LIMIT 3)
                            results2)
                    as avg
            FROM qualifying
            WHERE qualifying.raceId = (
                SELECT MAX(raceId)
                FROM qualifying
                WHERE raceId < %s);""",
            (race_id, race_id,)
        )
        return cursor.fetchall()

    def get_qualifying_championship_positions(self, race):
        """ Fetches current championship positions. """
        cursor = self.query(
            """
                SELECT
                    qualifying.driverId,
                    driverStandings.position
                FROM qualifying
                INNER JOIN driverStandings
                ON driverStandings.driverId=qualifying.driverId
                AND driverStandings.raceId=qualifying.raceId
                WHERE qualifying.raceId =
                    (SELECT MAX(raceId)
                        FROM races
                        WHERE raceId < %s);
            """,
            (race,)
        )
        return cursor.fetchall()

    def get_qualifying_form_average_team(self, race_id):
        """ Gets the pace averages at the circuit for the qualifying at the given race. """
        cursor = self.query(
            """
            SELECT
                driverId,
                (SELECT AVG(delta)
                    FROM
                        (SELECT
                            (NULLIF((LEAST(IFNULL(qualifying1.q1Seconds, ~0),
                            IFNULL(qualifying1.q2Seconds, ~0),
                            IFNULL(qualifying1.q3Seconds, ~0))), ~0)
                            -((SELECT MIN(LEAST(IFNULL(qualifying2.q1Seconds, ~0),
                                IFNULL(qualifying2.q2Seconds, ~0),
                                IFNULL(qualifying2.q3Seconds, ~0)))
                                    FROM qualifying qualifying2
                                    WHERE qualifying2.raceId = qualifying1.raceId)))
                                as delta
                            FROM qualifying qualifying1
                            WHERE qualifying1.raceId <= qualifying.raceId
                            AND qualifying.constructorId = qualifying1.constructorId
                            AND (qualifying1.q1Seconds IS NOT NULL
                                OR qualifying1.q2Seconds IS NOT NULL
                                OR qualifying1.q3Seconds IS NOT NULL)
                            ORDER BY qualifyId DESC
                            LIMIT 6)
                            results2)
                    as avg
            FROM qualifying
            WHERE qualifying.raceId = (
                SELECT MAX(raceId)
                FROM qualifying
                WHERE raceId < %s);""",
            (race_id,)
        )
        return cursor.fetchall()

    def get_qualifying_form_circuit_team(self, race_id):
        """ Gets the circuit pace averages at the circuit for the qualifying at the given race. """
        cursor = self.query(
            """
            SELECT
                driverId,
                (SELECT AVG(delta)
                    FROM
                        (SELECT
                            (NULLIF((LEAST(IFNULL(qualifying1.q1Seconds, ~0),
                            IFNULL(qualifying1.q2Seconds, ~0),
                            IFNULL(qualifying1.q3Seconds, ~0))), ~0)
                            -((SELECT MIN(LEAST(IFNULL(qualifying2.q1Seconds, ~0),
                                IFNULL(qualifying2.q2Seconds, ~0),
                                IFNULL(qualifying2.q3Seconds, ~0)))
                                    FROM qualifying qualifying2
                                    WHERE qualifying2.raceId = qualifying1.raceId)))
                                as delta
                            FROM qualifying qualifying1
                            INNER JOIN races ON qualifying1.raceId=races.raceId
                            WHERE qualifying1.raceId <= qualifying.raceId
                            AND qualifying.constructorId = qualifying1.constructorId
                            AND (qualifying1.q1Seconds IS NOT NULL
                                OR qualifying1.q2Seconds IS NOT NULL
                                OR qualifying1.q3Seconds IS NOT NULL)
                            AND races.circuitId = (SELECT circuitId
                                FROM races WHERE raceId = %s)
                            ORDER BY qualifyId DESC
                            LIMIT 6)
                            results2)
                    as avg
            FROM qualifying
            WHERE qualifying.raceId = (
                SELECT MAX(raceId)
                FROM qualifying
                WHERE raceId < %s);""",
            (race_id, race_id,)
        )
        return cursor.fetchall()
