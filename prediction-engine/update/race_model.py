import json
import tensorflow as tf
import numpy as np
from ..common.models import retrieve_race_model
import logging
import traceback
from ..common.db import Database
from ..common.utils import replace_none_with_average
from ..common.race import predict as race_predict

db = Database.get_database()

def update_race_model():
    db.mark_races_as_in_progress()
    training_data = db.get_race_dataset()
    model = retrieve_race_model()

    races = [item[0] for item in training_data]
    grid = [item[1] for item in training_data]
    qualifying = replace_none_with_average([item[2] for item in training_data])
    results = [str(item[3]) for item in training_data]

    features = {
        'race': np.array(races),
        'qualifying': np.array(qualifying),
        'grid': np.array(grid)
    }

    train_input_fn = tf.estimator.inputs.numpy_input_fn(
        x=features,
        y=np.array(results),
        batch_size=500,
        num_epochs=None,
        shuffle=False
    )

    model.train(input_fn=train_input_fn, steps=100)

    db.mark_races_as_complete()
