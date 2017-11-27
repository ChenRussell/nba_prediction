import pandas as pd
import redis
import ast
import json
import numpy as np
from keras.models import load_model

cli = redis.Redis()
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

def predict(away=None, home=None):
    home_data = game_detail_df[(game_detail_df['name']==home) & (game_detail_df['home']==1)].sort_values(by='date', ascending=False)[:5].mean()
    away_data = game_detail_df[(game_detail_df['name']==away) & (game_detail_df['home']==0)].sort_values(by='date', ascending=False)[:5].mean()
    home_data = home_data.drop(['home'])
    away_data = away_data.drop(['home'])
    new_x = np.array(home_data - away_data)
    model = load_model('nba-model.hdf5')
    return model.predict_classes(new_x[np.newaxis,:], verbose=0)[0][0]

teams = [
    ["POR", "BKN"],
    ["NYK", "ATL"],
    ["ORL", "BOS"],
    ["CHA", "CLE"],
    ["TOR", "IND"],
    ["MIA", "MIN"],
    ["DET", "OKC"],
    ["MEM", "DEN"],
    ["NOP", "PHX"],
    ["CHI", "GSW"]
]
teams_tom = [
    ["SAS", "CHA"],
    ["ORL", "PHI"],
    ["POR", "WAS"],
    ["TOR", "ATL"],
    ["BOS", "IND"],
    ["NYK", "HOU"],
    ["OKC", "DAL"],
    ["NOP", "GSW"],
    ["MIL", "UTA"],
    ["LAC", "SAC"]
]
teams_27 = [
    ["MIA", "CHI"],
    ["PHX", "MIN"],
    ["BKN", "MEM"]
]
for t in teams_27:
    p = predict(t[0], t[1])
    if p==1:
        print("%s(loss) vs %s( win)" % (t[0], t[1]))
    else:
        print("%s( win) vs %s(loss)" % (t[0], t[1]))
