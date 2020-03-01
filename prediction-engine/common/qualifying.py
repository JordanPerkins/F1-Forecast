import json
import tensorflow as tf
import numpy as np
from .models import retrieve_qualifying_model
import logging
import traceback
from .db import Database
from datetime import date

db = Database.get_database()

def predict(race_id):
    race = race_id
    if race is None:
        race = db.get_next_qualifying_race_id()

    race_name = db.get_race_name(race)

    logging.info("Making prediction for race with ID "+str(race)+" and name "+str(race_name))

    previous_race_at_track = db.get_previous_year_race_by_id(race)
    drivers_to_predict = db.get_drivers_in_qualifying(race - 1)
    drivers_to_predict_ids = [list(result)[0] for result in drivers_to_predict]
    if previous_race_at_track:
        logging.info("Race at this track exists previously, so using this to make prediction")
        drivers_in_race = db.get_drivers_in_qualifying(previous_race_at_track)
        drivers_in_race_ids = [list(result)[0] for result in drivers_in_race]
        drivers_not_in_race = list(set(drivers_to_predict_ids)-set(drivers_in_race_ids))
        driver_replacements = db.get_qualifying_driver_replacements(drivers_to_predict_ids, previous_race_at_track, drivers_not_in_race, race - 1)
        print(driver_replacements)
    else:
        logging.info("Race not found, so will use season average")

    test_features1 = {
        'race': np.array(['british', 'british', 'british','british', 'british', 'british','british', 'british']),
        'lap': np.array([0.325, 0.000,1.987,0.710,2.461,0.044, 1.207, 2.009]),
        'change': np.array([-0.339, -0.12, -1.076, 0.078, -0.988, 0.734, 1.569, 1.364]),
        'fastest_lap': np.array([85.892,85.892,85.892,85.892,85.892,85.892,85.892,85.892]),
        'season_change': np.array([-1.817, -1.817, -1.817, -1.817, -1.817, -1.817, -1.817, -1.817])
    }

    model = retrieve_qualifying_model()

    test_input_fn1 = tf.estimator.inputs.numpy_input_fn(
        x=test_features1,
        num_epochs=1,
        shuffle=False
    )

    predictions = model.predict(input_fn=test_input_fn1)

    return []