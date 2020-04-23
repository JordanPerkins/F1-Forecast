import logging
from .utils import evaluation_comparison

if __name__ == '__main__':
    logging.basicConfig()
    logging.root.setLevel(logging.INFO)
    logging.info('---- Race performance ----')
    evaluation_comparison(race=True)
    logging.info('---- Qualifying performance ----')
    evaluation_comparison(race=False)