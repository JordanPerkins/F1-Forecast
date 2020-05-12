""" The controllers for the prediction routes. """
import logging
import traceback
from flask import abort, jsonify
from ..common.qualifying import predict as qualifying_predict
from ..common.race import predict as race_predict
from ..common.utils import ranking_to_dictionary

def qualifying_prediction(race_id=None):
    """ The /predict/qualifying controller. """
    try:
        ranking, race_name, race_year, race_id = qualifying_predict(race_id)
        return jsonify({
            'name': race_name,
            'year': race_year,
            'id': race_id,
            'result': ranking_to_dictionary(ranking)
        })
    except Exception as err:
        logging.error('An error occurred retrieving qualifying prediction: %s', str(err))
        logging.debug(traceback.format_exc())
        abort(500, description="Internal Server Error")

def race_prediction(race_id=None):
    """ The /predict/race controller. """
    try:
        ranking, race_name, race_year, race_id = race_predict(race_id)
        return jsonify({
            'name': race_name,
            'year': race_year,
            'id': race_id,
            'result': ranking_to_dictionary(ranking)
        })
    except Exception as err:
        logging.error('An error occurred retrieving race prediction: %s', str(err))
        logging.debug(traceback.format_exc())
        abort(500, description="Internal Server Error")
