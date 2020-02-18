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
        if int(year) > 1980:
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

def get_qualifying_results_as_differences():
    result = {}
    for race, results in qualifying.items():
        lap_times = list(results.values())
        if len(lap_times):
            fastest_lap = min(lap_times)
            if race not in result:
                result[race] = {}
            for driver, qualifying_result in results.items():
                result[race][driver] = round((qualifying_result - fastest_lap),3)
    return result


qualifying_as_differences = get_qualifying_results_as_differences()

def get_previous_qualifying_result_as_differences(race, driver):
    if race in qualifying_as_differences and driver in qualifying_as_differences[race]:
        other_races = races_by_name[race_list[race]]
        previous_race_index = other_races.index(race) - 1
        if previous_race_index >= 0:
            previous_race_id = other_races[previous_race_index]
            if previous_race_id in qualifying_as_differences and driver in qualifying_as_differences[previous_race_id]:
                return qualifying_as_differences[previous_race_id][driver]
    return None


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
                    diff = qualifying_lap - previous_qualifying_lap
                    total += diff
                    count += 1
        if count > 0:
            return round(total/count, 3)
    return None

def get_average_change_by_differences(race, driver):
    total = 0
    count = 0
    if race in years_by_race:
        year = years_by_race[race]
        races_in_year = races_by_year[year]
        for season_race in races_in_year:
            if season_race in qualifying_as_differences and driver in qualifying_as_differences[season_race]:
                qualifying_lap = qualifying_as_differences[season_race][driver]
                previous_qualifying_lap = get_previous_qualifying_result_as_differences(season_race, driver)
                if previous_qualifying_lap:
                    diff = qualifying_lap - previous_qualifying_lap
                    total += diff
                    count += 1
        if count > 0:
            return round(total/count, 3)
    return None

def get_season_change(race):
    total = 0
    count = 0
    if race in years_by_race:
        year = years_by_race[race]
        races_in_year = races_by_year[year]
        for season_race in races_in_year:
            if season_race in qualifying:
                for driver, lap in qualifying[season_race].items():
                    previous_qualifying_lap = get_previous_qualifying_result(season_race, driver)
                    if previous_qualifying_lap:
                        diff = lap - previous_qualifying_lap
                        total += diff
                        count += 1
        if count > 0:
            return round(total/count, 3)
    return None

def get_average_change_by_differences_at_that_point(race, driver):
    total = 0
    count = 0
    if race in years_by_race:
        year = years_by_race[race]
        races_in_year = races_by_year[year]
        for season_race in races_in_year:
            if season_race <= race:
                if season_race in qualifying_as_differences and driver in qualifying_as_differences[season_race]:
                    qualifying_lap = qualifying_as_differences[season_race][driver]
                    previous_qualifying_lap = get_previous_qualifying_result_as_differences(season_race, driver)
                    if previous_qualifying_lap:
                        diff = qualifying_lap - previous_qualifying_lap
                        total += diff
                        count += 1
            if count > 0:
                return round(total/count, 3)
        return None


def get_fastest_qualifying_lap():
    result = {}
    for race, results in qualifying.items():
        lap_times = list(results.values())
        if len(lap_times):
            fastest_lap = min(lap_times)
            result[race] = fastest_lap
    return result

fastest_laps = get_fastest_qualifying_lap()

def get_results(races):
    results = {
        'result': [],
        'race': [],
        'change': [],
        'fastest_lap': [],
        'lap': [],
        'season_change': []
    }
    for race in races:
        if race in positions and race != "748":
            race_results = positions[race]
            for driver, position in race_results.items():
                previous_result = get_previous_qualifying_result_as_differences(race, driver)
                average_change = get_average_change_by_differences_at_that_point(race, driver)
                season_change = get_season_change(race)
                if previous_result and average_change and season_change:
                    results['fastest_lap'].append(fastest_laps[race])
                    results['lap'].append(previous_result)
                    results['result'].append(qualifying[race][driver])
                    results['race'].append(race_list[race])
                    results['change'].append(average_change)
                    results['season_change'].append(season_change)
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
    tf.feature_column.numeric_column(key='fastest_lap'),
    tf.feature_column.numeric_column(key='season_change'),
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
    'race': np.array(['british', 'british', 'british','british', 'british', 'british','british', 'british']),
    'lap': np.array([0.325, 0.000,1.987,0.710,2.461,0.044, 1.207, 2.009]),
    'change': np.array([-0.339, -0.12, -1.076, 0.078, -0.988, 0.734, 1.569, 1.364]),
    'fastest_lap': np.array([85.892,85.892,85.892,85.892,85.892,85.892,85.892,85.892]),
    'season_change': np.array([-1.817, -1.817, -1.817, -1.817, -1.817, -1.817, -1.817, -1.817])
}

test_input_fn1 = tf.estimator.inputs.numpy_input_fn(
    x=test_features1,
    num_epochs=1,
    shuffle=False
)


predictions = model.predict(input_fn=test_input_fn1)

predictions_list = list(predictions)

results = []
for i in range(0, len(predictions_list)):
    results.append((i, float(predictions_list[i]['predictions'][0])))
print(results)

sorted_results = sorted(results, key=lambda tup: tup[1])

fastest_lap = sorted_results[0][1]

differences = []

print(sorted_results)

for item in sorted_results:
    differences.append(item[1]-fastest_lap)

print(differences)

'''print(get_average_change_by_differences_at_that_point('1019', '822'))
print(get_average_change_by_differences_at_that_point('1019', '1'))
print(get_average_change_by_differences_at_that_point('1019', '844'))
print(get_average_change_by_differences_at_that_point('1019', '830'))
print(get_average_change_by_differences_at_that_point('1019', '842'))
print(get_average_change_by_differences_at_that_point('1019', '20'))
print(get_average_change_by_differences_at_that_point('1019', '817'))
print(get_average_change_by_differences_at_that_point('1019', '807'))'''

