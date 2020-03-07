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

