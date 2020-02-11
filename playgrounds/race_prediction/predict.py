import csv
import random
import numpy as np
import tensorflow as tf

def get_positions():
    result = {}
    with open('data/results.csv', newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='"')
        for row in reader:
            if row[1] not in result:
                result[row[1]] = {}
            result[row[1]][row[2]] = row[6]
    return result

def get_grid_positions():
    result = {}
    with open('data/results.csv', newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='"')
        for row in reader:
            if row[1] not in result:
                result[row[1]] = {}
            result[row[1]][row[2]] = int(row[5])
    return result

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

def get_qualifying_results_as_differences():
    result = {}
    qualifying_results = get_qualifying_results()
    for race, results in qualifying_results.items():
        lap_times = list(results.values())
        if len(lap_times):
            fastest_lap = min(lap_times)
            if race not in result:
                result[race] = {}
            for driver, qualifying_result in results.items():
                result[race][driver] = round((qualifying_result - fastest_lap),3)
    return result

def convert_to_seconds(time):
    parts = time.split(':')
    if len(parts) == 2:
        return (int(parts[0]) * 60) + float(parts[1])
    return 999999999

def get_races():
    result = {}
    with open('data/races.csv', newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='"')
        for row in reader:
            result[row[0]] = row[4].lower().replace('grand prix', '').strip()
    return result


def get_drivers():
    result = {}
    with open('data/driver.csv', newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='"')
        for row in reader:
            result[row[0]] = row[1]
    return result


def get_races_by_year():
    result = {}
    with open('data/races.csv', newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='"')
        for row in reader:
            if row[1] not in result:
                result[row[1]] = []
            result[row[1]].append(row[0])
    return result


def split_race_ids():
    training_races = []
    test_races = []
    races_by_year = get_races_by_year()
    for year, items in races_by_year.items():
        train_results_len = int(0.9 * len(items))
        random.shuffle(items)
        training_races += items[:train_results_len]
        test_races += items[train_results_len:]
    return training_races, test_races


driver_feature = tf.feature_column.categorical_column_with_vocabulary_list(
      'driver', list(set(get_drivers().values())))

race_feature = tf.feature_column.categorical_column_with_vocabulary_list(
      'race', sorted(list(set(get_races().values()))))

def get_results(races):
    results = {
        'driver': [],
        'result': [],
        'race': [],
        'qualifying': [],
        'grid': []
    }
    positions = get_positions()
    grid_positions = get_grid_positions()
    qualifying = get_qualifying_results_as_differences()
    race_names = get_races()
    drivers = get_drivers()
    for race in races:
        if race in positions and race != "748":
            race_results = positions[race]
            for driver, position in race_results.items():
                result = 'DNF'
                if position.isdigit() and int(position) <= 20:
                    result = position
                if race in qualifying and driver in qualifying[race] and race in grid_positions and driver in grid_positions[race]:
                    results['driver'].append(drivers[driver])
                    results['result'].append(result)
                    results['race'].append(race_names[race])
                    results['qualifying'].append(qualifying[race][driver])
                    results['grid'].append(grid_positions[race][driver])
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

feature_columns = [
    tf.feature_column.numeric_column(key='qualifying'),
    tf.feature_column.numeric_column(key='grid'),
    tf.feature_column.indicator_column(race_feature)
]


model = tf.estimator.DNNClassifier(
    model_dir='model/',
    hidden_units=[10],
    feature_columns=feature_columns,
    n_classes=21,
    label_vocabulary=['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', 'DNF'],
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

        csvwriter.writerow([(i + 1) * 100, evaluation_result['accuracy'], evaluation_result['average_loss']])'''

test_features1 = {
    'race': np.array(['british', 'british', 'british', 'british', 'british', 'british', 'british', 'british', 'british', 'british']),
    'qualifying': np.array([0.000, 0.006, 0.079, 0.183, 0.497, 0.694, 1.089, 1.131, 1.242, 1.293]),
    'grid': np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
}

test_input_fn1 = tf.estimator.inputs.numpy_input_fn(
    x=test_features1,
    num_epochs=1,
    shuffle=False
)


results = {}

predictions = model.predict(input_fn=test_input_fn1)
for pred_dict in predictions:
    class_id = pred_dict['class_ids'][0]
    for position in range(0,11):
        if position not in results:
            results[position] = []
        results[position].append(pred_dict['probabilities'][position])
    #print('Prediction is "{}" ({:.1f}%),'.format(
        #SPECIES[class_id], 100 * probability))



for position, values in results.items():
    sumOfValues = sum(values)
    for index in range(0, len(values)):
        results[position][index] = round((results[position][index] / sumOfValues), 3)

print(results)

