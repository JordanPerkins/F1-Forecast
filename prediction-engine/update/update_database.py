from ..common.db import Database
from ..common.utils import tuples_to_dictionary
import requests
import logging
import datetime

db = Database.get_database()

ERGAST_API_URL = 'https://ergast.com/api/f1/'
EXPIRY_DELTA_DAYS = 5

def insert_driver(driver):
    driver_id = db.insert_driver(
        driver['driverId'],
        driver['permanentNumber'],
        driver['code'],
        driver['givenName'],
        driver['familyName'],
        driver['dateOfBirth'],
        driver['nationality'],
        driver['url']
    )
    logging.info("Inserted new driver: "+str(driver['driverId']))
    return driver_id

def insert_constructor(constructor):
    constructor_id = db.insert_constructor(
        constructor['constructorId'],
        constructor['name'],
        constructor['nationality'],
        constructor['url']
    )
    logging.info("Inserted new constructor: "+str(constructor['constructorId']))
    return constructor_id

def insert_circuit(circuit):
    circuit_id = db.insert_circuit(
        circuit['circuitId'],
        circuit['circuitName'],
        circuit['Location']['locality'],
        circuit['Location']['country'],
        circuit['Location']['lat'],
        circuit['Location']['long'],
        circuit['url']
    )
    logging.info("Inserted new circuit: "+str(circuit['circuitId']))
    return circuit_id

def insert_results(race_id, results):
    drivers = tuples_to_dictionary(db.get_driver_references())
    constructors = tuples_to_dictionary(db.get_constructors())
    total_inserted = 0
    for result in results:
        driver_id = (drivers[result['Driver']['driverId']][0][0]
            if result['Driver']['driverId'] in drivers 
            else insert_driver(result['Driver']))
        constructor_id = (constructors[result['Constructor']['constructorId']][0][0]
            if result['Constructor']['constructorId'] in constructors
            else insert_constructor(result['Constructor']))
        inserted = db.insert_result(
            race_id,
            driver_id,
            constructor_id,
            result['number'],
            result['grid'],
            result['position'],
            result['positionText'],
            result['position'],
            result['points'],
            result['laps'],
            result['Time']['time'],
            result['Time']['millis'],
            result['FastestLap']['lap'],
            result['FastestLap']['rank'],
            result['FastestLap']['Time']['time'],
            result['FastestLap']['AverageSpeed']['speed'],
            1
        )
        if inserted == 1:
            total_inserted += 1
    return total_inserted

def insert_qualifying_results(race_id, results):
    drivers = tuples_to_dictionary(db.get_driver_references())
    constructors = tuples_to_dictionary(db.get_constructor_references())
    total_inserted = 0
    for result in results:
        driver_id = (drivers[result['Driver']['driverId']][0][0]
            if result['Driver']['driverId'] in drivers 
            else insert_driver(result['Driver']))
        constructor_id = (constructors[result['Constructor']['constructorId']][0][0]
            if result['Constructor']['constructorId'] in constructors
            else insert_constructor(result['Constructor']))
        inserted = db.insert_qualifying(
            race_id,
            driver_id,
            constructor_id,
            result['number'],
            result['position'],
            result['Q1'],
            result['Q2'],
            result['Q3']
        )
        if inserted == 1:
            total_inserted += 1
    return total_inserted


def insert_calendar_updates(results):
    circuits = tuples_to_dictionary(db.get_circuit_references())
    total_inserted = 0
    for result in results:
        circuit_id = (circuit[result['Circuit']['circuitId']][0][0]
            if result['Circuit']['circuitId'] in circuits
            else insert_circuit(result['Circuit']))
        inserted = db.insert_race(
            result['season'],
            result['round'],
            circuit_id,
            result['raceName'],
            result['date'],
            result['time'],
            result['url']
        )
        if inserted == 1:
            total_inserted += 1
    return total_inserted


def check_for_races():
    year, race_round, race_id, date = db.get_next_race_year_round()
    expiry_date = date + datetime.timedelta(days = EXPIRY_DELTA_DAYS)
    if expiry_date <= datetime.date.today():
        logging.info("Fetch time for race "+str(race_id)+" has now expired - deleting record")
        db.delete_race(race_id)

    request = requests.get(ERGAST_API_URL+str(year)+'/'+str(race_round)+'/results.json')
    json = request.json()
    if 'MRData' in json:
        data = json['MRData']
        if int(data['total']) > 0 and 'RaceTable' in data and 'Races' in data['RaceTable'] and len(data['RaceTable']['Races']) > 0:
            if 'Results' in data['RaceTable']['Races'] and len(data['RaceTable']['Races']['Results']) > 0:
                results = data['RaceTable']['Races']['Results']
                return insert_results(race_id, results)
    return 0

def check_for_qualifying():
    year, race_round, race_id, date = db.get_next_race_year_round_qualifying()
    print(date)
    request = requests.get(ERGAST_API_URL+str(year)+'/'+str(race_round)+'/qualifying.json')
    json = request.json()
    if 'MRData' in json:
        data = json['MRData']
        if int(data['total']) > 0 and 'RaceTable' in data and 'Races' in data['RaceTable'] and len(data['RaceTable']['Races']) > 0:
            if 'QualifyingResults' in data['RaceTable']['Races'] and len(data['RaceTable']['Races']['QualifyingResults']) > 0:
                results = data['RaceTable']['Races']['QualifyingResults']
                return insert_qualifying_results(race_id, results)
    return 0

def check_for_calendar_updates():
    year = db.get_next_missing_season()
    request = requests.get(ERGAST_API_URL+str(year)+'.json')
    json = request.json()
    if 'MRData' in json:
        data = json['MRData']
        if int(data['total']) > 0 and 'RaceTable' in data and 'Races' in data['RaceTable'] and len(data['RaceTable']['Races']) > 0:
            results = data['RaceTable']['Races']
            return insert_calendar_updates(results)
    return 0


def check_for_database_updates():
    calendar = check_for_calendar_updates()
    logging.info("Added "+str(calendar)+" records")
    races = check_for_races()
    logging.info("Added "+str(races)+" race records")
    qualifying = check_for_qualifying()
    logging.info("Added "+str(qualifying)+" qualifying records")
