import boto3
import logging
import tarfile
import os
import sys

QUALIFYING_MODEL = 'qualifying_model'
RACE_MODEL = 'race_model'
FILE_DIR = '/tmp/'
BUCKET = os.getenv('S3_MODEL_BUCKET')

s3 = boto3.client('s3')

def fetch_model(model):
    try:
        s3.download_file(BUCKET, model+'.tar.gz', FILE_DIR+model+'.tar.gz')
        tarfile.open(FILE_DIR+model+'.tar.gz', 'r').extractall(FILE_DIR)
        logging.info('Successfully retrieved ' + model + ' from S3')
        return FILE_DIR+model
    except Exception as e:
        logging.error('An error occured fetching the model: '+str(e))
        if os.path.exists(FILE_DIR+model):
            logging.info('An old model exists, so using that')
            return FILE_DIR+model
        raise

def fetch_race_model():
    return fetch_model(RACE_MODEL)


def fetch_qualifying_model():
    return fetch_model(QUALIFYING_MODEL)

