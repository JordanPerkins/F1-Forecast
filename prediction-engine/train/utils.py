""" Utilities used for training. """

import json
import os
import logging
from ..common.evaluate import evaluate

def print_results(results):
    """ Print out provided results. """
    logging.info("%% Winners Correct: %f\n%% Podiums Correct: %f\n", results[0], results[1])
    logging.info("%% Podium Correct (Any Order): %f\n", results[2])
    logging.info("%% Positions Correct: %f\nAvg. Coef: %f", results[3], results[4])

def evaluate_competition(race):
    """ Read in evaluation results, and run evaluation function. """
    script_dir = os.path.dirname(__file__)
    with open(os.path.join(script_dir, "./data/f1_predictor.json")) as json_file:
        data = json.load(json_file)

    results = evaluate(race, None, data)

    return results

def evaluation_comparison(race=True):
    """ Evaluate network and then competition. """
    results = evaluate(race)
    logging.info("------- Network evaluation results -----")
    print_results(results)
    competition = evaluate_competition(race)
    logging.info("------- Competition evaluation results -----")
    print_results(competition)
