import tensorflow as tf
import numpy as np
from .s3 import fetch_race_model
from .sql import race_features

def retrieve_model():
    race_feature = tf.feature_column.categorical_column_with_vocabulary_list(
        'race', sorted(race_features.get_race_list()))

    feature_columns = [
        tf.feature_column.numeric_column(key='qualifying'),
        tf.feature_column.numeric_column(key='grid'),
        tf.feature_column.indicator_column(race_feature)
    ]

    model = tf.estimator.DNNClassifier(
        model_dir=fetch_race_model(),
        hidden_units=[10],
        feature_columns=feature_columns,
        n_classes=21,
        label_vocabulary=['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', 'DNF'],
        optimizer=tf.train.ProximalAdagradOptimizer(
            learning_rate=0.1,
            l1_regularization_strength=0.001
        ))

    return model