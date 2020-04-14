""" Handles fetching and uploading of the model to the S3 bucket. """

import logging
import tarfile
import os
import boto3

QUALIFYING_MODEL = 'qualifying_model'
RACE_MODEL = 'race_model'
FILE_DIR = '/tmp/'
BUCKET = os.getenv('S3_MODEL_BUCKET')

s3 = boto3.client('s3')

def fetch_model(model):
    """ Attempts to fetch the file with the given name. """
    try:
        s3.download_file(BUCKET, model+'.tar.gz', FILE_DIR+model+'.tar.gz')
        tarfile.open(FILE_DIR+model+'.tar.gz', 'r').extractall(FILE_DIR)
        logging.info('Successfully retrieved %s from S3', model)
        return FILE_DIR+model
    except Exception as err:
        logging.error('An error occured fetching the model: %s', str(err))
        if os.path.exists(FILE_DIR+model):
            logging.info('An old model exists, so using that')
            return FILE_DIR+model
        raise

def fetch_race_model():
    """ Returns the race model. """
    return fetch_model(RACE_MODEL)


def fetch_qualifying_model():
    """ Returns the qualifying model. """
    return fetch_model(QUALIFYING_MODEL)
