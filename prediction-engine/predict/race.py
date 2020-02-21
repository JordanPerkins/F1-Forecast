import json
import os
import boto3
import tensorflow as tf
import numpy as np
from ..common import race_model
from flask import abort, jsonify
import logging
import traceback

# import request

def predict():
    model = race_model.retrieve_model()

    test_features1 = {
        'race': np.array(['british', 'british', 'british', 'british', 'british', 'british', 'british', 'british', 'british', 'british']),
        'qualifying': np.array([0.000, 0.006, 0.079, 0.183, 0.497, 0.694, 1.089, 1.131, 1.242, 1.293]),
        'grid': np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    }

    test_input_fn = tf.estimator.inputs.numpy_input_fn(
        x=test_features1,
        num_epochs=1,
        shuffle=False
    )


    results = {}

    predictions = model.predict(input_fn=test_input_fn)
    for pred_dict in predictions:
        class_id = pred_dict['class_ids'][0]
        for position in range(0,11):
            if position not in results:
                results[position] = []
            results[position].append(pred_dict['probabilities'][position].item())

    print(type(results[0][0]))

    return results

def race_prediction():
    try:
        result = predict()
        return jsonify(result)
    except Exception as e:
        logging.error('An error occured retrieving race prediction: '+str(e))
        logging.debug(traceback.format_exc())
        abort(500, description="Internal Server Error")