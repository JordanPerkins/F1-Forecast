""" Tests the prediction routes """

import os
import unittest
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
        truncate_table(db, 'racePredictionLog')
        truncate_table(db, 'qualifyingPredictionLog')
        app.config['TESTING'] = True
        app.config['DEBUG'] = False
        self.app = app.test_client()

    def test_qualifying_prediction_route(self):
        """ Test qualifying prediction route. """
        insert_initial_data(db, 2019, 4)
        insert_initial_data(db, 2019, 5)
        insert_initial_qualifying_data(db, 1, 1, 1, 1)
        insert_initial_driver_data(db)
        insert_initial_driver_data(db, 'hamilton', 'hamilton')
        insert_initial_constructor_data(db)
        insert_qualifying_prediction_data(db, 2, 1, 1, 1)
        insert_qualifying_prediction_data(db, 2, 1, 2, 2)
        response = self.app.get('/predict/qualifying')
        json_response = json.loads(response.get_data(as_text=True))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            json_response,
            {'id': 2, 'name': '', 'result': [
                {'driver_code': None, 'driver_dob': None, 'driver_forename': '',
                 'driver_id': 1, 'driver_nationality': None, 'driver_num': None,
                 'driver_quali_result': 0.123, 'driver_ref': 'bottas', 'driver_surname': '',
                 'driver_wiki': ''},
                {'driver_code': None, 'driver_dob': None, 'driver_forename': '',
                 'driver_id': 2, 'driver_nationality': None, 'driver_num': None,
                 'driver_quali_result': 0.123, 'driver_ref': 'hamilton',
                 'driver_surname': '', 'driver_wiki': 'hamilton'}
                ],
             'year': 2019}
        )

    def test_qualifying_prediction_route_with_id(self):
        """ Test prediction route with ID. """
        insert_initial_data(db, 2019, 4)
        insert_initial_data(db, 2019, 5)
        insert_initial_qualifying_data(db, 1, 1, 1, 1)
        insert_initial_driver_data(db)
        insert_initial_driver_data(db, 'hamilton', 'hamilton')
        insert_initial_constructor_data(db)
        insert_qualifying_prediction_data(db, 1, 1, 1, 1)
        insert_qualifying_prediction_data(db, 1, 1, 2, 2)
        response = self.app.get('/predict/qualifying/1')
        json_response = json.loads(response.get_data(as_text=True))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            json_response,
            {'id': 1, 'name': '', 'result': [
                {'driver_code': None, 'driver_dob': None, 'driver_forename': '',
                 'driver_id': 1, 'driver_nationality': None, 'driver_num': None,
                 'driver_quali_result': 0.123, 'driver_ref': 'bottas', 'driver_surname': '',
                 'driver_wiki': ''},
                {'driver_code': None, 'driver_dob': None, 'driver_forename': '',
                 'driver_id': 2, 'driver_nationality': None, 'driver_num': None,
                 'driver_quali_result': 0.123, 'driver_ref': 'hamilton',
                 'driver_surname': '', 'driver_wiki': 'hamilton'}
                ],
             'year': 2019}
        )

    def test_race_prediction_route(self):
        """ Test race prediction route. """
        insert_initial_data(db, 2019, 4)
        insert_initial_data(db, 2019, 5)
        insert_initial_qualifying_data(db, 1, 1, 1, 1)
        insert_initial_qualifying_data(db, 1, 1, 1, 1)
        insert_initial_results_data(db, 1, 1, 1, 1)
        insert_initial_results_data(db, 1, 1, 1, 1)
        insert_initial_driver_data(db)
        insert_initial_driver_data(db, 'hamilton', 'hamilton')
        insert_initial_constructor_data(db)
        insert_qualifying_prediction_data(db, 2, 1, 1, 1)
        insert_qualifying_prediction_data(db, 2, 1, 2, 2)
        insert_race_prediction_data(db, 2, 1, 1)
        insert_race_prediction_data(db, 2, 2, 2)
        response = self.app.get('/predict/race')
        json_response = json.loads(response.get_data(as_text=True))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            json_response,
            {'id': 2, 'name': '', 'result': [
                {'driver_code': None, 'driver_dob': None, 'driver_forename': '',
                 'driver_id': 1, 'driver_nationality': None, 'driver_num': None,
                 'driver_quali_result': None, 'driver_ref': 'bottas',
                 'driver_surname': '', 'driver_wiki': ''},
                {'driver_code': None, 'driver_dob': None, 'driver_forename': '',
                 'driver_id': 2, 'driver_nationality': None, 'driver_num': None,
                 'driver_quali_result': None, 'driver_ref': 'hamilton',
                 'driver_surname': '', 'driver_wiki': 'hamilton'}
            ],
             'year': 2019}
        )

    def test_race_prediction_route_with_id(self):
        """ Test race prediction route with ID. """
        insert_initial_data(db, 2019, 4)
        insert_initial_data(db, 2019, 5)
        insert_initial_qualifying_data(db, 1, 1, 1, 1)
        insert_initial_qualifying_data(db, 1, 1, 1, 1)
        insert_initial_results_data(db, 1, 1, 1, 1)
        insert_initial_results_data(db, 1, 1, 1, 1)
        insert_initial_driver_data(db)
        insert_initial_driver_data(db, 'hamilton', 'hamilton')
        insert_initial_constructor_data(db)
        insert_qualifying_prediction_data(db, 1, 1, 1, 1)
        insert_qualifying_prediction_data(db, 1, 1, 2, 2)
        insert_race_prediction_data(db, 1, 1, 1, qualifying_predicted=False)
        insert_race_prediction_data(db, 1, 2, 2, qualifying_predicted=False)
        response = self.app.get('/predict/race/1')
        json_response = json.loads(response.get_data(as_text=True))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            json_response,
            {'id': 1, 'name': '', 'result': [
                {'driver_code': None, 'driver_dob': None, 'driver_forename': '',
                 'driver_id': 1, 'driver_nationality': None, 'driver_num': None,
                 'driver_quali_result': None, 'driver_ref': 'bottas',
                 'driver_surname': '', 'driver_wiki': ''},
                {'driver_code': None, 'driver_dob': None, 'driver_forename': '',
                 'driver_id': 2, 'driver_nationality': None, 'driver_num': None,
                 'driver_quali_result': None, 'driver_ref': 'hamilton',
                 'driver_surname': '', 'driver_wiki': 'hamilton'}
            ],
             'year': 2019}
        )

if __name__ == '__main__':
    unittest.main()
