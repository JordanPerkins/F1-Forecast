import json
import tensorflow as tf
import numpy as np
from .models import retrieve_race_model
import logging
import traceback
from .db import Database
from .utils import replace_none_with_average
from .qualifying import predict as qualifying_predict
import time
import datetime
import hashlib

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

def generate_feature_hash(race_name, qualifying_deltas, qualifying_grid):
    strings = [
        race_name,
        (',').join([str(delta) for delta in qualifying_deltas]),
        (',').join([str(position) for position in qualifying_grid])
    ]
    hash_string = '|'.join(strings)
    hash_result = hashlib.sha256(hash_string.encode()).hexdigest()
    return hash_result, hash_string

def predict(race_id):
    race = race_id
    if race is None:
        race = db.get_next_race_year_round()[2]

    logging.info("Making prediction for race with ID "+str(race))

    qualifying_results = db.get_qualifying_results_with_driver(race)
    if len(qualifying_results) > 0:
        logging.info("Qualifying results exist for race with ID "+str(race))
        drivers_to_predict = [list(result)[:len(result) - 2] for result in qualifying_results]
        qualifying_grid = [int(list(result)[len(result) - 2]) for result in qualifying_results]
        qualifying_deltas = replace_none_with_average([list(result)[len(result) - 1] for result in qualifying_results])
        race_name, race_year = db.get_race_by_id(race)
    else:
        logging.info("Qualifying results not available for race with ID "+str(race)+", so will make prediction")
        qualifying_results, race_name, race_year, _ = qualifying_predict(race)
        drivers_to_predict = [list(result)[:len(result) - 3] for result in qualifying_results]
        qualifying_deltas = [list(result)[len(result) - 1] for result in qualifying_results]
        qualifying_grid = list(range(1, len(drivers_to_predict) + 1))

    features = {
        'race': np.array([race_name] * len(drivers_to_predict)),
        'qualifying': np.array(qualifying_deltas),
        'grid': np.array(qualifying_grid)
    }

    feature_hash, feature_string = generate_feature_hash(race_name, qualifying_deltas, qualifying_grid)

    cached_result = db.get_race_log(feature_hash)
    if cached_result:
        logging.info("Result is cached in prediction log, so returning that");
        return cached_result, race_name, race_year, race

    model = retrieve_race_model()

    input_fn = tf.estimator.inputs.numpy_input_fn(
        x=features,
        num_epochs=1,
        shuffle=False
    )

    predictions = model.predict(input_fn=input_fn)
    ranking = results_to_ranking(predictions, len(drivers_to_predict))
    driver_ranking = [list(drivers_to_predict[position[1]]) for position in ranking]

    # Add to the log table
    ts = time.time()
    timestamp = datetime.datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
    for index, driver in enumerate(driver_ranking):
        db.insert_race_log(driver[0], (index + 1), feature_hash, timestamp, feature_string) 

    return driver_ranking, race_name, race_year, race