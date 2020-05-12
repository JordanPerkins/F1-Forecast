""" Tests the information routes """

import os
import unittest
import datetime
import json
import mysql.connector as mysql

from .utils import *
from ..predict.app import application as app

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

class TestInfoRoutes(unittest.TestCase):
    """ Tests class. """

    def setUp(self):
        truncate_table(db, 'races')
        truncate_table(db, 'circuits')
        truncate_table(db, 'results')
        truncate_table(db, 'qualifying')
        truncate_table(db, 'drivers')
        truncate_table(db, 'constructors')
        truncate_table(db, 'driverStandings')
        truncate_table(db, 'constructorStandings')
        app.config['TESTING'] = True
        app.config['DEBUG'] = False
        self.app = app.test_client()

    def test_season_calendar(self):
        """ Tests season calendar route. """
        insert_initial_circuit_data(db)
        insert_initial_data(db, 2017, 1, 'First GP 2017')
        insert_initial_data(db, 2018, 1, 'First GP')
        insert_initial_data(db, 2018, 2, 'Second GP')
        insert_initial_data(db, 2018, 3, 'Third GP')
        insert_initial_results_data(db)
        response = self.app.get('/info/calendar')
        self.assertEqual(response.status_code, 200)
        json_response = json.loads(response.get_data(as_text=True))
        self.assertEqual(
            json_response,
            {'calendar': [
                {'circuit_country': None, 'circuit_location': None,
                 'circuit_name': 'Bahrain International Circuit',
                 'circuit_ref': 'bahrain', 'is_next_race': True,
                 'race_date': 'Tue, 12 May 2020 00:00:00 GMT',
                 'race_name': 'First GP', 'race_round': 1,
                 'race_time': 'None'},
                {'circuit_country': None, 'circuit_location': None,
                 'circuit_name': 'Bahrain International Circuit',
                 'circuit_ref': 'bahrain', 'is_next_race': False,
                 'race_date': 'Tue, 12 May 2020 00:00:00 GMT',
                 'race_name': 'Second GP', 'race_round': 2,
                 'race_time': 'None'},
                {'circuit_country': None, 'circuit_location': None,
                 'circuit_name': 'Bahrain International Circuit',
                 'circuit_ref': 'bahrain', 'is_next_race': False,
                 'race_date': 'Tue, 12 May 2020 00:00:00 GMT',
                 'race_name': 'Third GP', 'race_round': 3,
                 'race_time': 'None'}
            ],
             'next_race_date': 'Tue, 12 May 2020 00:00:00 GMT',
             'next_race_id': 2, 'next_race_round': 1, 'year': 2018}
        )

    def test_season_calendar_with_year(self):
        """ Test season calendar route with year. """
        insert_initial_circuit_data(db)
        insert_initial_data(db, 2017, 1, 'First GP 2017')
        insert_initial_data(db, 2018, 1, 'First GP')
        insert_initial_data(db, 2018, 2, 'Second GP')
        insert_initial_data(db, 2018, 3, 'Third GP')
        insert_initial_results_data(db)
        response = self.app.get('/info/calendar/2017')
        self.assertEqual(response.status_code, 200)
        json_response = json.loads(response.get_data(as_text=True))
        self.assertEqual(
            json_response,
            {'calendar': [
                {'circuit_country': None, 'circuit_location': None,
                 'circuit_name': 'Bahrain International Circuit',
                 'circuit_ref': 'bahrain', 'is_next_race': None,
                 'race_date': 'Tue, 12 May 2020 00:00:00 GMT',
                 'race_name': 'First GP 2017', 'race_round': 1,
                 'race_time': 'None'}
            ],
             'next_race_date': None, 'next_race_id': None,
             'next_race_round': None, 'year': 2017}
        )

    def test_results(self):
        """ Test results route. """
        insert_initial_driver_data(db)
        insert_initial_constructor_data(db)
        insert_initial_data(db, 2018, 1, 'First GP')
        insert_initial_results_data(db, 1, 1, 1, 1)
        insert_initial_results_data(db, 1, 1, 1, 2)
        response = self.app.get('/info/results/race')
        self.assertEqual(response.status_code, 200)
        json_response = json.loads(response.get_data(as_text=True))
        self.assertEqual(
            json_response,
            {'last_race_id': 1, 'last_race_name': 'first gp',
             'last_race_year': 2018,
             'results': [
                 {'driver_code': None, 'driver_dob': None,
                  'driver_forename': '', 'driver_id': 1,
                  'driver_nationality': None,
                  'driver_number': None, 'driver_ref': 'bottas',
                  'driver_surname': '', 'driver_url': '', 'race_grid': 0,
                  'race_laps': 0, 'race_points': 0.0,
                  'race_position': 1, 'result_id': 1},
                 {'driver_code': None, 'driver_dob': None,
                  'driver_forename': '', 'driver_id': 1,
                  'driver_nationality': None, 'driver_number': None,
                  'driver_ref': 'bottas',
                  'driver_surname': '', 'driver_url': '', 'race_grid': 0,
                  'race_laps': 0, 'race_points': 0.0,
                  'race_position': 2, 'result_id': 2}
             ]
            }
        )

    def test_results_with_id(self):
        """ Test results route with ID. """
        insert_initial_driver_data(db)
        insert_initial_constructor_data(db)
        insert_initial_data(db, 2017, 1, 'First GP 2017')
        insert_initial_data(db, 2018, 1, 'First GP')
        insert_initial_results_data(db, 1, 1, 1, 1)
        insert_initial_results_data(db, 1, 1, 1, 2)
        response = self.app.get('/info/results/race/1')
        self.assertEqual(response.status_code, 200)
        json_response = json.loads(response.get_data(as_text=True))
        self.assertEqual(
            json_response,
            {'last_race_id': 1, 'last_race_name': 'first gp 2017',
             'last_race_year': 2017,
             'results': [
                 {'driver_code': None, 'driver_dob': None,
                  'driver_forename': '', 'driver_id': 1,
                  'driver_nationality': None, 'driver_number': None,
                  'driver_ref': 'bottas', 'driver_surname': '',
                  'driver_url': '', 'race_grid': 0, 'race_laps': 0,
                  'race_points': 0.0, 'race_position': 1,
                  'result_id': 1},
                 {'driver_code': None, 'driver_dob': None,
                  'driver_forename': '', 'driver_id': 1,
                  'driver_nationality': None, 'driver_number': None,
                  'driver_ref': 'bottas', 'driver_surname': '',
                  'driver_url': '', 'race_grid': 0, 'race_laps': 0,
                  'race_points': 0.0, 'race_position': 2,
                  'result_id': 2}
             ]
            }
        )

    def test_qualifying(self):
        """ Test qualifying route. """
        insert_initial_driver_data(db)
        insert_initial_constructor_data(db)
        insert_initial_data(db, 2018, 1, 'First GP')
        insert_initial_qualifying_data(db, 1, 1, 1, 1)
        insert_initial_qualifying_data(db, 1, 1, 1, 2)
        response = self.app.get('/info/results/qualifying')
        self.assertEqual(response.status_code, 200)
        json_response = json.loads(response.get_data(as_text=True))
        self.assertEqual(
            json_response,
            {'last_race_id': 1, 'last_race_name': 'first gp',
             'last_race_year': 2018, 'results': [
                 {'driver_code': None, 'driver_dob': None, 'driver_forename': '',
                  'driver_id': 1, 'driver_nationality': None, 'driver_number': None,
                  'driver_ref': 'bottas', 'driver_surname': '',
                  'driver_url': '', 'qualify_id': 1, 'qualifying_position': 1,
                  'qualifying_q1': None,
                  'qualifying_q2': None, 'qualifying_q3': None},
                 {'driver_code': None, 'driver_dob': None, 'driver_forename': '',
                  'driver_id': 1, 'driver_nationality': None, 'driver_number': None,
                  'driver_ref': 'bottas', 'driver_surname': '', 'driver_url': '',
                  'qualify_id': 2, 'qualifying_position': 2, 'qualifying_q1': None,
                  'qualifying_q2': None, 'qualifying_q3': None}
             ]
            }
        )

    def test_qualifying_with_id(self):
        """ Test qualifying route with ID. """
        insert_initial_driver_data(db)
        insert_initial_constructor_data(db)
        insert_initial_data(db, 2017, 1, 'First GP 2017')
        insert_initial_data(db, 2018, 1, 'First GP')
        insert_initial_qualifying_data(db, 1, 1, 1, 1)
        insert_initial_qualifying_data(db, 1, 1, 1, 2)
        response = self.app.get('/info/results/qualifying/1')
        self.assertEqual(response.status_code, 200)
        json_response = json.loads(response.get_data(as_text=True))
        self.assertEqual(
            json_response,
            {'last_race_id': 1, 'last_race_name': 'first gp 2017',
             'last_race_year': 2017,
             'results': [
                 {'driver_code': None, 'driver_dob': None, 'driver_forename': '',
                  'driver_id': 1, 'driver_nationality': None, 'driver_number': None,
                  'driver_ref': 'bottas', 'driver_surname': '', 'driver_url': '',
                  'qualify_id': 1, 'qualifying_position': 1, 'qualifying_q1': None,
                  'qualifying_q2': None, 'qualifying_q3': None},
                 {'driver_code': None, 'driver_dob': None, 'driver_forename': '',
                  'driver_id': 1, 'driver_nationality': None, 'driver_number': None,
                  'driver_ref': 'bottas', 'driver_surname': '', 'driver_url': '',
                  'qualify_id': 2, 'qualifying_position': 2, 'qualifying_q1': None,
                  'qualifying_q2': None, 'qualifying_q3': None}
             ]
            }
        )

    def test_championship(self):
        """ Test championship route. """
        insert_initial_driver_data(db)
        insert_initial_constructor_data(db)
        insert_initial_data(db, 2018, 1, 'First GP')
        insert_initial_results_data(db, 1, 1, 1, 1)
        insert_initial_results_data(db, 1, 1, 1, 2)
        insert_initial_driver_standing_data(db, 1, 1, 1)
        insert_initial_driver_standing_data(db, 1, 1, 2)
        response = self.app.get('/info/championship/drivers')
        self.assertEqual(response.status_code, 200)
        json_response = json.loads(response.get_data(as_text=True))
        self.assertEqual(
            json_response,
            {'last_race_id': 1, 'last_race_name': 'first gp',
             'last_race_year': 2018,
             'standings': [
                 {'driver_code': None,
                  'driver_dob': None, 'driver_forename': '', 'driver_id': 1,
                  'driver_nationality': None, 'driver_number': None,
                  'driver_points': 0.0, 'driver_position': 1, 'driver_ref': 'bottas',
                  'driver_surname': '', 'driver_url': '', 'driver_wins': 0},
                 {'driver_code': None, 'driver_dob': None, 'driver_forename': '',
                  'driver_id': 1, 'driver_nationality': None, 'driver_number': None,
                  'driver_points': 0.0, 'driver_position': 2,
                  'driver_ref': 'bottas', 'driver_surname': '',
                  'driver_url': '', 'driver_wins': 0}
             ]
            }
        )

    def test_championship_with_year(self):
        """ Test championship route with year. """
        insert_initial_driver_data(db)
        insert_initial_constructor_data(db)
        insert_initial_data(db, 2017, 1, 'First GP 2017')
        insert_initial_data(db, 2018, 1, 'First GP')
        insert_initial_results_data(db, 1, 1, 1, 1)
        insert_initial_results_data(db, 1, 1, 1, 2)
        insert_initial_driver_standing_data(db, 1, 1, 1)
        insert_initial_driver_standing_data(db, 1, 1, 2)
        response = self.app.get('/info/championship/drivers/2017')
        self.assertEqual(response.status_code, 200)
        json_response = json.loads(response.get_data(as_text=True))
        self.assertEqual(
            json_response,
            {'last_race_id': 1, 'last_race_name': 'first gp 2017',
             'last_race_year': 2017, 'standings': [
                 {'driver_code': None, 'driver_dob': None, 'driver_forename': '',
                  'driver_id': 1, 'driver_nationality': None, 'driver_number': None,
                  'driver_points': 0.0, 'driver_position': 1, 'driver_ref': 'bottas',
                  'driver_surname': '', 'driver_url': '', 'driver_wins': 0},
                 {'driver_code': None, 'driver_dob': None, 'driver_forename': '',
                  'driver_id': 1, 'driver_nationality': None, 'driver_number': None,
                  'driver_points': 0.0, 'driver_position': 2, 'driver_ref': 'bottas',
                  'driver_surname': '', 'driver_url': '', 'driver_wins': 0}
             ]
            }
        )

    def test_championship_constructors(self):
        """ Test constructors route. """
        insert_initial_driver_data(db)
        insert_initial_constructor_data(db)
        insert_initial_data(db, 2018, 1, 'First GP')
        insert_initial_results_data(db, 1, 1, 1, 1)
        insert_initial_results_data(db, 1, 1, 1, 2)
        insert_initial_constructor_standing_data(db, 1, 1, 1)
        insert_initial_constructor_standing_data(db, 1, 1, 2)
        response = self.app.get('/info/championship/constructors')
        self.assertEqual(response.status_code, 200)
        json_response = json.loads(response.get_data(as_text=True))
        self.assertEqual(
            json_response,
            {'last_race_id': 1, 'last_race_name': 'first gp',
             'last_race_year': 2018, 'standings': [
                 {'constructor_id': 1, 'constructor_name': '',
                  'constructor_nationality': None, 'constructor_points': 0.0,
                  'constructor_position': 1, 'constructor_ref': 'red_bull',
                  'constructor_url': '', 'constructor_wins': 0},
                 {'constructor_id': 1, 'constructor_name': '',
                  'constructor_nationality': None, 'constructor_points': 0.0,
                  'constructor_position': 2, 'constructor_ref': 'red_bull',
                  'constructor_url': '', 'constructor_wins': 0}
             ]
            }
        )

    def test_championship_constructors_with_year(self):
        """ Test constructors route with year. """
        insert_initial_driver_data(db)
        insert_initial_constructor_data(db)
        insert_initial_data(db, 2017, 1, 'First GP 2017')
        insert_initial_data(db, 2018, 1, 'First GP')
        insert_initial_results_data(db, 1, 1, 1, 1)
        insert_initial_results_data(db, 1, 1, 1, 2)
        insert_initial_constructor_standing_data(db, 1, 1, 1)
        insert_initial_constructor_standing_data(db, 1, 1, 2)
        response = self.app.get('/info/championship/constructors/2017')
        self.assertEqual(response.status_code, 200)
        json_response = json.loads(response.get_data(as_text=True))
        self.assertEqual(
            json_response,
            {'last_race_id': 1, 'last_race_name': 'first gp 2017',
             'last_race_year': 2017, 'standings': [
                 {'constructor_id': 1, 'constructor_name': '',
                  'constructor_nationality': None, 'constructor_points': 0.0,
                  'constructor_position': 1, 'constructor_ref': 'red_bull',
                  'constructor_url': '', 'constructor_wins': 0},
                 {'constructor_id': 1, 'constructor_name': '',
                  'constructor_nationality': None, 'constructor_points': 0.0,
                  'constructor_position': 2, 'constructor_ref': 'red_bull',
                  'constructor_url': '', 'constructor_wins': 0}
             ]
            }
        )

if __name__ == '__main__':
    unittest.main()
