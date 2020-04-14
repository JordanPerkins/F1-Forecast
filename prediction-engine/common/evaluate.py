""" Module containing function for evaluating the network accuracy """

from .db import Database
from .race import predict as race_predict
from .qualifying import predict as qualifying_predict
from .utils import tuples_to_dictionary
from scipy.stats import spearmanr

db = Database.get_database()

def evaluate(race=True):
    """ Computes the evaluation figures for the network """
    races = db.get_evaluation_races()
    winners_correct = 0
    podium_correct = 0
    podium_any_order_correct = 0
    num_races = 0
    total_coef = 0
    for race_id, in races:
        if race:
            actual_result = tuples_to_dictionary(db.get_race_results(race_id))
            predicted_result = race_predict(race_id)[0]
        else:
            actual_result = tuples_to_dictionary(db.get_qualifying_results(race_id))
            predicted_result = qualifying_predict(race_id)[0]

        actual_ranking = [
            actual_result[driver[0]][0][10] for driver in predicted_result
            if (driver[0] in actual_result
                and actual_result[driver[0]][0][10] is not None)
        ]
        system_ranking = list(range(1, len(actual_ranking) + 1))

        coef, _ = spearmanr(actual_ranking, system_ranking)

        total_coef += coef

        if actual_ranking[0] == system_ranking[0]:
            winners_correct += 1

        if actual_ranking[0:3] == system_ranking[0:3]:
            podium_correct += 1

        if sorted(actual_ranking[0:3]) == sorted(system_ranking[0:3]):
            podium_any_order_correct += 1

        num_races += 1

    percentage_winners_correct = round((winners_correct / num_races), 3)
    percentage_podium_correct = round((podium_correct / num_races), 3)
    percentage_podium_any_order_correct = round((podium_any_order_correct / num_races), 3)
    average_coef = round((total_coef / num_races), 3)

    return (percentage_winners_correct, percentage_podium_correct,
            percentage_podium_any_order_correct, average_coef)

print(evaluate())
