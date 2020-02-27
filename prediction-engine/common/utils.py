

def convert_to_deltas(results):
    laps_in_seconds = [float(item.split(':')[0])*60 + float(item.split(':')[1]) for item in results]
    fastest_lap = min(laps_in_seconds)
    print(fastest_lap)
    return [round(item - fastest_lap, 3) for item in laps_in_seconds]


def results_to_ranking(results):
    