import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
import math

dataset_house = pd.read_csv("./housing.csv")

x_data = dataset_house.drop(['median_house_value'], axis=1)
y = dataset_house['median_house_value']

x_subset = x_data.drop(['ocean_proximity'], axis=1)
print(x_subset)
x_ocean = x_data['ocean_proximity']

scaler = MinMaxScaler()
x_subset = pd.DataFrame(scaler.fit_transform(x_subset), columns=x_subset.columns, index=x_subset.index)

print(dataset_house.head(2))
x_data = pd.concat([x_subset, x_ocean], axis=1)
print(x_data.head(2))

x_data['total_bedrooms'].fillna(x_data['total_bedrooms'].mean(), inplace = True)

x_train, x_test, y_train, y_test = train_test_split(x_data, y, test_size=0.3)

longitude = tf.feature_column.numeric_column('longitude')
latitude = tf.feature_column.numeric_column('latitude')
median_age = tf.feature_column.numeric_column('housing_median_age')
total_rooms = tf.feature_column.numeric_column('total_rooms')
total_bedroom = tf.feature_column.numeric_column('total_bedrooms')
population = tf.feature_column.numeric_column('population')
households = tf.feature_column.numeric_column('households')
median_income = tf.feature_column.numeric_column('median_income')

ocean_proximity = tf.contrib.layers.sparse_column_with_hash_bucket('ocean_proximity',hash_bucket_size=1000)

embedding_size = int(math.floor(len(x_data.ocean_proximity.unique())**0.25))
print(embedding_size)

ocean_proximity=tf.contrib.layers.embedding_column(sparse_id_column=ocean_proximity, dimension=embedding_size)

feature_col = [latitude, longitude,median_age, total_rooms, total_bedroom, population, households, median_income, ocean_proximity]

opti = tf.train.AdamOptimizer(learning_rate = 0.01)

input_func = tf.estimator.inputs.pandas_input_fn(x=x_train, 
    y= y_train, 
    batch_size=10, 
    num_epochs=1000, 
    shuffle=True)


test_input_func = tf.estimator.inputs.pandas_input_fn(x= x_test,                                                   
    batch_size=100, 
    num_epochs=1, 
    shuffle=False)

eval_input_func = tf.estimator.inputs.pandas_input_fn(x=x_test,
    y=y_test, 
    batch_size=10, 
    num_epochs=1, 
    shuffle=False)


estimator = tf.estimator.DNNRegressor(hidden_units=[9,9,3], feature_columns=feature_col, optimizer=opti, dropout=0.5, model_dir='model/')

#estimator.train(input_fn=input_func,steps=20000)

#result_eval = estimator.evaluate(input_fn=eval_input_func)

#print(result_eval)
predictions = []
for pred in estimator.predict(input_fn=test_input_func):
    predictions.append(np.array(pred['predictions']).astype(float))

print(predictions[0])

print(x_test.head(1))
