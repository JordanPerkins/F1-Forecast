import math
from collections import defaultdict 
from operator import itemgetter 
from itertools import groupby 

def replace_none_with_average(data, rounding=3):
    data_none_removed = [float(item) for item in data if item is not None]
    average = 0
    if len(data_none_removed):
        average = round(sum(data_none_removed) / len(data_none_removed), rounding)
    return [float(item) if item is not None else average for item in data]

def tuples_to_dictionary(tuples):
    result = {}
    for item in tuples:
        if item[0] not in result:
            result[item[0]] = []
        result[item[0]].append(item[1:])
    return result


def ranking_to_dictionary(ranking):
    result = []
    for driver in ranking:
        driver_quali_result = float(driver[-1]) if len(driver) > 9 else None
        result.append({
            'driver_id': driver[0],
            'driver_ref': driver[1],
            'driver_num': driver[2],
            'driver_code': driver[3],
            'driver_forename': driver[4],
            'driver_surname': driver[5],
            'driver_dob': driver[6],
            'driver_nationality': driver[7],
            'driver_wiki': driver[8],
            'driver_quali_result': driver_quali_result
        })
    return result

