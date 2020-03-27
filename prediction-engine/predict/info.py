
import json
from flask import abort, jsonify
from ..common.db import Database
import logging
import traceback

db = Database.get_database()

def calendar(year=None):
    try:
        season_year = year
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