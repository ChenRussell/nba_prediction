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
df.fillna(value=0.0)
df.head()
print(df.head())
# for k in data:
#     print(type(data[k]))
#     print(type(data[k].decode('gbk')))
#     print(data[k])

dataX = df.drop(["win", "date", "home", "away"], axis=1)
dataY = df["win"]
train_x = np.array(dataX)[::2] # train set
print(train_x)
train_y = np.array(dataY)[::2]
print(train_y)
test_x = np.array(dataX)[1::2] # test set
test_y = np.array(dataY)[1::2]

print(train_x.shape, train_y.shape, test_x.shape, test_y.shape)