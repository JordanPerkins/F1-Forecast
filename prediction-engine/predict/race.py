import json
from flask import abort, jsonify
import logging
import traceback
from ..common.race import predict

def race_prediction(race_id=None):
    try:
        result = predict(race_id)
        return jsonify(result)
    except Exception as e:
        logging.error('An error occured retrieving race prediction: '+str(e))
        logging.debug(traceback.format_exc())
        abort(500, description="Internal Server Error")