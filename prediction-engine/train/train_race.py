""" Module for running complete race training. """

import logging
from ..common.race import train
from ..common.db import Database
from ..common.s3 import delete_race_model
from .utils import evaluation_comparison

db = Database.get_database()

if __name__ == '__main__':
    logging.basicConfig()
    logging.root.setLevel(logging.INFO)
    logging.info("Starting training")
    db.mark_all_races_as_untrained()
    delete_race_model()
    train(load_model=False)
    evaluation_comparison()
