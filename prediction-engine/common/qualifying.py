import json
import tensorflow as tf
import numpy as np
from .models import retrieve_qualifying_model
import logging
import traceback
from .db import Database
from .utils import tuples_to_dictionary, process_qualifying_results

db = Database.get_database()

def driver_replacements_to_laps(drivers_to_predict, drivers_in_race, previous_race_at_track, race):
    drivers_to_predict_ids = [list(result)[0] for result in drivers_to_predict]
    drivers_in_race_ids = [list(result)[0] for result in drivers_in_race]
    drivers_not_in_race = list(set(drivers_to_predict_ids)-set(drivers_in_race_ids))
    replacement_dict = tuples_to_dictionary(db.get_qualifying_driver_replacements(drivers_to_predict_ids, previous_race_at_track, drivers_not_in_race, race - 1))
    new_driver_ids = [driver_id if driver_id not in drivers_not_in_race else (replacement_dict[driver_id][0] if driver_id in replacement_dict else None) for driver_id in drivers_to_predict_ids]
    print(new_driver_ids)
    drivers_in_race_dict = tuples_to_dictionary(drivers_in_race)
    return [drivers_in_race_dict[driver_id][-1] for driver_id in new_driver_ids]


def results_to_ranking(predictions):
    predictions_list = list(predictions)
    predictions_list_tuples = [(index, value['predictions'][0].item()) for index, value in enumerate(predictions_list)]
    sorted_predictions = sorted(predictions_list_tuples, key=lambda item: item[1])
    return sorted_predictions


def predict(race_id):
    race = race_id
    if race is None:
        race = db.get_next_qualifying_race_id()

    race_name = db.get_race_name(race)

    logging.info("Making prediction for race with ID "+str(race)+" and name "+str(race_name))

    previous_race_at_track = db.get_previous_year_race_by_id(race)
    drivers_to_predict = db.get_qualifying_results_with_driver(race - 1)
    if previous_race_at_track:
        logging.info("Race at this track exists previously, so using this to make prediction")
        drivers_in_race = db.get_qualifying_results_with_driver(previous_race_at_track)
        laps = driver_replacements_to_laps(drivers_to_predict, drivers_in_race, previous_race_at_track, race)
        deltas, ranking, fastest_lap = process_qualifying_results(laps)
        print(deltas)
        print(fastest_lap)
    else:
        logging.info("Race not found, so will use season average")

    features = {
        'race': np.array([race_name]*len(drivers_to_predict)),
        'lap': np.array(deltas),
        'change': np.array([-0.339, -0.12, -1.076, 0.078, -0.988, 0.734, 1.569, 1.364, 1.569, 1.364, -0.339, -0.12, -1.076, 0.078, -0.988, 0.734, 1.569, 1.364, 1.569, 1.364]),
        'fastest_lap': np.array([fastest_lap]*len(drivers_to_predict)),
        'season_change': np.array([-1.817, -1.817, -1.817, -1.817, -1.817, -1.817, -1.817, -1.817, -1.817, -1.817, -1.817, -1.817, -1.817, -1.817, -1.817, -1.817, -1.817, -1.817, -1.817, -1.817])
    }

    model = retrieve_qualifying_model()

    input_fn = tf.estimator.inputs.numpy_input_fn(
        x=features,
        num_epochs=1,
        shuffle=False
    )

    predictions = model.predict(input_fn=input_fn)
    ranking = results_to_ranking(predictions)
    driver_ranking = [drivers_to_predict[position[0]] + (position[1],) for position in ranking]

    return driver_ranking



