#!/usr/bin/env python3
from pandas import DataFrame
import pandas as pd
import numpy as np
import math
import os
import sys
import json
import urllib.request
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from jmaloc import MapRegion
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import cartopy.io.shapereader as shapereader
import itertools
from utils import val2col
from utils import os_mkdir
from utils import parse_command
from utils import common

# 矢羽を描く値（短矢羽：1m/s、長矢羽：5m/s、旗矢羽：10m/s）
half = 1.
full = 2.
flag = 10.
barb_increments = dict(half=half, full=full, flag=flag)


# データ取得部分
class AmedasStation():
    """AMeDASデータを取得し、ndarrayに変換する

    Parameters:
    ----------
    latest: str
        取得する時刻（形式：20210819120000）
    output_dir_path: str
        出力ディレクトリのパス
    ----------
    """
    def __init__(self, latest=None, outdir_path="."):
        url = "https://www.jma.go.jp/bosai/amedas/data/latest_time.txt"
        if latest is None:
            latest = np.loadtxt(urllib.request.urlopen(url), dtype="str")
        print(latest)
        self.latest_time = pd.to_datetime(latest).strftime("%Y%m%d%H%M%S")
        self.datetime = pd.to_datetime(latest)
        print(self.latest_time)
        self.outdir_path = outdir_path

    def retrieve(self, cnt=2):  # cntは再取得カウント
        """AMeDASデータをダウンロードする"""
        outdir_path = self.outdir_path
        if cnt <= 0:  # 0の場合は終了
            raise RuntimeError('maximum count')
        url_top = "https://www.jma.go.jp/bosai/amedas/data/map/"
        file_name = self.latest_time + ".json"
        # 既に取得している場合は取得しない
        if not os.path.exists(os.path.join(outdir_path, file_name)):
            # アメダスデータの取得
            try:
                url = url_top + file_name
                print(url)
                urllib.request.urlretrieve(
                    url, os.path.join(outdir_path, file_name))
            except:
                time.sleep(10.0)  # 10秒間待つ
                self.retrieve(cnt=cnt - 1)  # cntを減らして再帰
        #
        # 取得したファイルを開く
        try:
            with open(os.path.join(outdir_path, file_name), 'rt') as fin:
                data = fin.read()
        except:
            raise IOError("in " + os.path.join(outdir_path, file_name))
        df = DataFrame(json.loads(data)).T
        # アメダス地点情報の取得
        df_location = self.location()
        df["lon"] = df_location.loc[:, "lon"]
        df["lat"] = df_location.loc[:, "lat"]
        df["kjName"] = df_location.loc[:, "kjName"]
        df["knName"] = df_location.loc[:, "knName"]
        df["enName"] = df_location.loc[:, "enName"]
        #print(df)
        # csvファイルとして保存
        df.to_csv(os.path.join(outdir_path, self.latest_time + ".csv"))
        # DataFrameとして保持
        self.df = df

    def location(self):
        """AMeDAS地点の位置情報を取得する"""
        outdir_path = self.outdir_path
        url_top = "https://www.jma.go.jp/bosai/amedas/const/"
        file_name = "amedastable.json"
        # アメダス地点情報の取得
        url = url_top + file_name
        if not os.path.exists(os.path.join(outdir_path, file_name)):
            print(url)
            urllib.request.urlretrieve(url,
                                       os.path.join(outdir_path, file_name))
        # 取得したファイルを開く
        try:
            with open(os.path.join(outdir_path, file_name), 'rt') as fin:
                data = fin.read()
        except:
            raise IOError("in " + os.path.join(outdir_path, file_name))
        df = DataFrame(json.loads(data))
        #print(df)
        # 取り出したデータを返却
        return df.T

    def str_rep(self, inp):
        """データの文字列を処理する"""
        return inp.replace("[", "").replace("]", "").replace(",", "").split()

    def read_data(self, input_filename=None, rainstep="1h"):
        """AMeDASデータをndarrayに変換する
    
        Parameters:
        ----------
        input_filename: str
            入力ファイル名（Noneの場合はretrieveで保存したcsvファイル使用）
        rain_step: str
            降水量データの間隔（デフォルトは1時間降水量）
        ----------
	Returns 
        ----------
        lon, lat, temp, u, v, prep: ndarray
            経度、緯度、気温、東西風、南北風、降水量データ
        ----------
        """
        out_lon = list()
        out_lat = list()
        out_temp = list()
        out_u = list()
        out_v = list()
        out_prep = list()
        # データ取得部分
        if input_filename is not None:
            df = pd.read_csv(input_filename)
        else:
            df = pd.read_csv(os.path.join(self.outdir_path, self.latest_time + ".csv"))
            #df = self.df
        # 変数に分ける
        lon_in = df.loc[:, "lon"]
        lat_in = df.loc[:, "lat"]
        temp_in = df.loc[:, "temp"]
        wd_in = df.loc[:, "windDirection"]
        ws_in = df.loc[:, "wind"]
        prep_in = df.loc[:, "precipitation" + rainstep]
        for lon, lat, temp, wd, ws, prep in zip(lon_in, lat_in, temp_in, wd_in,
                                                ws_in, prep_in):
            # 経度・緯度の計算
            lon = self.str_rep(lon)
            lat = self.str_rep(lat)
            lon = float(lon[0]) + float(lon[1]) / 60.0
            lat = float(lat[0]) + float(lat[1]) / 60.0
            # データの保存
            out_lon.append(lon)
            out_lat.append(lat)
            try:
                # 気温の計算
                temp.isdecimal()
                new = self.str_rep(temp)
                if new[1] == "0":
                    temp = float(new[0])
                else:
                    temp = np.nan
                # データの保存
                out_temp.append(temp)
            except:
                out_temp.append(np.nan)
            #
            try:
                # 風向・風速の計算
                wd.isdecimal()
                ws.isdecimal()
                new_wd = self.str_rep(wd)
                new_ws = self.str_rep(ws)
                if new_wd[1] == "0" and new_ws[1] == "0":
                    wd = float(new_wd[0]) * 22.5
                    ws = float(new_ws[0])
                else:
                    wd = np.nan
                    ws = np.nan
                # 東西風、南北風への変換
                u = ws * np.cos((270.0 - wd) / 180.0 * np.pi)
                v = ws * np.sin((270.0 - wd) / 180.0 * np.pi)
                # データの保存
                out_u.append(u)
                out_v.append(v)
            except:
                out_u.append(np.nan)
                out_v.append(np.nan)
            try:
                # 降水量の計算
                prep.isdecimal()
                new = self.str_rep(prep)
                if new[1] == "0":
                    prep = float(new[0])
                else:
                    prep = np.nan
                out_prep.append(prep)
            except:
                out_prep.append(np.nan)
        return np.array(out_lon), np.array(out_lat), np.array(
            out_temp), np.array(out_u), np.array(out_v), np.array(out_prep)


def add_pref(ax,
             linestyle='-',
             facecolor='none',
             edgecolor='k',
             linewidth=0.8):
    """都道府県境を描く

    Parameters:
    ----------
    ax: matplotlib Axes
        cartopyを呼び出した際のaxes
    facecolor: str
        塗り潰す色
    edgecolor: str
        線の色
    linewidth: str
        線の幅
    ----------
    """
    # 10mの解像度のデータ
    shpfilename = shapereader.natural_earth(resolution='10m',
                                            category='cultural',
                                            name='admin_1_states_provinces')
    #
    # 都道府県のみ取得
    provinces = shapereader.Reader(shpfilename).records()
    provinces_of_japan = filter(
        lambda province: province.attributes['admin'] == 'Japan', provinces)
    #
    # 都道府県境の追加
    for province in provinces_of_japan:
        #print(province.attributes['name'])
        geometry = province.geometry
        ax.add_geometries([geometry],
                          ccrs.PlateCarree(),
                          facecolor=facecolor,
                          edgecolor=edgecolor,
                          linewidth=linewidth,
                          linestyle=linestyle)


def draw(lons,
         lats,
         d,
         u,
         v,
         output_filename="test.png",
         opt_mapcolor=False,
         opt_pref=False,
         opt_barbs=False,
         barb_increments=dict(half=5., full=10., flag=50.),
         title=None,
         tmin=None,
         tmax=None,
         tstep=None,
         area=None):
    """cartopyを用いて作図を行う

    Parameters:
    ----------
    lons: ndarray
        経度データ
    lats: ndarray
        緯度データ
    d: ndarray
        気温データ
    u: ndarray
        東西風データ
    v: ndarray
        南北風データ
    output_filename: str
        出力ファイル名
    opt_mapcolor: bool
        True: 陸・海・湖を塗り分けて描く
        False: 海岸線を描く
    opt_pref: bool
        都道府県境を描くかどうか
    opt_barbs: bool
        矢羽を描くかどうか
    barb_increment: dict
        矢羽のプロパティ
        float half
            短矢羽
        float full
            長矢羽
        float flag
            旗矢羽
    title: str
        図のタイトル
    tmin: float or int
        カラーマップの下限
    tmax: float or int
        カラーマップの上限
    tstep: float or int
        カラーマップのラベルを描く間隔
    area: str
        図を描く領域
    ----------
    """
    # プロット領域の作成
    fig = plt.figure(figsize=(18, 12))
    #
    # MapRegion Classの初期化
    region = MapRegion(area)
    # Map.regionの変数を取得
    lon_step = region.lon_step  # 経度線を描く間隔
    lon_min = region.lon_min  # 経度範囲下限
    lon_max = region.lon_max  # 経度範囲上限
    lat_step = region.lat_step  # 緯度線を描く間隔
    lat_min = region.lat_min  # 緯度範囲下限
    lat_max = region.lat_max  # 緯度範囲上限
    if area == "Japan":
        ms = 1  # マーカーサイズ
        length = 4  # 矢羽のサイズ
        lw = 0.6  # 矢羽の幅
        xloc = -0.2  # 矢羽の凡例を表示する位置(x)
        yloc = 0.4  # 矢羽の凡例を表示する位置(x)
    else:
        ms = 6  # マーカーサイズ
        length = 6  # 矢羽のサイズ
        #length = 7  # 矢羽のサイズ
        lw = 1.5  # 矢羽の幅
        xloc = -0.2  # 矢羽の凡例を表示する位置(x)
        yloc = 0.2  # 矢羽の凡例を表示する位置(x)
    #
    # cartopy呼び出し
    ax = fig.add_axes((0.1, 0.3, 0.8, 0.6), projection=ccrs.PlateCarree())
    #ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())
    ax.set_extent([lon_min, lon_max, lat_min, lat_max])  # 領域の限定

    # 経度、緯度線を描く
    xticks = np.arange(-180, 180, lon_step)
    yticks = np.arange(-90, 90, lat_step)
    gl = ax.gridlines(crs=ccrs.PlateCarree(),
                      draw_labels=True,
                      linewidth=1,
                      linestyle=':',
                      color='k',
                      alpha=0.8)
    gl.xlocator = mticker.FixedLocator(xticks)  # 経度線
    gl.ylocator = mticker.FixedLocator(yticks)  # 緯度線
    gl.top_labels = False  # 上側の目盛り線ラベルを描かない
    gl.right_labels = False  # 下側の目盛り線ラベルを描かない

    if opt_mapcolor:
        # 陸・海・湖を塗り分けて描く
        ax.add_feature(cfeature.LAND)
        ax.add_feature(cfeature.OCEAN)
        ax.add_feature(cfeature.COASTLINE, linewidth=0.8)
        ax.add_feature(cfeature.LAKES)
    else:
        # 海岸線を描く
        ax.coastlines(color='k', linewidth=0.8)
    #
    # 都道府県境を描く
    if opt_pref:
        add_pref(ax, linestyle='-', facecolor='none', linewidth=0.8)
    #
    # val2colクラスの初期化（気温の範囲はtmin、tmaxで設定、tstepで刻み幅）
    t2c = val2col(cmap='jet', tmin=tmin, tmax=tmax, tstep=tstep)
    # マーカーをプロット
    for xc, yc, dc in zip(lons, lats, d):
        if math.isnan(dc):
            print("Warn ", xc, yc, dc)
        else:
            c = t2c.conv(dc)
            ax.plot(xc, yc, marker='o', color=c, markersize=ms)

    # 矢羽を描く
    if opt_barbs:
        ax.barbs(lons,
                 lats,
                 u,
                 v,
                 sizes=dict(emptybarb=0.0),
                 length=length,
                 linewidth=lw,
                 barb_increments=barb_increments,
                 color='k')
        # 矢羽の値をプロット
        f1 = barb_increments['half']
        f2 = barb_increments['full']
        f3 = barb_increments['flag']
        name = f'half: {f1:.0f}m/s, full: {f2:.0f}m/s, flag: {f3:.0f}m/s'
        print(name)
        ax.text(lon_max + xloc, lat_min + yloc, name, ha='right', va='center')

    # タイトル
    if title is not None:
        plt.title(title, size=24)
        #fig.suptitle(title, size=24)

    # カラーバーを付ける
    t2c.colorbar(fig)

    # ファイルへの書き出し
    plt.savefig(output_filename, dpi=300, bbox_inches='tight')
    plt.close()


if __name__ == '__main__':
    # オプションの読み込み
    args = parse_command(sys.argv,
                         opt_time=False,
                         opt_wind=True,
                         opt_trange=True)
    # 作図する領域
    area = args.sta
    # 出力ディレクトリ名
    output_dir = args.output_dir
    # 矢羽を描くかどうか
    opt_barbs = args.addwind
    # 気温を描く範囲
    try:
        tr = args.temprange.split(',')
        tmin = float(tr[0])
        tmax = float(tr[1])
        try:
            tstep = float(tr[2])
        except IndexError:
            tstep = int((tmax - tmin) / 10.)
    except:
        raise ValueError("invalid temprange values")

    # AmedasStation Classの初期化
    amedas = AmedasStation()
    time = amedas.datetime
    # AmedasStation.retrieveメソッドを使い、アメダスデータを取得
    amedas.retrieve()
    # ndarrayデータを取り出す
    lons, lats, temp, u, v, rain = amedas.read_data()
    print(lons.shape, lats.shape, temp.shape, u.shape, v.shape, rain.shape)
    #
    # 時刻情報の設定
    tinfo = time.strftime("%Y/%m/%d %H:%M:%SJST")
    tinfof = time.strftime("%Y%m%d%H%M%S")
    # 出力ディレクトリ作成
    os_mkdir(output_dir)

    # 入力ファイル名
    input_filename = tinfof + ".csv"
    # 出力ファイル名
    if opt_barbs:
        output_filename = os.path.join(output_dir,
                                       area + "_temp+wind_" + tinfof + ".png")
    else:
        output_filename = os.path.join(output_dir,
                                       area + "_temp_" + tinfof + ".png")
    #
    # 作図
    draw(lons,
         lats,
         temp,
         u,
         v,
         output_filename,
         opt_mapcolor=True,
         opt_pref=True,
         opt_barbs=opt_barbs,
         barb_increments=barb_increments,
         tmin=tmin,
         tmax=tmax,
         tstep=tstep,
         title=tinfo,
         area=area)
