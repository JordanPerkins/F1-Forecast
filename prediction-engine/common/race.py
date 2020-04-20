""" Module which is responsible for making race predictions. """

import time
import datetime
import hashlib
import logging
import tensorflow as tf
import math
import numpy as np
from .models import retrieve_race_model
from .s3 import upload_race_model
from .db import Database
from .utils import replace_none_with_average, tuples_to_dictionary
from .qualifying import predict as qualifying_predict

db = Database.get_database()

def get_result_as_tuples(predictions, number_of_drivers):
    """ Converts TensorFlow result into a list of tuples that can be sorted,
        also normalising probability by position. """
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
    """ Converts the tuples into a final ranking, by repeatedly
        picking highest class probability. """
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
    """ Generate a unique hash of the features. """
    strings = [
        race_name,
        (',').join([str(delta) for delta in qualifying_deltas]),
        (',').join([str(position) for position in qualifying_grid])
    ]
    hash_string = '|'.join(strings)
    hash_result = hashlib.sha256(hash_string.encode()).hexdigest()
    return hash_result, hash_string

def predict(race_id, disable_cache=False):
    """ Obtain a prediction for the given (or next) race. """
    race = race_id
    if race is None:
        race = db.get_next_race_year_round()[2]

    logging.info("Making prediction for race with ID %s", str(race))

    qualifying_results = db.get_qualifying_results_with_driver(race)
    if len(qualifying_results) > 0:
        logging.info("Qualifying results exist for race with ID %s", str(race))
        drivers_to_predict = [list(result)[:len(result) - 2] for result in qualifying_results]
        qualifying_grid = [int(list(result)[len(result) - 2]) for result in qualifying_results]
        qualifying_deltas = replace_none_with_average([list(result)[len(result) - 1] for result in qualifying_results])
        race_name, race_year = db.get_race_by_id(race)
    else:
        logging.info("Qualifying results not available for race with ID %s, so will make prediction", str(race))
        qualifying_results, race_name, race_year, _ = qualifying_predict(race)
        drivers_to_predict = [list(result)[:len(result) - 3] for result in qualifying_results]
        qualifying_deltas = [list(result)[len(result) - 1] for result in qualifying_results]
        qualifying_grid = list(range(1, len(drivers_to_predict) + 1))

    driver_ids = [result[0] for result in qualifying_results]

    race_averages = tuples_to_dictionary(db.get_race_averages(race))
    circuit_averages = tuples_to_dictionary(db.get_circuit_averages(race))
    standings = tuples_to_dictionary(db.get_championship_positions(race))
    position_changes = tuples_to_dictionary(db.get_position_changes(race))

    race_averages_array = replace_none_with_average([
        (race_averages[driver][0][0] if driver in race_averages else None)
        for driver in driver_ids
    ])

    circuit_averages_array = replace_none_with_average([
        (circuit_averages[driver][0][0] if driver in circuit_averages else None)
        for driver in driver_ids
    ])

    standings_array = replace_none_with_average([
        (standings[driver][0][0] if driver in standings else None)
        for driver in driver_ids
    ])

    wins_array = replace_none_with_average([
        (standings[driver][0][1] if driver in standings else None)
        for driver in driver_ids
    ])

    position_changes_array = replace_none_with_average([
        (position_changes[driver][0][0] if driver in position_changes else None)
        for driver in driver_ids
    ])

    features = {
        'race': np.array([race_name] * len(drivers_to_predict)),
        'qualifying': np.array(qualifying_deltas),
        'grid': np.array(qualifying_grid),
        'average_form': np.array(race_averages_array),
        'circuit_average_form': np.array(circuit_averages_array),
        'championship_standing': np.array(standings_array),
        'position_changes': np.array(position_changes_array),
        'wins': np.array(wins_array)
    }

    feature_hash, feature_string = generate_feature_hash(race_name, qualifying_deltas, qualifying_grid)

    cached_result = db.get_race_log(feature_hash)
    if len(cached_result) > 0 and not disable_cache:
        logging.warn("Result is cached in prediction log, so returning that")
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
    timestamp = datetime.datetime.utcfromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
    for index, driver in enumerate(driver_ranking):
        db.insert_race_log(driver[0], (index + 1), feature_hash, timestamp, feature_string)

    return driver_ranking, race_name, race_year, race

def train(num_epochs=200, batch_size=50, load_model=True):
    last_race_id = db.get_last_race_id()
    db.mark_races_as_in_progress(last_race_id)
    training_data = db.get_race_dataset()
    model = retrieve_race_model(load_model)

    races = [item[0] for item in training_data]
    grid = [item[1] for item in training_data]
    qualifying = replace_none_with_average([item[2] for item in training_data])
    results = [str(item[3]) for item in training_data]

    if len(races) > 0:

        average_form = replace_none_with_average([item[0] for item in db.get_race_dataset_form()])
        circuit_average_form = replace_none_with_average([item[0] for item in db.get_race_dataset_form_circuit()])
        standings = replace_none_with_average([item[0] for item in db.get_race_dataset_standings()])
        wins = replace_none_with_average([item[0] for item in db.get_race_dataset_position_changes()])
        position_changes = replace_none_with_average([item[0] for item in db.get_race_dataset_position_changes()])

        logging.info("Data received from SQL, now training")

        features = {
            'race': np.array(races),
            'qualifying': np.array(qualifying),
            'grid': np.array(grid),
            'average_form': np.array(average_form),
            'circuit_average_form': np.array(circuit_average_form),
            'championship_standing': np.array(standings),
            'wins': np.array(wins),
            'position_changes': np.array(position_changes)
        }

        train_input_fn = tf.estimator.inputs.numpy_input_fn(
            x=features,
            y=np.array(results),
            batch_size=batch_size,
            num_epochs=num_epochs,
            shuffle=True
        )

        model.train(input_fn=train_input_fn)

        db.mark_races_as_complete()

        logging.info("Training complete, now uploading model")
        upload_race_model()
        return True
    logging.info("Nothing to do, no races waiting for training")

