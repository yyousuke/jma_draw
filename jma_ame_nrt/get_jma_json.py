#!/usr/bin/env python3
from pandas import DataFrame
import pandas as pd
import numpy as np
import os
import time
import json
import urllib.request
from datetime import datetime, timedelta

# 取得する時刻（Trueとすれば、最新のものを取得）
# opt_latest = True
opt_latest = False


class AmedasStation():
    """AMeDASデータを取得し、ndarrayに変換する"""

    def __init__(self, latest=None):
        """
        Parameters:
        ----------
        latest: str
            取得する時刻（形式：20210819120000）
        ----------
        """
        url = "https://www.jma.go.jp/bosai/amedas/data/latest_time.txt"
        if latest is None:
            latest = np.loadtxt(urllib.request.urlopen(url), dtype="str")
        print(latest)
        self.latest_time = pd.to_datetime(latest).strftime("%Y%m%d%H%M%S")
        print(self.latest_time)

    def retrieve(self):
        """アメダスデータ取得
        Returns:
        ----------
        df: ndarray
            アメダスデータ
        ----------
        """
        url_top = "https://www.jma.go.jp/bosai/amedas/data/map/"
        file_name = self.latest_time + ".json"
        if os.path.exists(file_name):  # 既に取得している場合
            return None
        # アメダスデータの取得
        url = url_top + file_name
        print(url)
        urllib.request.urlretrieve(url, file_name)
        try:
            with open(file_name, 'rt') as fin:
                data = fin.read()
        except OSError as e:
            raise OSError(e)
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
        """アメダス地点情報の取得"""
        url_top = "https://www.jma.go.jp/bosai/amedas/const/"
        file_name = "amedastable.json"
        # アメダス地点情報の取得
        url = url_top + file_name
        if not os.path.exists(file_name):
            print(url)
            urllib.request.urlretrieve(url, file_name)
        try:
            with open(file_name, 'rt') as fin:
                data = fin.read()
        except OSError as e:
            raise OSError(e)
        df = DataFrame(json.loads(data))
        # 取り出したデータを返却
        return df.T


if __name__ == '__main__':

    if opt_latest:  # 最新のものを取得
        # AmedasStation Classの初期化
        amedas = AmedasStation()
        # AmedasStation.retrieveメソッドを使い、アメダスデータを取得
        df = amedas.retrieve()
        print(df)
    else:  # 指定した時刻範囲で取得(opt_latest = Falseの場合のみ有効)
        # 開始・終了時刻
        time_sta = datetime(2021, 6, 30, 0, 0, 0)
        time_end = datetime(2021, 7, 19, 20, 30, 0)
        time_step = timedelta(minutes=10)
        time_now = time_sta
        while True:
            if time_now <= time_end:
                latest = time_now.strftime("%Y-%m-%dT%H:%M:%S+09:00")
                # latest = "2021-05-02T14:30:00+09:00"
                print(latest)
                # AmedasStation Classの初期化
                amedas = AmedasStation(latest)
                # AmedasStation.retrieveメソッドを使い、アメダスデータを取得
                df = amedas.retrieve()
                if df is not None:
                    time.sleep(10.0)  # 10秒間待つ
            else:
                break
            time_now = time_now + time_step
