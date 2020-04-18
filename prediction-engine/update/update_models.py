
import logging
import traceback
import tensorflow as tf
import numpy as np
from ..common.race import train as train_race

db = Database.get_database()

def update_models():
    logging.info("Training race model")
    train_race()
    
