import json
import tensorflow as tf
import numpy as np
from .models import retrieve_qualifying_model
import logging
import traceback
from .db import Database
from .utils import tuples_to_dictionary, process_qualifying_results

db = Database.get_database()

def driver_replacements_to_laps(drivers_to_predict_ids, drivers_in_race, previous_race_at_track, race):
    drivers_in_race_ids = [list(result)[0] for result in drivers_in_race]
    drivers_not_in_race = list(set(drivers_to_predict_ids)-set(drivers_in_race_ids))
    replacement_dict = {}
    if len(drivers_not_in_race):
        replacement_dict = tuples_to_dictionary(db.get_qualifying_driver_replacements(drivers_to_predict_ids, previous_race_at_track, drivers_not_in_race, race - 1))
    new_driver_ids = [driver_id if driver_id not in drivers_not_in_race else (replacement_dict[driver_id][0][0] if driver_id in replacement_dict else None) for driver_id in drivers_to_predict_ids]
    drivers_in_race_dict = tuples_to_dictionary(drivers_in_race)
    return [(None if driver_id is None else drivers_in_race_dict[driver_id][0][-1]) for driver_id in new_driver_ids], replacement_dict


def calculate_season_changes(race, replacement_dict, drivers_to_predict_ids):
    laps_dict = tuples_to_dictionary(db.get_all_laps_prior_to_race(race))
    other_laps_dict = tuples_to_dictionary(db.get_laps_in_prior_season_to_race(race))
    result = []
    for driver in drivers_to_predict_ids:
        results = []
        if driver in laps_dict:
            laps = laps_dict[driver]
            other_driver_id = driver if driver not in replacement_dict else replacement_dict[driver][0][0]
            for lap in laps:
                race_id = lap[0]
                lap_time = lap[1]
                other_lap_key = str(other_driver_id)+str(race_id)
                if lap_time is not None and race_id is not race and other_lap_key in other_laps_dict:
                    other_lap = other_laps_dict[other_lap_key][0][0]
                    if other_lap is not None:
                        lap_time_in_seconds = (float(lap_time.split(':')[0])*60 + float(lap_time.split(':')[1]))
                        other_lap_time_in_seconds = (float(other_lap.split(':')[0])*60 + float(other_lap.split(':')[1]))
                        diff = lap_time_in_seconds - other_lap_time_in_seconds
                        if driver not in replacement_dict:
                            results.append(diff)
                        else:
                            results.append(0.000)
        if len(results):
            result.append(round(sum(results) / len(results), 3))
        else:
            result.append(0.000)
    return result


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
    drivers_to_predict_ids = [list(result)[0] for result in drivers_to_predict]
    if previous_race_at_track:
        logging.info("Race at this track exists previously, so using this to make prediction")
        drivers_in_race = db.get_qualifying_results_with_driver(previous_race_at_track)
        laps, replacement_dict = driver_replacements_to_laps(drivers_to_predict_ids, drivers_in_race, previous_race_at_track, race)
        deltas, ranking, fastest_lap = process_qualifying_results(laps)
        differences = calculate_season_changes(race, replacement_dict, drivers_to_predict_ids)
        season_change = round(sum(differences) / len(differences), 3)
    else:
        logging.info("Race not found, so will use season average")

    features = {
        'race': np.array([race_name]*len(drivers_to_predict)),
        'lap': np.array(deltas),
        'change': np.array(differences),
        'fastest_lap': np.array([fastest_lap]*len(drivers_to_predict)),
        'season_change': np.array([season_change]*len(drivers_to_predict))
    }

    print(deltas)
    print(drivers_to_predict)
    print(differences)

    model = retrieve_qualifying_model()

    input_fn = tf.estimator.inputs.numpy_input_fn(
        x=features,
        num_epochs=1,
        shuffle=False
    )

    predictions = model.predict(input_fn=input_fn)
    ranking = results_to_ranking(predictions)
    fastest_lap = min([item[1] for item in ranking])
    driver_ranking = [drivers_to_predict[position[0]] + (round(position[1]-fastest_lap, 3),) for position in ranking]

    return driver_ranking


