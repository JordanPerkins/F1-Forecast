
""" The controllers for the information routes. """

import logging
import traceback
from flask import abort, jsonify
from ..common.db import Database

db = Database.get_database()

def season_calendar(year=None):
    """ Fetches the calendar of the specified year, or current season. """
    try:
        season_year = year
        race_round = None
        date = None
        race_id = None
        if season_year is None:
            season_year, race_round, race_id, date = db.get_next_race_year_round()

        logging.info("Fetching calendar for year %s", str(season_year))

        calendar = db.get_calendar(season_year)

        result = []
        for race in calendar:
            is_next_race = (race_round and race_round == race[3])
            result.append({
                'race_name': race[0],
                'race_date': race[1],
                'race_time': str(race[2]),
                'race_round': race[3],
                'circuit_name': race[4],
                'circuit_ref': race[5],
                'circuit_location': race[6],
                'circuit_country': race[7],
                'is_next_race': is_next_race
            })

        return jsonify({
            'year': season_year,
            'next_race_round': race_round,
            'next_race_id': race_id,
            'next_race_date': date,
            'calendar' : result
        })
    except Exception as err:
        logging.error('An error occurred fetching race calendar: %s', str(err))
        logging.debug(traceback.format_exc())
        abort(500, description="Internal Server Error")


def drivers_championship(year=None):
    """ Fetches the final driver's championship of the specified year,
        or the current standings. """
    try:
        if year is None:
            race_id = db.get_last_race_id()
        else:
            race_id = db.get_last_race_id_in_year(year)

        logging.info("Fetching drivers standings for race_id %s", str(race_id))

        result = []

        if race_id is None:
            race_name = None
            race_year = None
        else:
            race_name, race_year = db.get_race_by_id(race_id)

            standings = db.get_drivers_standings(race_id)

            for driver in standings:
                result.append({
                    'driver_id': driver[0],
                    'driver_ref': driver[1],
                    'driver_number': driver[2],
                    'driver_code': driver[3],
                    'driver_forename': driver[4],
                    'driver_surname': driver[5],
                    'driver_dob': driver[6],
                    'driver_nationality': driver[7],
                    'driver_url': driver[8],
                    'driver_points': driver[9],
                    'driver_wins': driver[10],
                    'driver_position': driver[11],
                })

        return jsonify({
            'last_race_id': race_id,
            'last_race_name': race_name,
            'last_race_year': race_year,
            'standings' : result
        })
    except Exception as err:
        logging.error('An error occurred fetching drivers standings: %s', str(err))
        logging.debug(traceback.format_exc())
        abort(500, description="Internal Server Error")


def constructors_championship(year=None):
    """ Fetches the final constructors's championship of the
        specified year, or the current standings. """
    try:
        if year is None:
            race_id = db.get_last_race_id()
        else:
            race_id = db.get_last_race_id_in_year(year)

        logging.info("Fetching drivers standings for race_id %s", str(race_id))

        result = []

        if race_id is None:
            race_name = None
            race_year = None
        else:
            race_name, race_year = db.get_race_by_id(race_id)

            standings = db.get_constructors_standings(race_id)

            for constructor in standings:
                result.append({
                    'constructor_id': constructor[0],
                    'constructor_ref': constructor[1],
                    'constructor_name': constructor[2],
                    'constructor_nationality': constructor[3],
                    'constructor_url': constructor[4],
                    'constructor_points': constructor[5],
                    'constructor_wins': constructor[6],
                    'constructor_position': constructor[7]
                })

        return jsonify({
            'last_race_id': race_id,
            'last_race_name': race_name,
            'last_race_year': race_year,
            'standings' : result
        })
    except Exception as err:
        logging.error('An error occurred fetching constructors standings: %s', str(err))
        logging.debug(traceback.format_exc())
        abort(500, description="Internal Server Error")


def race_results(race=None):
    """ Fetches the results of the last or specified race. """
    try:
        if race:
            race_id = race
        else:
            race_id = db.get_last_race_id()

        logging.info("Fetching results for race_id %s", str(race_id))

        race_name, race_year = db.get_race_by_id(race_id)

        results = db.get_race_results(race_id)

        result = []
        for race_result in results:
            result.append({
                'driver_id': race_result[0],
                'result_id': race_result[1],
                'driver_ref': race_result[2],
                'driver_number': race_result[3],
                'driver_code': race_result[4],
                'driver_forename': race_result[5],
                'driver_surname': race_result[6],
                'driver_dob': race_result[7],
                'driver_nationality': race_result[8],
                'driver_url': race_result[9],
                'race_grid': race_result[10],
                'race_position': race_result[11],
                'race_points': race_result[12],
                'race_laps': race_result[13]
            })

        return jsonify({
            'last_race_id': race_id,
            'last_race_name': race_name,
            'last_race_year': race_year,
            'results' : result
        })
    except Exception as err:
        logging.error('An error occurred fetching last race results: %s', str(err))
        logging.debug(traceback.format_exc())
        abort(500, description="Internal Server Error")

def qualifying_results(race=None):
    """ Fetches the results of qualifying in the last or specified race. """
    try:
        if race:
            race_id = race
        else:
            race_id = db.get_last_qualifying_race_id()

        logging.info("Fetching qualifying results for race_id %s", str(race_id))

        race_name, race_year = db.get_race_by_id(race_id)

        results = db.get_qualifying_results(race_id)

        result = []
        for qualifying_result in results:
            result.append({
                'driver_id': qualifying_result[0],
                'qualify_id': qualifying_result[1],
                'driver_ref': qualifying_result[2],
                'driver_number': qualifying_result[3],
                'driver_code': qualifying_result[4],
                'driver_forename': qualifying_result[5],
                'driver_surname': qualifying_result[6],
                'driver_dob': qualifying_result[7],
                'driver_nationality': qualifying_result[8],
                'driver_url': qualifying_result[9],
                'qualifying_position': qualifying_result[10],
                'qualifying_q1': qualifying_result[11],
                'qualifying_q2': qualifying_result[12],
                'qualifying_q3': qualifying_result[13]
            })

        return jsonify({
            'last_race_id': race_id,
            'last_race_name': race_name,
            'last_race_year': race_year,
            'results' : result
        })
    except Exception as err:
        logging.error('An error occurred fetching last qualifying results: %s', str(err))
        logging.debug(traceback.format_exc())
        abort(500, description="Internal Server Error")
