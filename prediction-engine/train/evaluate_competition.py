import json
import os
import logging
from ..common.evaluate import evaluate

def evaluate_competition(race=True):
    script_dir = os.path.dirname(__file__)
    with open(os.path.join(script_dir, "./data/f1_predictor.json")) as json_file:
        data = json.load(json_file)

    races = data.keys()
    results = evaluate(race, races, data)

    results1 = evaluate(race, races)
    print(results1)
    print(results)

logging.basicConfig()
logging.root.setLevel(logging.NOTSET)
evaluate_competition(race=True)