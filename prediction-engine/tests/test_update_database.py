""" Tests the database updating system """

import os
import unittest
from decimal import Decimal
import mysql.connector as mysql

from ..update.update_database import *
from .utils import *

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
    """ Tests class. """

    def setUp(self):
        """ Clear tables before each test. """
        truncate_table(db, 'races')
        truncate_table(db, 'circuits')
        truncate_table(db, 'results')
        truncate_table(db, 'qualifying')
        truncate_table(db, 'drivers')
        truncate_table(db, 'constructors')
        truncate_table(db, 'driverStandings')
        truncate_table(db, 'constructorStandings')

    def test_check_for_calendar_updates(self):
        """ Check calendar is updated. """
        insert_initial_data(db, 2018)
        insert_initial_circuit_data(db)
        result = check_for_calendar_updates()
        self.assertEqual(result, 21)
        data = get_race_data(db)
        self.assertEqual(len(data), 22)
        self.assertEqual(data[1], (2, 2019, 1, 2, 'Australian Grand Prix',
                                   datetime.date(2019, 3, 17), datetime.timedelta(seconds=18600),
                                   'https://en.wikipedia.org/wiki/2019_Australian_Grand_Prix', None,
                                   None, None, 2, 'albert_park',
                                   'Albert Park Grand Prix Circuit', 'Melbourne', 'Australia',
                                   -37.8497, 144.968, None,
                                   'http://en.wikipedia.org/wiki/Melbourne_Grand_Prix_Circuit'))
        self.assertEqual(data[2], (3, 2019, 2, 1, 'Bahrain Grand Prix',
                                   datetime.date(2019, 3, 31), datetime.timedelta(seconds=54600),
                                   'https://en.wikipedia.org/wiki/2019_Bahrain_Grand_Prix', None,
                                   None, None, 1, 'bahrain',
                                   'Bahrain International Circuit', None, None, None,
                                   None, None, ''))

    def test_check_for_calendar_updates_with_missing_season(self):
        """ Check no data is handled gracefully. """
        insert_initial_data(db, 2050)
        result = check_for_calendar_updates()
        self.assertEqual(result, 0)
        data = get_race_data(db)
        self.assertEqual(len(data), 0)

    def test_check_for_races(self):
        """ Check race results are added. """
        insert_initial_data(db, 2019, 4)
        insert_initial_data(db, 2019, 5)
        insert_initial_results_data(db)
        insert_initial_driver_data(db)
        insert_initial_constructor_data(db)
        result = check_for_races()
        self.assertEqual(result, 20)
        data = get_result_data(db)
        self.assertEqual(len(data), 20)
        self.assertEqual(data[0], (2, 2, 2, 2, 44, 2, 1, '1', 1, 26.0, 66, '1:35:50.443', 5750443,
                                   54, 1, '1:18.492', '213.499', 1, 2, 'hamilton', 44, 'HAM',
                                   'Lewis', 'Hamilton', datetime.date(1985, 1, 7), 'British',
                                   'http://en.wikipedia.org/wiki/Lewis_Hamilton', 2, 'mercedes',
                                   'Mercedes', 'German',
                                   'http://en.wikipedia.org/wiki/Mercedes-Benz_in_Formula_One'))
        self.assertEqual(data[1], (3, 2, 1, 2, 77, 1, 2, '2', 2, 18.0, 66, '+4.074', 5754517, 55,
                                   2, '1:18.737', '212.835', 1, 1, 'bottas', None, None, '', '',
                                   None, None, '', 2, 'mercedes', 'Mercedes', 'German',
                                   'http://en.wikipedia.org/wiki/Mercedes-Benz_in_Formula_One'))
        self.assertEqual(data[2], (4, 2, 3, 1, 33, 4, 3, '3', 3, 15.0, 66, '+7.679', 5758122, 57,
                                   3, '1:19.769', '210.081', 1, 3, 'max_verstappen', 33, 'VER',
                                   'Max', 'Verstappen', datetime.date(1997, 9, 30), 'Dutch',
                                   'http://en.wikipedia.org/wiki/Max_Verstappen', 1,
                                   'red_bull', '', None, ''))

    def test_check_for_races_with_missing_season(self):
        """ Check no data is handled gracefully. """
        insert_initial_data(db, 2019, 4)
        insert_initial_data(db, 2050, 5)
        insert_initial_results_data(db)
        insert_initial_driver_data(db)
        insert_initial_constructor_data(db)
        result = check_for_races()
        self.assertEqual(result, 0)

    def test_check_for_qualifying(self):
        """ Check qualifying results are added. """
        insert_initial_data(db, 2019, 4)
        insert_initial_data(db, 2019, 5)
        insert_initial_qualifying_data(db)
        insert_initial_driver_data(db)
        insert_initial_constructor_data(db)
        result = check_for_qualifying()
        self.assertEqual(result, 20)
        data = get_qualifying_data(db)
        self.assertEqual(len(data), 20)
        self.assertEqual(data[0], (2, 2, 1, 2, 77, 1, '1:16.979', '1:15.924', '1:15.406',
                                   Decimal('76.979'), Decimal('75.924'), Decimal('75.406'),
                                   1, 'bottas', None, None, '', '', None, None, '', 2,
                                   'mercedes', 'Mercedes', 'German',
                                   'http://en.wikipedia.org/wiki/Mercedes-Benz_in_Formula_One'))
        self.assertEqual(data[1], (3, 2, 2, 2, 44, 2, '1:17.292', '1:16.038', '1:16.040',
                                   Decimal('77.292'), Decimal('76.038'), Decimal('76.040'), 2,
                                   'hamilton', 44, 'HAM', 'Lewis', 'Hamilton',
                                   datetime.date(1985, 1, 7), 'British',
                                   'http://en.wikipedia.org/wiki/Lewis_Hamilton', 2, 'mercedes',
                                   'Mercedes', 'German',
                                   'http://en.wikipedia.org/wiki/Mercedes-Benz_in_Formula_One'))
        self.assertEqual(data[2], (4, 2, 3, 3, 5, 3, '1:17.425', '1:16.667', '1:16.272',
                                   Decimal('77.425'), Decimal('76.667'), Decimal('76.272'), 3,
                                   'vettel', 5, 'VET', 'Sebastian', 'Vettel',
                                   datetime.date(1987, 7, 3),
                                   'German', 'http://en.wikipedia.org/wiki/Sebastian_Vettel', 3,
                                   'ferrari', 'Ferrari', 'Italian',
                                   'http://en.wikipedia.org/wiki/Scuderia_Ferrari'))

    def test_check_for_qualifying_with_missing_season(self):
        """ Check no data is handled gracefully. """
        insert_initial_data(db, 2019, 4)
        insert_initial_data(db, 2050, 5)
        insert_initial_qualifying_data(db)
        insert_initial_driver_data(db)
        insert_initial_constructor_data(db)
        result = check_for_qualifying()
        self.assertEqual(result, 0)

    def test_check_for_driver_standing(self):
        """ Check driver standing results are added. """
        insert_initial_data(db, 2019, 4)
        insert_initial_data(db, 2019, 5)
        insert_initial_driver_standing_data(db)
        insert_initial_driver_data(db)
        result = check_for_drivers_standings()
        self.assertEqual(result, 20)
        data = get_driver_standing_data(db)
        self.assertEqual(len(data), 20)
        self.assertEqual(data[0], (2, 2, 2, 112.0, 1, '1', 3, 2, 'hamilton', 44, 'HAM', 'Lewis',
                                   'Hamilton', datetime.date(1985, 1, 7), 'British',
                                   'http://en.wikipedia.org/wiki/Lewis_Hamilton'))
        self.assertEqual(data[1], (3, 2, 1, 105.0, 2, '2', 2, 1, 'bottas', None, None, '', '',
                                   None, None, ''))
        self.assertEqual(data[2], (4, 2, 3, 66.0, 3, '3', 0, 3, 'max_verstappen', 33, 'VER', 'Max',
                                   'Verstappen', datetime.date(1997, 9, 30), 'Dutch',
                                   'http://en.wikipedia.org/wiki/Max_Verstappen'))

    def test_check_for_driver_standing_with_missing_season(self):
        """ Check no data is handled gracefully. """
        insert_initial_data(db, 2019, 4)
        insert_initial_data(db, 2050, 5)
        insert_initial_driver_standing_data(db)
        insert_initial_driver_data(db)
        result = check_for_drivers_standings()
        self.assertEqual(result, 0)

    def test_check_for_constructor_standing(self):
        """ Check constructor standing results are added. """
        insert_initial_data(db, 2019, 4)
        insert_initial_data(db, 2019, 5)
        insert_initial_constructor_standing_data(db)
        insert_initial_constructor_data(db)
        result = check_for_constructor_standings()
        self.assertEqual(result, 10)
        data = get_constructor_standing_data(db)
        self.assertEqual(len(data), 10)
        self.assertEqual(data[0], (2, 2, 2, 217.0, 1, '1', 5, 2, 'mercedes', 'Mercedes', 'German',
                                   'http://en.wikipedia.org/wiki/Mercedes-Benz_in_Formula_One'))
        self.assertEqual(data[1], (3, 2, 3, 121.0, 2, '2', 0, 3, 'ferrari', 'Ferrari', 'Italian',
                                   'http://en.wikipedia.org/wiki/Scuderia_Ferrari'))
        self.assertEqual(data[2], (4, 2, 1, 87.0, 3, '3', 0, 1, 'red_bull', '', None, ''))

    def test_check_for_constructor_standing_with_missing_season(self):
        """ Check no data is handled gracefully. """
        insert_initial_data(db, 2019, 4)
        insert_initial_data(db, 2050, 5)
        insert_initial_constructor_standing_data(db)
        insert_initial_constructor_data(db)
        result = check_for_constructor_standings()
        self.assertEqual(result, 0)

if __name__ == '__main__':
    unittest.main()
