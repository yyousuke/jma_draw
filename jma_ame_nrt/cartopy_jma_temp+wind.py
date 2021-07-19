#!/usr/bin/env python3
from pandas import Series, DataFrame
import pandas as pd
import numpy as np
import math
import json
import os
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from jmaloc import MapRegion
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import cartopy.io.shapereader as shapereader
import itertools
from utils import common

# 出力ディレクトリ名
output_dir = "./map"

# 地域の選択
#area = "Japan"
area = "Tokyo_b"
#area = "Tokyo"

# 矢羽を描くかどうか
opt_barbs = False
#opt_barbs = True


# dir_name: 作成するディレクトリ名
def os_mkdir(dir_name):
    if not os.path.isdir(output_dir):
        if os.path.isfile(output_dir):
            os.remove(output_dir)
        print("mkdir " + output_dir)
        os.mkdir(output_dir)


class temp2col():
    def __init__(self, tmin=0., tmax=20., tstep=2, cmap='jet'):
        self.tmin = tmin
        self.tmax = tmax
        self.tstep = tstep
        self.cmap = cmap
        self.cm = plt.get_cmap(self.cmap)

    def conv(self, temp):
        n = (temp - self.tmin) / (self.tmax - self.tmin) * self.cm.N
        n = max(min(n, self.cm.N), 0)
        return self.cm(int(n))

    def colorbar(self, fig=None, anchor=(0.35, 0.24), size=(0.3, 0.02)):
        if fig is None:
            raise Exception('fig is needed')
        ax = fig.add_axes(anchor + size)
        gradient = np.linspace(0, 1, self.cm.N)
        gradient_array = np.vstack((gradient, gradient))
        ticks = list()
        labels = list()
        ll = np.arange(self.tmin, self.tmax, self.tstep)
        for t in ll:
            ticks.append((t - self.tmin) / (self.tmax - self.tmin) * self.cm.N)
            labels.append("{f:.0f}".format(f=t))
        # カラーバーを描く
        ax.imshow(gradient_array, aspect='auto', cmap=self.cm)
        ax.yaxis.set_major_locator(mticker.NullLocator())
        ax.yaxis.set_minor_locator(mticker.NullLocator())
        ax.set_xticks(ticks)
        ax.set_xticklabels(labels)
        #ax.set_axis_off()


def str_rep(inp):
    return inp.replace("[", "").replace("]", "").replace(",", "").split()


def read_data(input_filename):
    out_lon = list()
    out_lat = list()
    out_temp = list()
    out_u = list()
    out_v = list()
    # データ取得部分
    df = pd.read_csv(input_filename)
    #print(df)
    lon_in = df.loc[:, "lon"]
    lat_in = df.loc[:, "lat"]
    temp_in = df.loc[:, "temp"]
    wd_in = df.loc[:, "windDirection"]
    ws_in = df.loc[:, "wind"]
    for lon, lat, temp, wd, ws in zip(lon_in, lat_in, temp_in, wd_in, ws_in):
        # 経度・緯度の計算
        lon = str_rep(lon)
        lat = str_rep(lat)
        lon = float(lon[0]) + float(lon[1]) / 60.0
        lat = float(lat[0]) + float(lat[1]) / 60.0
        #print(lon.strip(), lat.strip(), temp)
        try:
            # 気温の計算
            temp.isdecimal()
            new = str_rep(temp)
            if new[1] == "0":
                temp = float(new[0])
            else:
                temp = np.nan
            #print(temp)
            # 風向・風速の計算
            wd.isdecimal()
            ws.isdecimal()
            new_wd = str_rep(wd)
            new_ws = str_rep(ws)
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
            out_lon.append(lon)
            out_lat.append(lat)
            out_temp.append(temp)
            out_u.append(u)
            out_v.append(v)
        except:
            continue
            #print("Warn: ", temp)
        #print("len = ", len(out_lon))
        #if lon > 140.75 and int(lat) == 35:
        #    print(lon, lat, temp, ws, wd, u, v)
    return np.array(out_lon), np.array(out_lat), np.array(out_temp), np.array(
        out_u), np.array(out_v)


# ax: cartopyを呼び出した際のaxes
def add_pref(ax,
             linestyle='-',
             facecolor='none',
             edgecolor='k',
             linewidth=0.8):
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
         title=None,
         area=None):

    # プロット領域の作成
    fig = plt.figure(figsize=(18, 12))
    #fig = plt.figure(figsize=(9, 6))
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
    else:
        ms = 6  # マーカーサイズ
        length = 7  # 矢羽のサイズ
        lw = 1.5  # 矢羽の幅
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

    # 海岸線を描く
    if opt_mapcolor:
        # 陸・海・湖を塗り分けて描く
        ax.add_feature(cfeature.LAND)
        ax.add_feature(cfeature.OCEAN)
        ax.add_feature(cfeature.COASTLINE, linewidth=0.8)
        ax.add_feature(cfeature.LAKES)
    else:
        ax.coastlines(color='k', linewidth=0.8)
    #
    # 都道府県境を描く
    if opt_pref:
        add_pref(ax, linestyle='-', facecolor='none', linewidth=0.8)
    #
    # temp2colクラスの初期化（気温の範囲はtmin、tmaxで設定、tstepで刻み幅）
    t2c = temp2col(cmap='jet', tmin=16., tmax=36.)
    # マーカーをプロット
    for xc, yc, dc in zip(lons, lats, d):
        if math.isnan(dc):
            print("Warn ", dc)
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
                 color='k')

    # タイトル
    if title is not None:
        plt.title(title, size=24)
        #fig.suptitle(title, size=24)

    # カラーバーを付ける
    t2c.colorbar(fig)

    # ファイルへの書き出し
    plt.savefig(output_filename, dpi=300, bbox_inches='tight')
    plt.close()


# 時刻の形式
# tinfo = "2021/03/12 16:10:00JST"
# tinfof = "20210312161000"
def main(tinfo=None, tinfof=None, area="Japan", opt_barbs=False, output_dir='.'):
    if tinfof is not None:
        # 入力ファイル名
        input_filename = tinfof + ".csv"
        # 出力ファイル名
        if opt_barbs:
            output_filename = os.path.join(
                output_dir, area + "_temp+wind_" + tinfof + ".png")
        else:
            output_filename = os.path.join(output_dir,
                                           area + "_temp_" + tinfof + ".png")
        # データの取得
        lons, lats, temp, u, v = read_data(input_filename)
        print(lons.shape, lats.shape, temp.shape, u.shape, v.shape)
        draw(lons, lats, temp, u, v, output_filename, title=tinfo,
	area=area,
             opt_pref=True,
             opt_barbs=opt_barbs,
             opt_mapcolor=True)


if __name__ == '__main__':

    # 出力ディレクトリ作成
    os_mkdir(output_dir)

    # 開始・終了時刻
    #time_sta = datetime(2021, 7, 19, 6, 0, 0)
    #time_end = datetime(2021, 7, 19, 17, 30, 0)
    time_sta = datetime(2021, 7, 19, 17, 30, 0)
    time_end = datetime(2021, 7, 19, 17, 30, 0)
    time_step = timedelta(minutes=10)
    time = time_sta
    while True:
        if time <= time_end:
            tinfo = time.strftime("%Y/%m/%d %H:%M:%SJST")
            tinfof = time.strftime("%Y%m%d%H%M%S")
            print(tinfo)
            main(tinfo, tinfof, area=area, opt_barbs=opt_barbs, output_dir=output_dir)
        else:
            break
        time = time + time_step
