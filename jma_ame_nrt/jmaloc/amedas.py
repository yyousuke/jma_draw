#
#  2021/06/13 Yamashita
#  アメダス地点の経度・緯度を返す
#
from pandas import DataFrame
import pandas as pd
import numpy as np
import os
import json
import urllib.request


# アメダス地点情報の取得
class AmedasStation():
    """アメダス地点情報の取得"""
    def __init__(self):
        """アメダス地点データの取得と地点情報への変換"""
        # データ読み込み
        df = self._location()
        # 数値化された経度、緯度情報に変換
        self.df = self._convert(df)

    def get_staloc(self, kn_name=None, kj_name=None, en_name=None):
        """アメダス地点の経度、緯度を返す
        Parameters:
        ----------
        kn_name: str
            カタカナの地点名
        kj_name: str
            漢字の地点名
        en_name: str
            英語の地点名
        ----------
        Returns:
        ----------
        float
            経度、緯度
        ----------
        """
        if kn_name is None and kj_name is None and en_name is None:
            raise Exception('either kn_name or kj_name or en_name is needed')
        if kn_name is not None:
            df_loc = self.df[self.df.loc[:, "knname"] == kn_name]
        if kj_name is not None:
            df_loc = self.df[self.df.loc[:, "kjname"] == kj_name]
        if en_name is not None:
            df_loc = self.df[self.df.loc[:, "enname"] == en_name]
        print(df_loc)
        longitude = df_loc.iloc[0, 4]
        latitude = df_loc.iloc[0, 5]
        return float(longitude), float(latitude)

    def _location(self):
        """AMeDAS地点の位置情報を取得し、pandas DataFrameで返却"""
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

    def _str_rep(self, inp):
        """データの文字列を処理し数値リストを返す"""
        inp = str(inp)
        return inp.replace("[", "").replace("]", "").replace(",", "").split()

    # 入力 df: DataFrame
    def _convert(self, df):
        """アメダス地点データ変換
        Parameters:
        ----------
        df: pandas DataFrame
            アメダス地点情報
        ----------
        Returns:
        ----------
        df: pandas DataFrame
            経度・緯度を数値に変換したアメダス地点情報
        ----------
        """
        lons = []
        lats = []
        alts = []
        staids = []
        nkjs = []
        nkns = []
        nens = []
        for lon, lat, alt, staid, nkj, nkn, nen in zip(
                df.loc[:, "lon"], df.loc[:, "lat"], df.loc[:, "alt"], df.index,
                df.loc[:, "kjName"], df.loc[:, "knName"], df.loc[:, "enName"]):
            # 経度・緯度の計算
            lon = self._str_rep(lon)
            lat = self._str_rep(lat)
            lon = float(lon[0]) + float(lon[1]) / 60.0
            lat = float(lat[0]) + float(lat[1]) / 60.0
            lons.append(lon)
            lats.append(lat)
            alts.append(float(alt))
            staids.append(staid)
            nkjs.append(nkj)
            nkns.append(nkn)
            nens.append(nen)
        # データ作成
        df = DataFrame(
            {
                'staid': np.array(staids),
                'kjname': np.array(nkjs),
                'knname': np.array(nkns),
                'enname': np.array(nens),
                'longitude': np.array(lons),
                'latitude': np.array(lats),
                'altitude': np.array(alts)
            },
            dtype='unicode')
        #print(df)
        df.to_csv("amedastable.csv")
        return df
