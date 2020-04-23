""" Contains functions for reconstructing the models. """

import tensorflow as tf
from .s3 import fetch_race_model, fetch_qualifying_model
from .db import Database

def retrieve_race_model(load_model=True):
    """ Returns the Tensorflow race model. """
    race_feature = tf.feature_column.categorical_column_with_vocabulary_list(
        'race',
        sorted(Database.get_database().get_race_list())
    )

    grid_feature = tf.feature_column.categorical_column_with_vocabulary_list(
        'grid',
        [str(i) for i in range(1, 21)]
    )

    standing_feature = tf.feature_column.categorical_column_with_vocabulary_list(
        'championship_standing',
        [str(i) for i in range(1, 21)]
    )

    feature_columns = [
        tf.feature_column.numeric_column(key='qualifying'),
        tf.feature_column.numeric_column(key='average_form'),
        tf.feature_column.numeric_column(key='circuit_average_form'),
        tf.feature_column.numeric_column(key='position_changes'),
        tf.feature_column.indicator_column(race_feature),
        tf.feature_column.indicator_column(grid_feature),
        tf.feature_column.indicator_column(standing_feature)
    ]

    model = tf.estimator.DNNClassifier(
        model_dir=fetch_race_model(load_model),
        hidden_units=[50, 50],
        feature_columns=feature_columns,
        n_classes=20,
        label_vocabulary=[str(i) for i in range(1, 21)],
        optimizer=tf.train.ProximalAdagradOptimizer(
            learning_rate=0.1,
            l1_regularization_strength=0.001
        ))

    return model

def retrieve_qualifying_model(load_model=True):
    """ Returns the Tensorflow qualifying model. """
    race_feature = tf.feature_column.categorical_column_with_vocabulary_list(
        'race',
        sorted(Database.get_database().get_race_list())
    )

    feature_columns = [
        tf.feature_column.numeric_column(key='average_form'),
        tf.feature_column.numeric_column(key='circuit_average_form'),
        tf.feature_column.numeric_column(key='championship_standing'),
        tf.feature_column.indicator_column(race_feature)
    ]

    model = tf.estimator.DNNRegressor(
        model_dir=fetch_qualifying_model(load_model),
        hidden_units=[20, 20],
        feature_columns=feature_columns,
        optimizer=tf.train.ProximalAdagradOptimizer(
            learning_rate=0.1,
            l1_regularization_strength=0.001
        ))

    return model
