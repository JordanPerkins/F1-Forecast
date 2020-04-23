""" Handles fetching and uploading of the model to the S3 bucket. """

import logging
import tarfile
import os
import boto3
import shutil

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

def upload_model(model):
    """ Attempts to upload the model with the given name. """
    with tarfile.open(FILE_DIR+model+'.tar.gz', "w:gz") as tar_handle:
        tar_handle.add(FILE_DIR+model)
    s3.upload_file(FILE_DIR+model+'.tar.gz', BUCKET, model+'.tar.gz')

def fetch_race_model(load_model=True):
    """ Returns the race model. """
    if load_model:
        return fetch_model(RACE_MODEL)
    return FILE_DIR+RACE_MODEL

def fetch_qualifying_model(load_model=True):
    """ Returns the qualifying model. """
    if load_model:
        return fetch_model(QUALIFYING_MODEL)
    return FILE_DIR+QUALIFYING_MODEL

def upload_race_model():
    """ Returns the race model. """
    return upload_model(RACE_MODEL)

def upload_qualifying_model():
    """ Returns the qualifying model. """
    return upload_model(QUALIFYING_MODEL)

def delete_model(model):
    if os.path.exists(FILE_DIR+model):
        shutil.rmtree(FILE_DIR+model)

def delete_race_model():
    delete_model(RACE_MODEL)

def delete_qualifying_model():
    delete_model(QUALIFYING_MODEL)
