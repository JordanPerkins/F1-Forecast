import json
import os
import logging
from ..common.evaluate import evaluate
from ..common.race import train as train_race
from ..common.db import Database
from ..common.s3 import delete_race_model

db = Database.get_database()

def train():
    logging.info("Starting training")
    db.mark_all_races_as_untrained()
    delete_race_model()
    train_race(load_model=False)
    results = evaluate()
    logging.info("------- Network evaluation results -----")
    print_results(results)
    competition = evaluate_competition()
    logging.info("------- Competition evaluation results -----")
    print_results(competition)

def print_results(results):
    logging.info("%% Winners Correct: %f\n%% Podiums Correct: %f\n", results[0], results[1])
    logging.info("%% Podium Correct (Any Order): %f\n", results[2])
    logging.info("%% Positions Correct: %f\nAvg. Coef: %f", results[3], results[4])

def evaluate_competition():
    script_dir = os.path.dirname(__file__)
    with open(os.path.join(script_dir, "./data/f1_predictor.json")) as json_file:
        data = json.load(json_file)

    results = evaluate(True, None, data)

    return results

if __name__ == '__main__':
    logging.basicConfig()
    logging.root.setLevel(logging.INFO)
    train()