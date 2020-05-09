""" Module which is responsible for making race predictions. """

import time
import datetime
import logging
import tensorflow as tf
import numpy as np
from .models import retrieve_race_model
from .s3 import upload_race_model
from .db import Database
from .utils import tuples_to_dictionary, generate_feature_hash
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
        if total > 0:
            result.extend([(position, index, (value / total)) for index, value in enumerate(values)])
        else:
            result.extend([(position, index, 0) for index, value in enumerate(values)])
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

def replace_none_with_average(data, rounding=3):
    """ Replaces none values in an array with the average of the other values. """
    data_none_removed = [float(item) for item in data if item is not None]
    average = 0
    if len(data_none_removed) != 0:
        average = round(sum(data_none_removed) / len(data_none_removed), rounding)
    return [float(item) if item is not None else average for item in data]

def predict(race_id, disable_cache=False, load_model=True):
    """ Obtain a prediction for the given (or next) race. """
    race = race_id
    if race is None:
        race = db.get_next_race_year_round()[2]

    logging.info("Making prediction for race with ID %s", str(race))

    qualifying_results = db.get_qualifying_results_with_driver(race)
    if len(qualifying_results) > 0:
        logging.info("Qualifying results exist for race with ID %s", str(race))
        drivers_to_predict = [list(result)[:len(result) - 3] for result in qualifying_results]
        qualifying_grid = [int(list(result)[len(result) - 2]) for result in qualifying_results]
        qualifying_deltas = replace_none_with_average([list(result)[len(result) - 1] for result in qualifying_results])
        constructors = [list(result)[len(result) - 3] for result in qualifying_results]
        race_name, race_year = db.get_race_by_id(race)
        qualifying_predicted = False
    else:
        logging.info("Qualifying results not available for race with ID %s, so will make prediction", str(race))
        qualifying_results, race_name, race_year, _ = qualifying_predict(race)
        drivers_to_predict = [list(result)[:len(result) - 3] for result in qualifying_results]
        qualifying_deltas = [list(result)[len(result) - 1] for result in qualifying_results]
        qualifying_grid = [i for i in range(1, len(drivers_to_predict) + 1)]
        constructors = [list(result)[len(result) - 3] for result in qualifying_results]
        qualifying_predicted = True

    cached_result = db.get_race_log(race, qualifying_predicted)
    if len(cached_result) > 0 and not disable_cache:
        logging.warn("Result is cached in prediction log, so returning that")
        return cached_result, race_name, race_year, race

    driver_ids = [result[0] for result in qualifying_results]
    drivers = [result[1] for result in qualifying_results]

    race_averages = tuples_to_dictionary(db.get_race_averages(race))
    circuit_averages = tuples_to_dictionary(db.get_circuit_averages(race))
    standings = tuples_to_dictionary(db.get_championship_positions(race))
    position_changes = tuples_to_dictionary(db.get_position_changes(race))
    race_averages_team = tuples_to_dictionary(db.get_race_averages_team(race))
    circuit_averages_team = tuples_to_dictionary(db.get_circuit_averages_team(race))
    position_changes_team = tuples_to_dictionary(db.get_position_changes_team(race))

    race_averages_array = [
        (float(race_averages[driver][0][0]) if driver in race_averages
         and race_averages[driver][0][0] is not None
         else qualifying_grid[index])
        for index, driver in enumerate(driver_ids)
    ]

    circuit_averages_array = ([
        (float(circuit_averages[driver][0][0]) if driver in circuit_averages
         and circuit_averages[driver][0][0] is not None
         else float(race_averages_array[index]))
        for index, driver in enumerate(driver_ids)
    ])

    championship_standing_array = ([
        (int(standings[driver][0][0]) if driver in standings
         and standings[driver][0][0] is not None else 20)
        for driver in driver_ids
    ])

    position_changes_array = [
        (float(position_changes[driver][0][0]) if driver in position_changes
         and position_changes[driver][0][0] is not None else 0)
        for driver in driver_ids
    ]

    race_averages_team_array = [
        (float(race_averages_team[driver][0][0]) if driver in race_averages_team
         and race_averages_team[driver][0][0] is not None
         else race_averages_array[index])
        for index, driver in enumerate(driver_ids)
    ]

    position_changes_team_array = [
        (float(position_changes_team[driver][0][0]) if driver in position_changes_team
         and position_changes_team[driver][0][0] is not None
         else position_changes_array[index])
        for index, driver in enumerate(driver_ids)
    ]

    circuit_averages_team_array = ([
        (float(circuit_averages_team[driver][0][0]) if driver in circuit_averages_team
         and circuit_averages_team[driver][0][0] is not None
         else float(race_averages_team_array[index]))
        for index, driver in enumerate(driver_ids)
    ])

    features = {
        'race': np.array([race_name] * len(drivers_to_predict)),
        'qualifying': np.array(qualifying_deltas),
        'grid': np.array(qualifying_grid),
        'average_form': np.array(race_averages_array),
        'average_form_team': np.array(race_averages_team_array),
        'circuit_average_form': np.array(circuit_averages_array),
        'circuit_average_form_team': np.array(circuit_averages_team_array),
        'championship_standing': np.array(championship_standing_array),
        'position_changes': np.array(position_changes_array),
        'position_changes_team': np.array(position_changes_team_array),
        'driver': np.array(drivers),
        'constructor': np.array(constructors)
    }

    feature_hash, feature_string = generate_feature_hash(features)

    model = retrieve_race_model(load_model)

    input_fn = tf.estimator.inputs.numpy_input_fn(
        x=features,
        num_epochs=1,
        shuffle=False
    )

    predictions = model.predict(input_fn=input_fn)
    ranking = results_to_ranking(predictions, len(drivers_to_predict))
    driver_ranking = [list(drivers_to_predict[position[1]]) for position in ranking]

    # Add to the log table
    if not disable_cache:
        timestamp = datetime.datetime.utcfromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
        for index, driver in enumerate(driver_ranking):
            db.insert_race_log(
                race, driver[0], (index + 1), feature_hash,
                timestamp, feature_string, qualifying_predicted
            )

    return driver_ranking, race_name, race_year, race

def train(num_epochs=200, batch_size=30, load_model=True):
    """ Train race model. """
    last_race_id = db.get_last_race_id()
    db.mark_races_as_in_progress(last_race_id)
    training_data = db.get_race_dataset()
    model = retrieve_race_model(load_model)

    races = [item[0] for item in training_data]
    grid = [int(item[1]) for item in training_data]
    qualifying = [float(item[2]) for item in training_data]
    results = [str(item[3]) for item in training_data]
    driver = [item[4] for item in training_data]
    constructor = [item[5] for item in training_data]

    if len(races) > 0:

        average_form = [
            (float(item[0]) if item[0] is not None else grid[index])
            for index, item in enumerate(db.get_race_dataset_form())
        ]
        circuit_average_form = [
            (float(item[0]) if item[0] is not None else average_form[index])
            for index, item in enumerate(db.get_race_dataset_form_circuit())
        ]
        standings = [int(item[0]) if item[0] is not None else 20 for item in db.get_race_dataset_standings()]
        position_changes = [
            (float(item[0]) if item[0] is not None else (grid[index] - int(results[index])))
            for index, item in enumerate(db.get_race_dataset_position_changes())
        ]
        average_form_team = [
            (float(item[0]) if item[0] is not None else average_form[index])
            for index, item in enumerate(db.get_race_dataset_form_team())
        ]
        circuit_average_form_team = [
            (float(item[0]) if item[0] is not None else average_form_team[index])
            for index, item in enumerate(db.get_race_dataset_form_team_circuit())
        ]
        position_changes_team = [
            (float(item[0]) if item[0] is not None else position_changes[index])
            for index, item in enumerate(db.get_race_dataset_position_changes_team())
        ]

        logging.info("Data received from SQL, now training")

        features = {
            'race': np.array(races),
            'qualifying': np.array(qualifying),
            'grid': np.array(grid),
            'average_form': np.array(average_form),
            'circuit_average_form': np.array(circuit_average_form),
            'circuit_average_form_team': np.array(circuit_average_form_team),
            'championship_standing': np.array(standings),
            'position_changes': np.array(position_changes),
            'position_changes_team': np.array(position_changes_team),
            'driver': np.array(driver),
            'constructor':  np.array(constructor),
            'average_form_team': np.array(average_form_team)
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
