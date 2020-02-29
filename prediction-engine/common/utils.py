
import numpy as np

def convert_to_deltas(results):
    laps_in_seconds = [float(item.split(':')[0])*60 + float(item.split(':')[1]) for item in results]
    fastest_lap = min(laps_in_seconds)
    print(fastest_lap)
    return [round(item - fastest_lap, 3) for item in laps_in_seconds]

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
        tuples = list(filter(lambda x: (x[0] not in ranked_positions and x[1] not in ranked_drivers), tuples))
    sorted_ranking = sorted(ranking, key=lambda item: item[0])
    return sorted_ranking

def deltas_to_ranking(deltas):
    lap_ordering = sorted(range(len(deltas)), key=deltas.__getitem__)
    ranking = sorted(range(len(lap_ordering)), key=lap_ordering.__getitem__)
    return [ranking + 1 for ranking in ranking]