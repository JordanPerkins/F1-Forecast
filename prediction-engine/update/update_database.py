from ..common.db import Database
import requests
import logging

db = Database.get_database()

ERGAST_API_URL = 'https://ergast.com/api/f1/'

def check_for_races():
    year, race_round = db.get_next_race_year_round()
    result = requests.get(ERGAST_API_URL+str(year)+'/'+str(race_round)+'/results.json')
    json = result.json()
    if 'MRData' in json:
        data = json['MRData']
        if int(data['total']) > 0 and 'RaceTable' in data and 'Races' in data['RaceTable'] and len(data['RaceTable']['Races']) > 0:   
            return 1
        return 0
    return 0


def check_for_database_updates():
    races = check_for_races()
    logging.info("Added "+str(races)+" race records")
