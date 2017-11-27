链接：https://mp.weixin.qq.com/s/3vFTxKOE9xPoO0xEow70aA
使用深度学习来预测 NBA 比赛结果

2017-11-22 zhengheng 脚本有意思
这篇文章，我们来使用深度学习来预测 NBA 比赛结果，这也是之前的 用深度学习来预测英超比赛结果 https://mp.weixin.qq.com/s/s5F6FzWt8SxeWYxUp8aAhg 的姊妹篇。(有兴趣的话可以从本公众号的历史消息中找到)

通过本文，我们可以学习到：

如何爬取 NBA 技术统计数据；
如何预处理数据；
如何搭建简单的深度网络模型；
如何预测比赛结果。
最终我们得到一个预测第二天比赛准确率 100% 的模型。




( 其实只能说明那天的比赛没有冷门出现 ... )



技术统计数据收集
要用深度学习来预测比赛结果，需要有大量技术统计数据作为学习样本。

来看下官方的技术统计网站：http://stats.nba.com/schedule



打开浏览器的开发者工具，点击每场比赛右边的 BOX SCORE，我们就能看到会请求这样的一个 json 文件：



具体到我们要找的数据统计，是这个 json 里面的 hls (主队数据) 和 vls (客队数据)：

url 是这种格式：

https://data.nba.com/data/10s/v2015/json/mobile_teams/nba/2017/scores/gamedetail/0021700228_gamedetail.json
多尝试几次就可以发现规律：

https://data.nba.com/data/10s/v2015/json/mobile_teams/nba/ 这个是固定的；
2017 是赛季开始年份，比如上赛季则是 2016；
/scores/gamedetail/ 和 最后的 _gamedetail.json 也是固定的；
0021700228 则是比赛的 id，规律为 002 是规定的，17 则是赛季开始年份的后两位，如上赛季是 16；00228 则是 5 位的数字，从 1 开始，不足补零，比如该赛季第一场是 00001，而 00228 就是第 228 场比赛；
抓到的 url 是 https，其实 http 也是支持的，抓取时比 https 快点。
收集脚本比较简单，就是循环获取，然后存 redis。


对于我们要用来跑训练的数据，需要整理成 主队数据 - 客队数据的方式，并增加一个 win or lose 的 label (篮球比赛没有平局)。

127.0.0.1:6379> HGET gamedetaildiff 0021700228_gamedetail.json
"{u'ast': 2, 'win': 1.0, u'fbptsa': 6, u'tf': 1, u'bpts': -4, 'away': u'LAC', u'pip': -2, 'home': u'CHA', u'dreb': 4, u'fga': 4, u'tmtov': 0, u'scp': 14, 'date': u'2017-11-19', u'fbptsm': 5, u'tpa': -3, u'fgm': 1, u'stl': 2, u'fbpts': 10, u'ble': 13, u'tov': -6, u'oreb': 1, u'potov': 16, u'fta': 10, u'pipm': -1, u'pf': -6, u'tmreb': -2, u'blk': 3, u'reb': 5, u'pipa': -4, u'ftm': 10, u'tpm': 3}"
最后一共收集了，2015、2016、2017 至 2017-11-19 三个赛季的有效数据共 2699 条。



数据预处理
我们用 Pandas 来做数据处理，非常方便。

先直接从 redis 里读入数据：

import pandas as pd
import redis
import ast

cli = redis.Redis()
data = cli.hgetall("gamedetaildiff")
df = pd.DataFrame([ast.literal_eval(data[k]) for k in data])
df = df.fillna(value=0.0)   # 用 0 填补空白数据
df.head()

输入数据去掉无关项，整理成训练数据和测试数据：

dataX = df.drop(["win", "date", "home", "away"], axis=1)
dataY = df["win"]
train_x = np.array(dataX)[::2] # train set
train_y = np.array(dataY)[::2]
test_x = np.array(dataX)[1::2] # test set
test_y = np.array(dataY)[1::2]
处理后的数据维度：



搭建深度网络
这部分其实反而是这篇文章中最简单的部分，因为我们有 Keras：

from keras.models import Sequential
from keras.layers.core import Dense

model = Sequential()
model.add(Dense(60, input_dim=train_x.shape[1], activation='relu'))
model.add(Dense(30, activation='relu'))
model.add(Dense(1, activation='sigmoid'))
model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
最简单的三层全连接层网络。

因为网络的输出维度是 1，所以最后一层的激活函数是 sigmoid，损失函数为 binary_crossentropy。



模型训练以及验证


可以看到 10 个 epochs 之后，模型对于训练数据的准确度已经达到了 98.89%

再使用测试数据对该模型进行验证：


训练数据的准确度也达到了 95.40%，说明这个模型还是比较靠谱的。虽然训练花不了几秒钟，但我们还是保存下吧：

model.save("nba-model.hdf5")


新数据的预测
我们有模型可以来预测比赛结果了。现在我们的问题就在于如何模拟对阵双方的技术统计了。

我们用主队上五场主场技术统计均值，和客队上五场客场技术统计均值，两者相减作为模型的预测输入。

先从 redis 获取下完整的数据：

game_detail_data = cli.hgetall("gamedetail")
game_detail_json = []
for k in game_detail_data:
    di_v = {}
    di_h = {}
    j = json.loads(game_detail_data[k])
    vls = j["g"]["vls"]
    hls = j["g"]["hls"]
    di_v.update(vls["tstsg"])
    di_v.update({"date": j["g"]["gdtutc"], "name": vls["ta"], "home": 0})
    game_detail_json.append(di_v)
    di_h.update(hls["tstsg"])
    di_h.update({"date": j["g"]["gdtutc"], "name": hls["ta"], "home": 1})
    game_detail_json.append(di_h)
game_detail_df = pd.DataFrame(game_detail_json)
game_detail_df = game_detail_df.fillna(value=0.0)
用 Pandas 可以一行代码实现 找到主队上五场主场数据均值 的功能：

def predict(home=None, away=None):
    home_data = game_detail_df[(game_detail_df['name']==home) & (game_detail_df['home']==1)].sort_values(by='date', ascending=False)[:5].mean()
    away_data = game_detail_df[(game_detail_df['name']==away) & (game_detail_df['home']==0)].sort_values(by='date', ascending=False)[:5].mean()
    home_data = home_data.drop(['home'])
    away_data = away_data.drop(['home'])
    new_x = np.array(home_data - away_data)
    return model.predict_classes(new_x[np.newaxis,:], verbose=0)[0][0]
预测效果
数据只收集到美国时间 2017-11-19：


我们来看下 2017-11-20 那天的比赛结果：

跑下我们模型的预测结果：


11 场全部正确，amazing !!


