import json
from flask import abort, jsonify
import logging
import traceback
from ..common.race import predict
from ..common.utils import ranking_to_dictionary

def race_prediction(race_id=None):
    try:
        ranking, race_name, race_year, race_id = predict(race_id)
        return jsonify({
            'name': race_name,
            'year': race_year,
            'id': race_id,
            'result': ranking_to_dictionary(ranking)
        })
    except Exception as e:
        logging.error('An error occurred retrieving race prediction: '+str(e))
        logging.debug(traceback.format_exc())
        abort(500, description="Internal Server Error")