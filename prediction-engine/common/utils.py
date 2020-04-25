""" A set of utility functions common to multiple modules. """

import hashlib

def tuples_to_dictionary(tuples):
    """ Converts tuples to a dictionary indexed on the first value. """
    result = {}
    for item in tuples:
        if item[0] not in result:
            result[item[0]] = []
        result[item[0]].append(item[1:])
    return result


def ranking_to_dictionary(ranking):
    """ Converts ranking tuples to a dictionary (json) object """
    result = []
    for driver in ranking:
        driver_quali_result = float(driver[-1]) if len(driver) > 9 else None
        result.append({
            'driver_id': driver[0],
            'driver_ref': driver[1],
            'driver_num': driver[2],
            'driver_code': driver[3],
            'driver_forename': driver[4],
            'driver_surname': driver[5],
            'driver_dob': driver[6],
            'driver_nationality': driver[7],
            'driver_wiki': driver[8],
            'driver_quali_result': driver_quali_result
        })
    return result

def generate_feature_hash(features):
    """ Generate a unique hash of the features. """
    strings = [features['race'][0]]

    for key, array in features.items():
        if key is not 'race':
            strings.append((',').join([str(item) for item in array]))

    hash_string = '|'.join(strings)
    hash_result = hashlib.sha256(hash_string.encode()).hexdigest()
    return hash_result, hash_string
