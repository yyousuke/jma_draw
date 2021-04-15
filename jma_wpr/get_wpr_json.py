#!/usr/bin/env python3
from pandas import Series, DataFrame
import pandas as pd
import numpy as np
import os
import json
import urllib.request


# データ取得部分
class WprStation():
    def __init__(self, station_no=None):
        self.station_no = str(station_no)

    def retrieve(self, time_list=None, opt_retrieve=True):
        url_top = "https://www.jma.go.jp/bosai/windprofiler/data/"
        file_name = self.station_no + ".json"
        # WPRデータの取得
        url = url_top + file_name
        print(url)
        if opt_retrieve:
            urllib.request.urlretrieve(url, file_name)
        # 配列の初期化（z方向はデータ長よりも長く)
        size = (50, )
        z = np.ones(size) * np.nan
        with open(file_name, 'rt') as fin:
            data = fin.read()
        d = json.loads(data)
        #
        u = []
        v = []
        w = []
        zmax = 0
        for tinfo in time_list:
            # 配列の初期化（データ長よりも長い配列作成)
            u_o = np.ones(size) * np.nan
            v_o = np.ones(size) * np.nan
            w_o = np.ones(size) * np.nan
            df = DataFrame(d[tinfo])
            #df = DataFrame(d['20210321064000'])
            u_i, v_i, w_i, z_i = self._divide(df)
            u_o[0:u_i.shape[0]] = u_i
            v_o[0:v_i.shape[0]] = v_i
            w_o[0:w_i.shape[0]] = w_i
            print(tinfo, "zlevs =", len(z_i))
            if len(z_i) > zmax:
                z[0:w_i.shape[0]] = z_i
                zmax = len(z_i)
            u.append(u_o)
            v.append(v_o)
            w.append(w_o)
        #
        # 取り出したデータを返却
        return np.array(u), np.array(v), np.array(w), np.array(z), zmax

    def _divide(self, df):
        u = df.loc[:, 'u']
        v = df.loc[:, 'v']
        w = df.loc[:, 'w']
        z = df.loc[:, 'height']
        return u, v, w, z

def wpr_time(opt_retrive=True):
    url_top = "https://www.jma.go.jp/bosai/windprofiler/data/"
    file_name = "times.json"
    if opt_retrieve and os.path.exists(file_name):
        os.remove(file_name)
    # アメダス地点情報の取得
    url = url_top + file_name
    if not os.path.exists(file_name):
        print(url)
        urllib.request.urlretrieve(url, file_name)
    with open(file_name, 'rt') as fin:
        data = fin.read()
    df = DataFrame(json.loads(data))
    # 取り出したデータを返却
    return df


def wpr_location():
    url_top = "https://www.jma.go.jp/bosai/windprofiler/const/"
    file_name = "station.json"
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

    # データを取得するかどうか
    opt_retrieve = True
    #opt_retrieve = False
    # WPRデータの時刻を取得
    t = wpr_time(opt_retrive=True)
    time_list = [l[0] for l in np.array(t).tolist()]
    print(time_list, len(time_list))
    # WPRの位置を取得
    l = wpr_location()
    station_list = np.array(l.index).tolist()
    print(station_list, len(station_list))
    #station_no = 47406 # 留萌
    station_no = 47656 # 静岡

    # WprStation Classの初期化
    wpr = WprStation(station_no=station_no)
    # AmedasStation.retrieveメソッドを使い、WPRデータを取得
    u, v, w, z, zmax = wpr.retrieve(time_list, opt_retrieve=opt_retrieve)
    #print(z)
    # csvファイルとして保存

    # 高度・時刻データ書き出し
    Series(z).to_csv('height.csv', header=None)
    Series(np.array(time_list)).to_csv('time.csv', header=None)

    # 時間ー高度面のデータ作成
    u = pd.DataFrame(u[:, 0:zmax], index=np.array(time_list), columns=z[0:zmax])
    v = pd.DataFrame(v[:, 0:zmax], index=np.array(time_list), columns=z[0:zmax])
    w = pd.DataFrame(w[:, 0:zmax], index=np.array(time_list), columns=z[0:zmax])
    #
    # 時間ー高度面のデータ書き出し
    u.to_csv('u_' + str(station_no) + ".csv")
    v.to_csv('v_' + str(station_no) + ".csv")
    w.to_csv('w_' + str(station_no) + ".csv")

