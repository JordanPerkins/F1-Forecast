""" Module containing function for evaluating the network accuracy """

from .db import Database
from .race import predict as race_predict
from .qualifying import predict as qualifying_predict
from .utils import tuples_to_dictionary
from scipy.stats import spearmanr

db = Database.get_database()

def evaluate(race=True, races=None, override_predictions=None):
    """ Computes the evaluation figures for the network """
    winners_correct = 0
    podium_correct = 0
    podium_any_order_correct = 0
    num_races = 0
    total_correct_positions = 0
    total_positions = 0
    all_coef = []

    if races:
        evaluation_races = races
    else:
        evaluation_races = [
            evaluation_race[0]
            for evaluation_race in db.get_evaluation_races()
        ]

    for race_id in evaluation_races:
        if race:
            actual_result = tuples_to_dictionary(db.get_race_results(race_id))
            position_index = 10
        else:
            actual_result = tuples_to_dictionary(db.get_qualifying_results(race_id))
            position_index = 9

        if override_predictions:
            if race:
                predictions = override_predictions[str(race_id)]['race']
            else:
                predictions = override_predictions[str(race_id)]['qualifying']

            actual_ranking = [
                actual_result[driver][0][position_index]
                for driver in predictions
                if (driver in actual_result
                    and actual_result[driver][0][position_index] is not None)
            ]
        else:
            if race:
                predicted_result = race_predict(race_id)[0]
            else:
                predicted_result = qualifying_predict(race_id)[0]

            actual_ranking = [
                actual_result[driver[0]][0][position_index] for driver in predicted_result
                if (driver[0] in actual_result
                    and actual_result[driver[0]][0][position_index] is not None)
            ]
        system_ranking = list(range(1, len(actual_ranking) + 1))

        coef, _ = spearmanr(actual_ranking, system_ranking)

        all_coef.append(coef)

        if actual_ranking[0] == system_ranking[0]:
            winners_correct += 1

        if actual_ranking[0:3] == system_ranking[0:3]:
            podium_correct += 1

        if sorted(actual_ranking[0:3]) == sorted(system_ranking[0:3]):
            podium_any_order_correct += 1

        for position in system_ranking:
            if actual_ranking[position - 1] == position:
                total_correct_positions += 1
        
        total_positions += len(system_ranking)
        num_races += 1

    percentage_winners_correct = round((winners_correct / num_races), 3) * 100
    percentage_podium_correct = round((podium_correct / num_races), 3) * 100
    percentage_podium_any_order_correct = round((podium_any_order_correct / num_races), 3) * 100
    percentage_correct_positions = round((total_correct_positions / total_positions), 3) * 100
    average_coef = round((sum(all_coef) / num_races), 3)

    return (percentage_winners_correct, percentage_podium_correct,
            percentage_podium_any_order_correct,
            percentage_correct_positions, average_coef, all_coef)

