#!/usr/bin/env python3
import pandas as pd
import numpy as np
import math
import os
import sys
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

# 出力ディレクトリ名
#output_dir = "./map"

# 地域の選択
#area = "Japan"
#area = "Tokyo_a"
#area = "Tokyo_b"
area = "Tokyo"
#area = "Sapporo"

# 気温の範囲
tmin = 18.
tmax = 38.
tstep = 2.
#
#tmin = 10.
#tmax = 40.
#tstep = 3.

# 矢羽を描くかどうか
#opt_barbs = False
#opt_barbs = True
#
# 矢羽を描く値
half = 1.
full = 2.
flag = 10.
barb_increments = dict(half=half, full=full, flag=flag)



def str_rep(inp):
    """データの文字列を処理する"""
    return inp.replace("[", "").replace("]", "").replace(",", "").split()


def read_data(input_filename):
    """AMeDAS csvデータを読み込む

    Parameters:
    ----------
    input_filename: str
        入力ファイル名
    ----------
    """
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
    return np.array(out_lon), np.array(out_lat), np.array(out_temp), np.array(
        out_u), np.array(out_v)


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
    tmin: float
        カラーマップの下限
    tmax: float
        カラーマップの上限
    tstep: float
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
    else:
        ms = 6  # マーカーサイズ
        length = 6  # 矢羽のサイズ
        #length = 7  # 矢羽のサイズ
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
        ax.text(lon_max - 0.2, lat_min + 0.2, name, ha='right', va='center')
        #ax.text(lon_max - 1.2, lat_min + 0.1, name, ha='center', va='center')

    # タイトル
    if title is not None:
        plt.title(title, size=24)
        #fig.suptitle(title, size=24)

    # カラーバーを付ける
    t2c.colorbar(fig)

    # ファイルへの書き出し
    plt.savefig(output_filename, dpi=300, bbox_inches='tight')
    plt.close()


def main(tinfo=None,
         tinfof=None,
         area="Japan",
         opt_barbs=False,
         barb_increments=dict(half=5., full=10., flag=50.),
         tmin=None,
         tmax=None,
         tstep=None,
         output_dir='.'):
    """指定された時刻のデータの作図

    Parameters:
    ----------
    tinfo: str
        図のタイトルに表示する時刻
        (形式：2021/03/12 16:10:00JST)
    tinfof: str
        ファイル名の一部に用いる時刻
        (形式：20210312161000)
    area: str
        図を描く領域
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
    tmin: float
        カラーマップの下限
    tmax: float
        カラーマップの上限
    tstep: float
        カラーマップのラベルを描く間隔
    output_dir: str
        出力ディレクトリ
    ----------
    """
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


if __name__ == '__main__':
    # オプションの読み込み
    args = parse_command(sys.argv, opt_wind=True)
    # 開始・終了時刻
    time_sta = pd.to_datetime(args.time_sta)
    time_end = pd.to_datetime(args.time_end)
    # 作図する領域
    area = args.sta
    # 出力ディレクトリ名
    output_dir = args.output_dir
    # 矢羽を描くかどうか
    opt_barbs = args.wind
    # 出力ディレクトリ作成
    os_mkdir(output_dir)

    # 開始・終了時刻
    #time_sta = datetime(2021, 8, 10, 0, 0, 0)
    #time_end = datetime(2021, 8, 10, 23, 50, 0)
    # データの時間間隔
    time_step = timedelta(minutes=10)
    time = time_sta
    while True:
        if time <= time_end:
            tinfo = time.strftime("%Y/%m/%d %H:%M:%SJST")
            tinfof = time.strftime("%Y%m%d%H%M%S")
            print(tinfo)
            main(tinfo,
                 tinfof,
                 area=area,
                 opt_barbs=opt_barbs,
                 barb_increments=barb_increments,
                 tmin=tmin,
                 tmax=tmax,
                 tstep=tstep,
                 output_dir=output_dir)
        else:
            break
        time = time + time_step
