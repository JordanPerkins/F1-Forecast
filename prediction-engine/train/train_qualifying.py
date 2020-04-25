""" Module for running complete qualifying training. """

import logging
from ..common.qualifying import train
from ..common.db import Database
from ..common.s3 import delete_qualifying_model
from .utils import evaluation_comparison

db = Database.get_database()

if __name__ == '__main__':
    logging.basicConfig()
    logging.root.setLevel(logging.INFO)
    logging.info("Starting qualifying training")
    db.mark_all_qualifying_as_untrained()
    delete_qualifying_model()
    train(load_model=False)
    evaluation_comparison(race=False)
