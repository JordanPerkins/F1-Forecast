
import json
from flask import abort, jsonify
from ..common.db import Database
import logging
import traceback

db = Database.get_database()

def calendar(year=None):
    try:
        season_year = year
        race_round = None
        date = None,
        race_id = None
        if season_year is None:
            season_year, race_round, race_id, date = db.get_next_race_year_round()

        logging.info("Fetching calendar for year "+str(season_year))

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
    except Exception as e:
        logging.error('An error occurred fetching race calendar: '+str(e))
        logging.debug(traceback.format_exc())
        abort(500, description="Internal Server Error")


def drivers_championship(year=None):
    try:
        if year is None:
            race_id = db.get_last_race_id()
        else:
            race_id = db.get_last_race_id_in_year(year)

        logging.info("Fetching drivers standings for race_id "+str(race_id))

        race_name, race_year = db.get_race_by_id(race_id)

        standings = db.get_drivers_standings(race_id)

        result = []
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
    except Exception as e:
        logging.error('An error occurred fetching drivers standings: '+str(e))
        logging.debug(traceback.format_exc())
        abort(500, description="Internal Server Error")


def constructors_championship(year=None):
    try:
        if year is None:
            race_id = db.get_last_race_id()
        else:
            race_id = db.get_last_race_id_in_year(year)

        logging.info("Fetching drivers standings for race_id "+str(race_id))

        race_name, race_year = db.get_race_by_id(race_id)

        standings = db.get_constructors_standings(race_id)

        result = []
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
    except Exception as e:
        logging.error('An error occurred fetching drivers standings: '+str(e))
        logging.debug(traceback.format_exc())
        abort(500, description="Internal Server Error")