import json
import tarfile
import os
import boto3
import tensorflow as tf

s3 = boto3.client('s3')

race_list = ['abu dhabi', 'argentine', 'australian', 'austrian', 'azerbaijan', 'bahrain', 'belgian', 'brazilian', 'british', 'caesars palace', 'canadian', 'chinese', 'dallas', 'detroit', 'dutch', 'european', 'french', 'german', 'hungarian', 'indian', 'indianapolis 500', 'italian', 'japanese', 'korean', 'luxembourg', 'malaysian', 'mexican', 'mexico city', 'monaco', 'moroccan', 'pacific', 'pescara', 'portuguese', 'russian', 'san marino', 'singapore', 'south african', 'spanish', 'swedish', 'swiss', 'turkish', 'united states', 'united states  west', 'vietnamese']

# import requests

FILE_DIR = '/tmp/'
BUCKET = 'f1forecastmodels'

def fetch_model():
    s3.download_file(BUCKET, 'model.tar.gz', FILE_DIR+'model.tar.gz')
    tarfile.open(FILE_DIR+'model.tar.gz', 'r').extractall(FILE_DIR)

def predict():
    race_feature = tf.feature_column.categorical_column_with_vocabulary_list(
      'race', race_list)

    feature_columns = [
        tf.feature_column.numeric_column(key='qualifying'),
        tf.feature_column.numeric_column(key='grid'),
        tf.feature_column.indicator_column(race_feature)
    ]

    model = tf.estimator.DNNClassifier(
        model_dir='/tmp/model/',
        hidden_units=[10],
        feature_columns=feature_columns,
        n_classes=21,
        label_vocabulary=['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', 'DNF'],
        optimizer=tf.train.ProximalAdagradOptimizer(
            learning_rate=0.1,
            l1_regularization_strength=0.001
        ))

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
            results[position].append(pred_dict['probabilities'][position])

    return results

def lambda_handler(event, context):
    """Sample pure Lambda function

    Parameters
    ----------
    event: dict, required
        API Gateway Lambda Proxy Input Format

        Event doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html#api-gateway-simple-proxy-for-lambda-input-format

    context: object, required
        Lambda Context runtime methods and attributes

        Context doc: https://docs.aws.amazon.com/lambda/latest/dg/python-context-object.html

    Returns
    ------
    API Gateway Lambda Proxy Output Format: dict

        Return doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html
    """

    # try:
    #     ip = requests.get("http://checkip.amazonaws.com/")
    # except requests.RequestException as e:
    #     # Send some context about this error to Lambda Logs
    #     print(e)

    #     raise e

    fetch_model()
    results = predict()

    return {
        "statusCode": 200,
        "body": json.dumps(results),
    }
