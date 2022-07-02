#!/usr/bin/env python3
from pandas import DataFrame
import pandas as pd
import numpy as np
import os
import json
import urllib.request

# 取得する時刻（Noneとすれば、最新のものを取得）
latest = None
# latest = "2021-05-02T14:30:00+09:00"


# データ取得部分
class AmedasStation():
    def __init__(self, latest=None):
        url = "https://www.jma.go.jp/bosai/amedas/data/latest_time.txt"
        if latest is None:
            latest = np.loadtxt(urllib.request.urlopen(url), dtype="str")
        print(latest)
        self.latest_time = pd.to_datetime(latest).strftime("%Y%m%d%H%M%S")
        print(self.latest_time)

    def retrieve(self):
        url_top = "https://www.jma.go.jp/bosai/amedas/data/map/"
        file_name = self.latest_time + ".json"
        # アメダスデータの取得
        url = url_top + file_name
        print(url)
        urllib.request.urlretrieve(url, file_name)
        with open(file_name, 'rt') as fin:
            data = fin.read()
        df = DataFrame(json.loads(data)).T
        # アメダス地点情報の取得
        df_location = self.location()
        df["lon"] = df_location.loc[:, "lon"]
        df["lat"] = df_location.loc[:, "lat"]
        df["kjName"] = df_location.loc[:, "kjName"]
        df["knName"] = df_location.loc[:, "knName"]
        df["enName"] = df_location.loc[:, "enName"]
        # csvファイルとして保存
        df.to_csv(self.latest_time + ".csv")
        #
        # 取り出したデータを返却
        return df

    def location(self):
        url_top = "https://www.jma.go.jp/bosai/amedas/const/"
        file_name = "amedastable.json"
        # アメダス地点情報の取得
        url = url_top + file_name
        if not os.path.exists(file_name):
            print(url)
            urllib.request.urlretrieve(url, file_name)
        with open(file_name, 'rt') as fin:
            data = fin.read()
        df = DataFrame(json.loads(data))
        # 取り出したデータを返却
        return df.T


if __name__ == '__main__':

    # AmedasStation Classの初期化
    amedas = AmedasStation(latest)
    # AmedasStation.retrieveメソッドを使い、アメダスデータを取得
    df = amedas.retrieve()
    print(df)
