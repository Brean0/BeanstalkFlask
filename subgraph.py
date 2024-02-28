import requests
import json
import numpy as np
url = 'https://graph.node.bean.money/subgraphs/name/beanstalk-testing'

body = """
{
  metapoolOracles(orderBy: season, orderDirection: desc, first: 168) {
    deltaB
    season
  }
  fieldHourlySnapshots(
    orderBy: season
    orderDirection: desc
    first: 168
    where: {podRate_gt: "0"}
  ) {
    season
    podRate
  }
  beanstalks {
    seasons(orderBy: season, orderDirection: desc, first: 168) {
      marketCap
      price
      season
      beans
    }
  }
  farmers(
    orderBy: silo__stalk
    orderDirection: desc
    where: {silo_: {stalk_gt: "0"}}
    first: 1000
  ) {
    silo {
      stalk
    }
  }
}
"""

def getSubgraphData():
    response = requests.post(url=url, json={"query": body})
    if response.status_code == 200:
        return json.loads(response.content)
    return None

def getBeanstalkData() -> tuple:
    json = getSubgraphData()
    metapoolOracles = json['data']['metapoolOracles']
    fieldHourlySnapshots = json['data']['fieldHourlySnapshots']
    beanstalks = json['data']['beanstalks'][0]['seasons']
    latestSeason = beanstalks[0]['season']
    # convert the dict into numpy arrays:
    deltaB = np.array([int(x['deltaB']) for x in metapoolOracles])
    podRate = np.array([float(x['podRate']) for x in fieldHourlySnapshots])
    beans = np.array([float(x['beans']) for x in beanstalks])
    price = np.array([float(x['price']) for x in beanstalks])
    stalk = np.array([int(x['silo']['stalk']) for x in json['data']['farmers']]) / 1e10
    data = [deltaB, podRate, beans, price, stalk]
    return(data, latestSeason)