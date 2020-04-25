""" Contains functions for reconstructing the models. """

import tensorflow as tf
from .s3 import fetch_race_model, fetch_qualifying_model
from .db import Database

def retrieve_race_model(load_model=True):
    """ Returns the Tensorflow race model. """
    race_feature = tf.feature_column.categorical_column_with_hash_bucket(
        'race',
        hash_bucket_size=60
    )

    driver_feature = tf.feature_column.categorical_column_with_hash_bucket(
        'driver',
        hash_bucket_size=1000
    )

    constructor_feature = tf.feature_column.categorical_column_with_hash_bucket(
        'constructor',
        hash_bucket_size=300
    )

    feature_columns = [
        tf.feature_column.numeric_column(key='qualifying'),
        tf.feature_column.numeric_column(key='average_form'),
        tf.feature_column.numeric_column(key='average_form_team'),
        tf.feature_column.numeric_column(key='circuit_average_form'),
        tf.feature_column.numeric_column(key='circuit_average_form_team'),
        tf.feature_column.numeric_column(key='position_changes'),
        tf.feature_column.numeric_column(key='grid'),
        tf.feature_column.numeric_column(key='championship_standing'),
        tf.feature_column.indicator_column(race_feature),
        tf.feature_column.indicator_column(driver_feature),
        tf.feature_column.indicator_column(constructor_feature)
    ]

    model = tf.estimator.DNNClassifier(
        model_dir=fetch_race_model(load_model),
        hidden_units=[30, 30],
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
    race_feature = tf.feature_column.categorical_column_with_hash_bucket(
        'race',
        hash_bucket_size=60
    )

    driver_feature = tf.feature_column.categorical_column_with_hash_bucket(
        'driver',
        hash_bucket_size=1000
    )

    constructor_feature = tf.feature_column.categorical_column_with_hash_bucket(
        'constructor',
        hash_bucket_size=300
    )

    feature_columns = [
        tf.feature_column.numeric_column(key='average_form'),
        tf.feature_column.numeric_column(key='average_form_team'),
        tf.feature_column.numeric_column(key='circuit_average_form'),
        tf.feature_column.numeric_column(key='circuit_average_form_team'),
        tf.feature_column.numeric_column(key='championship_standing'),
        tf.feature_column.indicator_column(race_feature),
        tf.feature_column.indicator_column(driver_feature),
        tf.feature_column.indicator_column(constructor_feature)
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
