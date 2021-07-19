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
from matplotlib.colors import ListedColormap
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import cartopy.io.shapereader as shapereader
import itertools
from utils import ColUtils
from utils import common

# 出力ディレクトリ名
output_dir = "./map"

#area = "Japan"
#area = "Tokyo"
#area = "Tokai"
#area = "Shizuoka_a"
area = "Tyugoku"
#area = "Kagoshima"


# dir_name: 作成するディレクトリ名
def os_mkdir(dir_name):
    if not os.path.isdir(output_dir):
        if os.path.isfile(output_dir):
            os.remove(output_dir)
        print("mkdir " + output_dir)
        os.mkdir(output_dir)


# clevs: levels of boundary
# ccols: colors between the boundaries (len(clevs) must be len(ccols)+1)
class collevs():
    def __init__(self, clevs=[], ccols=[]):
        self.clevs_min = clevs[0]
        self.clevs = clevs
        self.ccols = ccols
        if len(clevs) != len(ccols) + 1:
            print(len(clevs), len(ccols))
            raise Exception('len(clevs) must be len(ccols)+1')

    def conv(self, val):
        if val < float(self.clevs[0]):
            col = 'gray'
            #col = self.ccols[0]
        for n in np.arange(len(self.ccols)):
            if val >= float(self.clevs[n]) and val < float(self.clevs[n + 1]):
                col = self.ccols[n]
        return col

    def colorbar(self,
                 fig=None,
                 anchor=(0.35, 0.24),
                 size=(0.3, 0.02),
                 fontsize=11):
        if fig is None:
            raise Exception('fig is needed')
        ax = fig.add_axes(anchor + size)
        gradient = np.linspace(0, 1, len(self.clevs) - 1)
        gradient_array = np.vstack((gradient, gradient))
        ticks = list()
        labels = list()
        ll = self.clevs[:-1]
        for n, t in enumerate(ll):
            ticks.append(n - 0.5)
            if t >= 1.:
                labels.append("{f:.0f}".format(f=t))
            else:
                labels.append("{f:.1f}".format(f=t))
        # カラーバーを描く
        cmap = ListedColormap(self.ccols)
        ax.imshow(gradient_array, aspect='auto', cmap=cmap)
        ax.yaxis.set_major_locator(mticker.NullLocator())
        ax.yaxis.set_minor_locator(mticker.NullLocator())
        ax.set_xticks(ticks)
        ax.set_xticklabels(labels, fontsize=fontsize)
        #ax.set_axis_off()


class temp2col():
    def __init__(self, tmin=0., tmax=20., tstep=2, cmap='jet'):
        self.tmin = tmin
        self.tmax = tmax
        self.tstep = tstep
        self.cmap = cmap
        try:
            self.cm = plt.get_cmap(self.cmap)
        except:
            cutils = ColUtils(cmap)  # 色テーブルの選択
            self.cm = cutils.get_ctable()  # 色テーブルの取得

    def conv(self, temp):
        n = (temp - self.tmin) / (self.tmax - self.tmin) * self.cm.N
        n = max(min(n, self.cm.N), 0)
        return self.cm(int(n))

    def colorbar(self,
                 fig=None,
                 anchor=(0.35, 0.24),
                 size=(0.3, 0.02),
                 fontsize=11):
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
        ax.set_xticklabels(labels, fontsize=fontsize)
        #ax.set_axis_off()


def str_rep(inp):
    return inp.replace("[", "").replace("]", "").replace(",", "").split()


def read_data(input_filename):
    out_lon = list()
    out_lat = list()
    out_temp = list()
    out_u = list()
    out_v = list()
    out_prep = list()
    # データ取得部分
    df = pd.read_csv(input_filename)
    #print(df)
    lon_in = df.loc[:, "lon"]
    lat_in = df.loc[:, "lat"]
    temp_in = df.loc[:, "temp"]
    wd_in = df.loc[:, "windDirection"]
    ws_in = df.loc[:, "wind"]
    prep_in = df.loc[:, "precipitation3h"]
    for lon, lat, temp, wd, ws, prep in zip(lon_in, lat_in, temp_in, wd_in,
                                            ws_in, prep_in):
        # 経度・緯度の計算
        lon = str_rep(lon)
        lat = str_rep(lat)
        lon = float(lon[0]) + float(lon[1]) / 60.0
        lat = float(lat[0]) + float(lat[1]) / 60.0
        #print(lon.strip(), lat.strip(), temp)
        # データの保存
        out_lon.append(lon)
        out_lat.append(lat)
        try:
            # 気温の計算
            temp.isdecimal()
            new = str_rep(temp)
            if new[1] == "0":
                temp = float(new[0])
            else:
                temp = np.nan
            #print(temp)
            # データの保存
            out_temp.append(temp)
        except:
            out_temp.append(np.nan)
        #
        try:
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
            out_u.append(u)
            out_v.append(v)
        except:
            out_u.append(np.nan)
            out_v.append(np.nan)
        #
        try:
            # 降水量の計算
            prep.isdecimal()
            new = str_rep(prep)
            if new[1] == "0":
                prep = float(new[0])
            else:
                prep = np.nan
            out_prep.append(prep)
        except:
            out_prep.append(np.nan)
    return np.array(out_lon), np.array(out_lat), np.array(out_temp), np.array(
        out_u), np.array(out_v), np.array(out_prep)


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
         opt_markerlabel=False,
         opt_barbs=False,
         title=None,
         area=None):

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
        ax.add_feature(cfeature.LAND, color='darkseagreen')
        #ax.add_feature(cfeature.OCEAN)
        ax.add_feature(cfeature.OCEAN, color='powderblue')
        ax.add_feature(cfeature.COASTLINE, linewidth=0.8)
        ax.add_feature(cfeature.LAKES)
    else:
        ax.coastlines(resolution='10m', color='k', linewidth=0.8)
    #
    # 都道府県境を描く
    if opt_pref:
        add_pref(ax, linestyle='-', facecolor='none', linewidth=0.8)

    #
    #clevs = [0.5, 10., 20., 50., 100., 200., 300., 400., 2000.]
    clevs = [0.5, 10., 20., 50., 80., 100., 120., 150., 2000.]
    ccols = [
        "lavender", "paleturquoise", "dodgerblue", "b", "gold", "darkorange",
        "r", "firebrick"
    ]
    # collevsクラスの初期化（降水量の範囲をclevs、色をccolsで与える）
    t2c = collevs(clevs=clevs, ccols=ccols)
    #
    # マーカーとテキストをプロット
    for xc, yc, dc in zip(lons, lats, d):
        if math.isnan(dc):
            print("Warn ", xc, yc, dc)
        else:
            c = t2c.conv(dc)
            ax.plot(xc, yc, marker='o', color=c, markersize=ms)
            if opt_markerlabel:
                if xc >= lon_min and xc <= lon_max and yc >= lat_min and yc <= lat_max:
                    ax.text(xc + 0.03, yc - 0.02, str(dc), color=c, fontsize=8)

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
    t2c.colorbar(fig, anchor=(0.30, 0.25), size=(0.35, 0.02))

    # ファイルへの書き出し
    plt.savefig(output_filename, dpi=300, bbox_inches='tight')
    plt.close()


# 時刻の形式
# tinfo = "2021/03/12 16:10:00JST"
# tinfof = "20210312161000"
def main(tinfo=None, tinfof=None, area="Japan", output_dir='.'):
    if tinfof is not None:
        # 入力ファイル名
        input_filename = tinfof + ".csv"
        # 出力ファイル名
        output_filename = os.path.join(output_dir,
                                       area + "_rain3h_" + tinfof + ".png")
        # データの取得
        lons, lats, temp, u, v, prep = read_data(input_filename)
        print(lons.shape, lats.shape, temp.shape, u.shape, v.shape, prep.shape)
        #
        # 作図
        draw(lons,
             lats,
             prep,
             u,
             v,
             output_filename,
             title=tinfo,
             area=area,
             opt_pref=True,
             opt_markerlabel=True,
             opt_mapcolor=True)


if __name__ == '__main__':

    # 出力ディレクトリ作成
    os_mkdir(output_dir)

    # 開始・終了時刻
    #time_sta = datetime(2021, 6, 30, 0, 0, 0)
    #time_sta = datetime(2021, 7, 5, 15, 0, 0)
    #time_sta = datetime(2021, 7, 7, 15, 0, 0)
    time_sta = datetime(2021, 7, 7, 15, 0, 0)
    time_end = datetime(2021, 7, 12, 12, 0, 0)
    time_step = timedelta(hours=1)
    #time_step = timedelta(hours=3)
    #time_step = timedelta(minutes=10)
    time = time_sta
    while True:
        if time <= time_end:
            tinfo = time.strftime("%Y/%m/%d %H:%M:%SJST")
            tinfof = time.strftime("%Y%m%d%H%M%S")
            print(tinfo)
            main(tinfo, tinfof, area=area, output_dir=output_dir)
        else:
            break
        time = time + time_step
