#!/usr/bin/env python3
from pandas import Series, DataFrame
import pandas as pd
import numpy as np
import os
import json
import urllib.request


# データ取得部分
class WprStation():
    """WPRデータを取得し、ndarrayに変換する

    Parameters:
    ----------
    station_no: int
        ５桁の地点番号
    ----------
    """
    def __init__(self, station_no=None):
        self.station_no = str(station_no)

    def retrieve(self, time_list=None, opt_retrieve=True):
        """WPRデータをダウンロードする
        Parameters:
        ----------
        time_list: list(str, str, ...)
            WPRデータ時刻のリスト
        opt_retrieve: bool
            データ取得を行うかどうか
        ----------
        Returns:
        ----------
        u, v, w, z: ndarray
            東西風、南北風、鉛直速度、高度
        zmax: int
            高度データが入力された最大値
        ----------
        """
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
            try:
                df = DataFrame(d[tinfo])
                u_i, v_i, w_i, z_i = self._divide(df)
                u_o[0:u_i.shape[0]] = u_i
                v_o[0:v_i.shape[0]] = v_i
                w_o[0:w_i.shape[0]] = w_i
            except Exception:
                z_i = []
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
        """データを取り出す"""
        u = df.loc[:, 'u']
        v = df.loc[:, 'v']
        w = df.loc[:, 'w']
        z = df.loc[:, 'height']
        return u, v, w, z


def wpr_time(opt_retrive=True):
    """WPR時刻情報を取得し保存する

    Parameters:
    ----------
    opt_retrive: bool
        データが存在する場合にも取得する
    ----------
    """
    url_top = "https://www.jma.go.jp/bosai/windprofiler/data/"
    file_name = "times.json"
    if opt_retrieve and os.path.exists(file_name):
        os.remove(file_name)
    # WPR時刻情報の取得
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
    """WPR地点情報を取得しデータを返却する

    Returns:
    ----------
    df: pandas.DataFrame
        取り出したデータ
    ----------
    """
    url_top = "https://www.jma.go.jp/bosai/windprofiler/const/"
    file_name = "station.json"
    # WPR地点情報の取得
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
    # opt_retrieve = False
    # WPRデータの時刻を取得
    t = wpr_time(opt_retrive=True)
    time_list = [tl[0] for tl in np.array(t).tolist()]
    print(time_list, len(time_list))
    # WPRの位置を取得
    sl = wpr_location()
    station_list = np.array(sl.index).tolist()
    print(station_list, len(station_list))
    # station_no = 47626 # 熊谷
    # station_no = 47656 # 静岡
    station_no = 47636  # 名古屋

    # WprStation Classの初期化
    wpr = WprStation(station_no=station_no)
    # AmedasStation.retrieveメソッドを使い、WPRデータを取得
    u, v, w, z, zmax = wpr.retrieve(time_list, opt_retrieve=opt_retrieve)
    # csvファイルとして保存

    # 高度・時刻データ書き出し
    Series(z).to_csv('height.csv', header=None)
    Series(np.array(time_list)).to_csv('time.csv', header=None)

    # 時間ー高度面のデータ作成
    u = pd.DataFrame(u[:, 0:zmax],
                     index=np.array(time_list),
                     columns=z[0:zmax])
    v = pd.DataFrame(v[:, 0:zmax],
                     index=np.array(time_list),
                     columns=z[0:zmax])
    w = pd.DataFrame(w[:, 0:zmax],
                     index=np.array(time_list),
                     columns=z[0:zmax])
    #
    # 時間ー高度面のデータ書き出し
    u.to_csv('u_' + str(station_no) + ".csv")
    v.to_csv('v_' + str(station_no) + ".csv")
    w.to_csv('w_' + str(station_no) + ".csv")
