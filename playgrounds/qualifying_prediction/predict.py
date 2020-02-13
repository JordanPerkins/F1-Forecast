import csv
import random
import numpy as np
import tensorflow as tf


def get_races_by_year():
    result = {}
    with open('data/races.csv', newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='"')
        for row in reader:
            if row[1] not in result:
                result[row[1]] = []
            result[row[1]].append(row[0])
    return result


def convert_to_seconds(time):
    parts = time.split(':')
    if len(parts) == 2:
        return (int(parts[0]) * 60) + float(parts[1])
    return 999999999


def get_qualifying_results():
    result = {}
    with open('data/qualifying.csv', newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='"')
        for row in reader:
            if row[1] not in result:
                result[row[1]] = {}
            if ":" in row[8]:
                result[row[1]][row[2]] = convert_to_seconds(row[8])
            elif ":" in row[7]:
                result[row[1]][row[2]] = convert_to_seconds(row[7])
            elif ":" in row[6]:
                result[row[1]][row[2]] = convert_to_seconds(row[6])
    return result


def get_races():
    result = {}
    with open('data/races.csv', newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='"')
        for row in reader:
            result[row[0]] = row[4].lower().replace('grand prix', '').strip()
    return result


def get_races_by_name():
    result = {}
    races = get_races()
    for id, race in races.items():
        if race not in result:
            result[race] = []
        result[race].append(id)
    return result


def get_positions():
    result = {}
    with open('data/results.csv', newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='"')
        for row in reader:
            if row[1] not in result:
                result[row[1]] = {}
            result[row[1]][row[2]] = row[6]
    return result


race_list = get_races()
positions = get_positions()
qualifying = get_qualifying_results()
races_by_name = get_races_by_name()
races_by_year = get_races_by_year()


def split_race_ids():
    training_races = []
    test_races = []
    for year, items in races_by_year.items():
        if int(year) > 2014:
            train_results_len = int(0.9 * len(items))
            random.shuffle(items)
            training_races += items[:train_results_len]
            test_races += items[train_results_len:]
    return training_races, test_races


def get_previous_qualifying_result(race, driver):
    if race in qualifying and driver in qualifying[race]:
        other_races = races_by_name[race_list[race]]
        previous_race_index = other_races.index(race) - 1
        if previous_race_index >= 0:
            previous_race_id = other_races[previous_race_index]
            if previous_race_id in qualifying and driver in qualifying[previous_race_id]:
                return qualifying[previous_race_id][driver]
    return None


def get_years_by_race():
    result = {}
    for year, ids in races_by_year.items():
        for id in ids:
            result[id] = year
    return result


years_by_race = get_years_by_race()


def get_average_change(race, driver):
    total = 0
    count = 0
    if race in years_by_race:
        year = years_by_race[race]
        races_in_year = races_by_year[year]
        for season_race in races_in_year:
            if season_race in qualifying and driver in qualifying[season_race]:
                qualifying_lap = qualifying[season_race][driver]
                previous_qualifying_lap = get_previous_qualifying_result(season_race, driver)
                if previous_qualifying_lap:
                    diff = previous_qualifying_lap - qualifying_lap
                    total += diff
                    count += 1
        if count > 0:
            return round(total/count, 3)
    return None


def get_results(races):
    results = {
        'result': [],
        'race': [],
        'change': [],
        'lap': []
    }
    for race in races:
        if race in positions and race != "748":
            race_results = positions[race]
            for driver, position in race_results.items():
                previous_result = get_previous_qualifying_result(race, driver)
                average_change = get_average_change(race, driver)
                if previous_result and average_change:
                    results['lap'].append(previous_result)
                    results['result'].append(qualifying[race][driver])
                    results['race'].append(race_list[race])
                    results['change'].append(average_change)
    for key in results.keys():
        results[key] = np.array(results[key])
    return results, results['result']


training_races, test_races = split_race_ids()
train_features, train_labels = get_results(training_races)
test_features, test_labels = get_results(test_races)

train_input_fn = tf.estimator.inputs.numpy_input_fn(
    x=train_features,
    y=train_labels,
    batch_size=500,
    num_epochs=None,
    shuffle=False
)

test_input_fn = tf.estimator.inputs.numpy_input_fn(
    x=test_features,
    y=test_labels,
    num_epochs=1,
    shuffle=False
)

race_feature = tf.feature_column.categorical_column_with_vocabulary_list(
      'race', sorted(list(set(race_list.values()))))

feature_columns = [
    tf.feature_column.numeric_column(key='change'),
    tf.feature_column.numeric_column(key='lap'),
    tf.feature_column.indicator_column(race_feature)
]

model = tf.estimator.DNNRegressor(
    model_dir='model/',
    hidden_units=[10],
    feature_columns=feature_columns,
    optimizer=tf.train.ProximalAdagradOptimizer(
        learning_rate=0.1,
        l1_regularization_strength=0.001
    ))

'''with open('training-log.csv', 'w') as stream:
    csvwriter = csv.writer(stream)

    for i in range(0, 200):
        model.train(input_fn=train_input_fn, steps=100)
        evaluation_result = model.evaluate(input_fn=test_input_fn)

        predictions = list(model.predict(input_fn=test_input_fn))

        print(evaluation_result)

        csvwriter.writerow([(i + 1) * 100, evaluation_result['loss'], evaluation_result['average_loss']])'''


test_features1 = {
    'race': np.array(['british']),
    'lap': np.array([89.607]),
    'change': np.array([-0.800])
}

test_input_fn1 = tf.estimator.inputs.numpy_input_fn(
    x=test_features1,
    num_epochs=1,
    shuffle=False
)


predictions = model.predict(input_fn=test_input_fn1)

print(list(predictions))



