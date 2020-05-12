# prediction-engine

The prediction engine provides the predictions as well as results information via a series of APIs, served with Python Flask.

The predictions are made using TensorFlow, with an S3 Bucket used for storage, and the majority of this code can be found in the common folder.

There is also a background process for updating the databases and models automatically, which is found in the update folder.

A local module for training and creating models can be found in train.

## Run Prediction APIs
    * First set environment variables: MYSQL_USER, MYSQL_DB, MYSQL_HOST, MYSQL_PASSWORD, S3_MODEL_BUCKET
    * Install requirements: pip install -r requirements.txt
    * From .., run python -m prediction-engine.predict.pywsgi

## Run tests
    * First set environment variables: MYSQL_USER, MYSQL_DB, MYSQL_HOST, MYSQL_PASSWORD, S3_MODEL_BUCKET
    * Install requirements: pip install -r requirements.txt
    * From .., run python -m unittest discover -v