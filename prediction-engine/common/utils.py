import math
from collections import defaultdict 
from operator import itemgetter 
from itertools import groupby 

def convert_to_deltas(results):
    laps_in_seconds = [(float(item.split(':')[0])*60 + float(item.split(':')[1])) if item is not None else None for item in results]
    fastest_lap = min([item for item in laps_in_seconds if item is not None])
    return [round(item - fastest_lap, 3) if item is not None else None for item in laps_in_seconds], fastest_lap

def deltas_to_ranking(deltas):
    deltas_with_inf = [item if item is not None else math.inf for item in deltas]
    lap_ordering = sorted(range(len(deltas_with_inf)), key=deltas_with_inf.__getitem__)
    ranking = sorted(range(len(lap_ordering)), key=lap_ordering.__getitem__)
    return [ranking + 1 for ranking in ranking]

def process_qualifying_results(results):
    deltas, fastest_lap = convert_to_deltas(results)
    deltas_without_none = [item for item in deltas if item is not None]
    delta_average = sum(deltas_without_none) / len(deltas_without_none)
    deltas_with_none_replaced = [item if item is not None else delta_average for item in deltas]
    ranking = deltas_to_ranking(deltas)
    return deltas_with_none_replaced, ranking, fastest_lap

def get_result_as_tuples(predictions, number_of_drivers):
    by_position = {}
    for pred_dict in predictions:
        for position in range(0, number_of_drivers):
            if position not in by_position:
                by_position[position] = []
            by_position[position].append(pred_dict['probabilities'][position].item())
    
    result = []
    for position, values in by_position.items():
        total = sum(values)
        result.extend([(position, index, (value / total)) for index, value in enumerate(values)])
    return result

def results_to_ranking(predictions, number_of_drivers):
    ranked_drivers = []
    ranked_positions = []
    ranking = []
    tuples = get_result_as_tuples(predictions, number_of_drivers)
    while len(ranking) < number_of_drivers:
        max_tuple = max(tuples, key=lambda item: item[2])
        ranked_positions.append(max_tuple[0])
        ranked_drivers.append(max_tuple[1])
        ranking.append(max_tuple)
        tuples = [item for item in tuples if item[0] not in ranked_positions and item[1] not in ranked_drivers]
    sorted_ranking = sorted(ranking, key=lambda item: item[0])
    return sorted_ranking

def tuples_to_dictionary(tuples):
    result = {}
    for item in tuples:
        if item[0] not in result:
            result[item[0]] = []
        result[item[0]].append(item[1:])
    return result

