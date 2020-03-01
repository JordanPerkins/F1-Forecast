import json
import tensorflow as tf
import numpy as np
from .models import retrieve_race_model
import logging
import traceback
from .db import Database
from .utils import process_qualifying_results, results_to_ranking

db = Database.get_database()

def predict(race_id):
    race = race_id
    if race is None:
        race = db.get_next_race_id()

    race_name = db.get_race_name(race)

    logging.info("Making prediction for race with ID "+str(race)+" and name "+str(race_name))

    qualifying_results = db.get_qualifying_results_with_driver(race)
    if len(qualifying_results) > 0:
        drivers_to_predict = [list(result)[:len(result) - 1] for result in qualifying_results]
        qualifying_results_list = [list(result)[len(result) - 1] for result in qualifying_results]
    else:
        drivers_to_predict = db.get_drivers_in_race(race - 1)
        
        logging.info("Qualifying results not available, so will make prediction")

    qualifying_deltas, qualifying_grid = process_qualifying_results(qualifying_results_list)

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