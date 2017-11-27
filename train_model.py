from keras.models import Sequential
from keras.layers.core import Dense
import pandas as pd
import redis
import ast
import json
import numpy as np

cli = redis.Redis()
data = cli.hgetall("gamedetaildiff")

# ast.literal_eval 是将字符串转换成对应的对象
df = pd.DataFrame([ast.literal_eval(data[k].decode('gbk')) for k in data])
# df = pd.DataFrame([json.loads(data[k].decode('gbk')) for k in data])
df = df.fillna(value=0.0)
# df = df.replace("NaN", 0)
df.head()
print(df)

dataX = df.drop(["win", "date", "home", "away"], axis=1)
dataY = df["win"]
# train_x = np.array(dataX)[::2] # train set
train_x = np.array(dataX)[1230:] # train set
print(train_x)
# train_y = np.array(dataY)[::2]
train_y = np.array(dataY)[1230:]
print(train_y)
test_x = np.array(dataX)[1::2] # test set   [start:end:间隔]
test_y = np.array(dataY)[1::2]
print(train_x.shape, train_y.shape, test_x.shape, test_y.shape)
model = Sequential()
model.add(Dense(60, input_dim=train_x.shape[1], activation='relu'))
model.add(Dense(30, activation='relu'))
model.add(Dense(1, activation='sigmoid'))
model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])

model.summary()
model.fit(train_x, train_y, batch_size=16, epochs=10)
print("*********************************")
model.evaluate(test_x, test_y)

model.save("nba-model.hdf5")