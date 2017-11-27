from urllib.request import urlopen
import json
import logging
import redis

urlstr = "https://data.nba.com/data/10s/v2015/json/mobile_teams/nba/2017/scores/gamedetail/0021700129_gamedetail.json"
urlstr1 = "https://data.nba.com/data/10s/v2015/json/mobile_teams/nba/2017/scores/gamedetail/0021700276_gamedetail.json"
print(urlstr1.split("/")[-1])
for i in range(1230):
    j = 1700001+i+275
    urlstr = "https://data.nba.com/data/10s/v2015/json/mobile_teams/nba/"+str(2017)+"/scores/gamedetail/002"+str(j)+"_gamedetail.json"
    print(urlstr)
    jsondata = urlopen(urlstr)

    text = jsondata.read().decode('utf-8')   # 将bytes类型转换成string
    print(type(jsondata.read()))  # bytes 类型
    print(str(jsondata.read()))
    data = json.loads(text)
    print(type(data))
    print(data)

    print(data['g']['stt'])

    di = {}

    stt = data["g"]["stt"]
    key = urlstr.split("/")[-1]
    print("key:", key)
    if(stt.endswith("Qtr")):
        logging.warning("%s game is not finished" % key)

    vls = data['g']['vls']
    hls = data['g']['hls']
    vs = int(vls['s'])
    hs = int(hls['s'])
    print(vs)
    print(hs)

    # win or loss
    w = 1.0 if hs>vs else 0.0
    di.update({"win": w})
    # stats iff
    vsts = vls["tstsg"]
    hsts = hls["tstsg"]

    print(vsts)
    print(hsts)

    for k in hsts:
        di.update({k:int(hsts[k])-int(vsts[k])})

    # team name
    vn = vls["ta"]
    hn = hls["ta"]
    di.update({"home": hn, "away": vn})

    # game date
    date = data["g"]["gdtutc"]
    di.update({"date": date})

    cli = redis.Redis()
    cli.hset("gamedetaildiff", key, str(di))
    logging.info("%s save success" % key)
    cli.hset("gamedetail", key, text)

