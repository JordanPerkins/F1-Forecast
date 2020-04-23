""" Module which is responsible for making qualifying predictions. """

import time
from datetime import datetime
import hashlib
import logging
import tensorflow as tf
import numpy as np
from .models import retrieve_qualifying_model
from .s3 import upload_qualifying_model
from .db import Database
from .utils import tuples_to_dictionary, replace_none_with_average

db = Database.get_database()

def results_to_ranking(predictions):
    """ Orders the result from TensorFlow to produce a ranking. """
    predictions_list = list(predictions)
    predictions_list_tuples = [
        (index, value['predictions'][0].item())
        for index, value in enumerate(predictions_list)
    ]
    sorted_predictions = sorted(predictions_list_tuples, key=lambda item: item[1])
    return sorted_predictions

def generate_feature_hash(race_name, average_form):
    """ Generate a unique hash of the features. """
    strings = [
        race_name,
        (',').join([str(average) for average in average_form])
    ]
    hash_string = '|'.join(strings)
    hash_result = hashlib.sha256(hash_string.encode()).hexdigest()
    return hash_result, hash_string

def predict(race_id, disable_cache=False, load_model=True):
    """ Obtain a prediction for the given (or next) race in qualifying. """
    race = race_id
    if race is None:
        race = db.get_next_race_year_round_qualifying()[2]

    race_name, race_year = db.get_race_by_id(race)

    logging.info('Making prediction for race with ID %s and name %s', str(race), race_name)

    averages_with_driver = db.get_qualifying_form_with_drivers(race)
    drivers_to_predict = [list(result)[:len(result) - 1] for result in averages_with_driver]
    average_form = [float(list(result)[len(result) - 1]) for result in averages_with_driver]

    features = {
        'race': np.array([race_name]*len(drivers_to_predict)),
        'average_form': np.array(average_form)
    }

    fe_hash, fe_string = generate_feature_hash(
        race_name,
        average_form
    )

    cached_result = db.get_qualifying_log(fe_hash)
    if len(cached_result) > 0 and not disable_cache:
        logging.info("Result is cached in prediction log, so returning that")
        return cached_result, race_name, race_year, race

    model = retrieve_qualifying_model(load_model)

    input_fn = tf.estimator.inputs.numpy_input_fn(
        x=features,
        num_epochs=1,
        shuffle=False
    )

    predictions = model.predict(input_fn=input_fn)
    ranking = results_to_ranking(predictions)
    fastest_lap = min([item[1] for item in ranking])
    driver_ranking = [
        (list(drivers_to_predict[position[0]]) +
         [round(position[1]-fastest_lap, 3)])
        for position in ranking
    ]

    # Add to the log table
    timestamp = datetime.utcfromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
    for index, driver in enumerate(driver_ranking):
        db.insert_qualifying_log(driver[0], (index + 1), fe_hash, timestamp, driver[-1], fe_string)
    return driver_ranking, race_name, race_year, race

def train(num_epochs=200, batch_size=30, load_model=True):
    last_race_id = db.get_last_race_id()
    db.mark_qualifiyng_as_in_progress(last_race_id)
    training_data = db.get_qualifying_dataset()
    model = retrieve_qualifying_model(load_model)

    races = [item[0] for item in training_data]
    results = [float(item[1]) for item in training_data]

    if len(races) > 0:

        average_form = [float(item[0]) for item in db.get_qualifying_dataset_form()]

        logging.info("Data received from SQL, now training qualifying")

        features = {
            'race': np.array(races),
            'average_form': np.array(average_form)
        }

        train_input_fn = tf.estimator.inputs.numpy_input_fn(
            x=features,
            y=np.array(results),
            batch_size=batch_size,
            num_epochs=num_epochs,
            shuffle=True
        )

        model.train(input_fn=train_input_fn)

        db.mark_qualifying_as_complete()

        logging.info("Training complete, now uploading model")
        upload_qualifying_model()
        return True
    logging.info("Nothing to do, no races waiting for qualifying training")
