""" Utility functions used in the tests. """

def truncate_table(db, table):
    """ Cleares the given table. """
    cursor = db.cursor()
    cursor.execute("TRUNCATE TABLE "+table+";")
    db.commit()
    cursor.close()

def insert_initial_data(db, year, round_no=1, name=''):
    """ Insert data into races table. """
    cursor = db.cursor()
    cursor.execute(
        """INSERT INTO races
            (year, round, date, name, circuitId)
            VALUES (%s, %s, NOW(), %s, 1)""",
        (year, round_no, name,)
    )
    db.commit()
    cursor.close()

def insert_initial_circuit_data(db):
    """ Insert data into circuits table. """
    cursor = db.cursor()
    cursor.execute(
        """INSERT INTO circuits
            (circuitRef, name)
            VALUES ('bahrain', 'Bahrain International Circuit')
        """
        )
    db.commit()
    cursor.close()

def insert_initial_results_data(db, race_id=1, constructor_id=0, driver_id=0, position=None):
    """ Insert data into results table. """
    cursor = db.cursor()
    cursor.execute(
        """
        INSERT INTO results
        (raceId, driverId, constructorId, position)
        VALUES (%s, %s, %s, %s)""",
        (race_id, constructor_id, driver_id, position,)
    )
    db.commit()
    cursor.close()

def insert_initial_qualifying_data(db, race_id=1, constructor_id=0, driver_id=0, position=None):
    """ Insert data into qualifying table. """
    cursor = db.cursor()
    cursor.execute(
        """
        INSERT INTO qualifying
        (raceId, driverId, constructorId, position)
        VALUES (%s, %s, %s, %s)""",
        (race_id, constructor_id, driver_id, position,)
    )
    db.commit()
    cursor.close()

def insert_initial_driver_standing_data(db, race_id=1, driver_id=0, position=None):
    """ Insert data into driver standing table. """
    cursor = db.cursor()
    cursor.execute(
        """
        INSERT INTO driverStandings
        (raceId, driverId, position)
        VALUES (%s, %s, %s)""",
        (race_id, driver_id, position,)
    )
    db.commit()
    cursor.close()

def insert_initial_constructor_standing_data(db, race_id=1, constructor_id=0, position=None):
    """ Insert data into constructor standing table. """
    cursor = db.cursor()
    cursor.execute(
        """
        INSERT INTO constructorStandings
        (raceId, constructorId, position)
        VALUES (%s, %s, %s)""",
        (race_id, constructor_id, position,)
    )
    db.commit()
    cursor.close()

def insert_initial_driver_data(db, driver_ref='bottas', url=''):
    """ Insert data into driver table. """
    cursor = db.cursor()
    cursor.execute(
        """INSERT INTO drivers (driverRef, url) VALUES (%s, %s)""",
        (driver_ref,url,)
    )
    db.commit()
    cursor.close()

def insert_initial_constructor_data(db):
    """ Insert data into constructor table. """
    cursor = db.cursor()
    cursor.execute("""INSERT INTO constructors (constructorRef) VALUES ('red_bull')""")
    db.commit()
    cursor.close()

def insert_qualifying_prediction_data(db, race_id=1, constructor_id=1, driver_id=0, position=None):
    """ Insert data into qualifying prediction table. """
    cursor = db.cursor()
    cursor.execute(
        """
        INSERT INTO qualifyingPredictionLog
        (raceId, driverId, constructorId, position, time, delta)
        VALUES (%s, %s, %s, %s, NOW(), '0.123')""",
        (race_id, driver_id, constructor_id, position,)
    )
    db.commit()
    cursor.close()

def insert_race_prediction_data(db, race_id=1, driver_id=0, position=None, qualifying_predicted=True):
    """ Insert data into qualifying prediction table. """
    cursor = db.cursor()
    cursor.execute(
        """
        INSERT INTO racePredictionLog
        (raceId, driverId, position, time, qualifyingPredicted)
        VALUES (%s, %s, %s, NOW(), %s)""",
        (race_id, driver_id, position,qualifying_predicted,)
    )
    db.commit()
    cursor.close()

def get_race_data(db):
    """ Get race data for checking changes. """
    cursor = db.cursor()
    cursor.execute(
        """SELECT * FROM races
        INNER JOIN circuits ON circuits.circuitId=races.circuitId;
        """
    )
    result = cursor.fetchall()
    cursor.close()
    return result

def get_result_data(db):
    """ Get results data for checking changes. """
    cursor = db.cursor()
    cursor.execute(
        """
        SELECT * FROM results
        INNER JOIN drivers ON drivers.driverId=results.driverId
        INNER JOIN constructors ON constructors.constructorId=results.constructorId;
    """)
    result = cursor.fetchall()
    cursor.close()
    return result

def get_qualifying_data(db):
    """ Get qualifying data for checking changes. """
    cursor = db.cursor()
    cursor.execute("""
        SELECT * FROM qualifying
        INNER JOIN drivers ON drivers.driverId=qualifying.driverId
        INNER JOIN constructors ON constructors.constructorId=qualifying.constructorId;
    """)
    result = cursor.fetchall()
    cursor.close()
    return result

def get_driver_standing_data(db):
    """ Get driver standing data for checking changes. """
    cursor = db.cursor()
    cursor.execute("""
        SELECT * FROM driverStandings
        INNER JOIN drivers ON drivers.driverId=driverStandings.driverId;""")
    result = cursor.fetchall()
    cursor.close()
    return result

def get_constructor_standing_data(db):
    """ Get constructor data for checking changes. """
    cursor = db.cursor()
    cursor.execute("""
        SELECT * FROM constructorStandings
        INNER JOIN constructors ON
        constructors.constructorId=constructorStandings.constructorId;""")
    result = cursor.fetchall()
    cursor.close()
    return result
