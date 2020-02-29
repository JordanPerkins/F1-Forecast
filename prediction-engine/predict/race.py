import json
import os
import boto3
import tensorflow as tf
import numpy as np
from ..common import race_model
from flask import abort, jsonify
import logging
import traceback
from ..common.db import Database
from ..common import utils

# import request

db = Database.get_database()

def predict(race_id):
    race = race_id
    if race is None:
        race = db.get_next_race_id()

    race_name = db.get_race_name(race)

    logging.info("Making prediction for race with ID "+str(race)+" and name "+str(race_name))

    drivers_to_predict = db.get_drivers_in_race(race - 1)

    qualifying_results = db.get_qualifying_results(race)
    if len(qualifying_results) != len(drivers_to_predict):
        logging.info("Qualifying results not available, so will make prediction")
    qualifying_deltas, qualifying_grid = utils.process_qualifying_results(qualifying_results)
    print(qualifying_grid)
    print(qualifying_deltas)

    model = race_model.retrieve_model()

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
    ranking = utils.results_to_ranking(predictions, len(drivers_to_predict))
    driver_ranking = [drivers_to_predict[position[1]] for position in ranking]

    return driver_ranking

def race_prediction(race_id=None):
    try:
        result = predict(race_id)
        return jsonify(result)
    except Exception as e:
        logging.error('An error occured retrieving race prediction: '+str(e))
        logging.debug(traceback.format_exc())
        abort(500, description="Internal Server Error")