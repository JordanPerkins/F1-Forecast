import json
import tensorflow as tf
import numpy as np
from .models import retrieve_race_model
import logging
import traceback
from .db import Database
from .utils import replace_none_with_average
from .qualifying import predict as qualifying_predict

db = Database.get_database()

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

def predict(race_id):
    race = race_id
    if race is None:
        race = db.get_next_race_id()

    race_name = db.get_race_name(race)

    logging.info("Making prediction for race with ID "+str(race)+" and name "+str(race_name))

    qualifying_results = db.get_qualifying_results_with_driver(race)
    if len(qualifying_results) > 0:
        drivers_to_predict = [list(result)[:len(result) - 2] for result in qualifying_results]
        qualifying_grid = [int(list(result)[len(result) - 2]) for result in qualifying_results]
        qualifying_deltas = replace_none_with_average([list(result)[len(result) - 1] for result in qualifying_results])
    else:
        qualifying_results = qualifying_predict(race)
        drivers_to_predict = [list(result)[:len(result) - 1] for result in qualifying_results]
        qualifying_deltas = [list(result)[len(result) - 1] for result in qualifying_results]
        qualifying_grid = list(range(1, len(drivers_to_predict) + 1))
        logging.info("Qualifying results not available, so will make prediction")

    model = retrieve_race_model()

    features = {
        'race': np.array([race_name] * len(drivers_to_predict)),
        'qualifying': np.array(qualifying_deltas),
        'grid': np.array(qualifying_grid)
    }

    input_fn = tf.estimator.inputs.numpy_input_fn(
        x=features,
        num_epochs=1,
        shuffle=False
    )

    predictions = model.predict(input_fn=input_fn)
    ranking = results_to_ranking(predictions, len(drivers_to_predict))
    driver_ranking = [drivers_to_predict[position[1]] for position in ranking]

    return driver_ranking