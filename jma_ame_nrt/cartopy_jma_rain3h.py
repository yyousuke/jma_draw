#!/usr/bin/env python3
import pandas as pd
import numpy as np
import math
import os
import sys
from datetime import timedelta
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from jmaloc import MapRegion
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import cartopy.io.shapereader as shapereader
from utils import collevs
from utils import os_mkdir
from utils import parse_command
from utils import common
common


def str_rep(inp):
    """データの文字列を処理し数値リストを返す"""
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
    out_prep = list()
    # データ取得部分
    df = pd.read_csv(input_filename)
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
        # print(lon.strip(), lat.strip(), temp)
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
            # データの保存
            out_temp.append(temp)
        except AttributeError:
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
        except AttributeError:
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
        except AttributeError:
            out_prep.append(np.nan)
    return np.array(out_lon), np.array(out_lat), np.array(out_temp), np.array(
        out_u), np.array(out_v), np.array(out_prep)


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
    """cartopyを用いて作図を行う

    Parameters:
    ----------
    lons: ndarray
        経度データ
    lats: ndarray
        緯度データ
    d: ndarray
        降水量データ
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
    opt_markerlabel: bool
        マーカーの隣に降水量を表示するかどうか
    opt_barbs: bool
        矢羽を描くかどうか
    title: str
        図のタイトル（Noneなら描かない）
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
        length = 7  # 矢羽のサイズ
        lw = 1.5  # 矢羽の幅
    #
    # cartopy呼び出し
    ax = fig.add_axes((0.1, 0.3, 0.8, 0.6), projection=ccrs.PlateCarree())
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
        ax.add_feature(cfeature.OCEAN)
        # ax.add_feature(cfeature.OCEAN, color='powderblue')
        ax.add_feature(cfeature.COASTLINE)
        # ax.add_feature(cfeature.COASTLINE, linewidth=0.8)
        ax.add_feature(cfeature.LAKES)
    else:
        ax.coastlines(resolution='10m', color='k', linewidth=0.8)
    #
    # 都道府県境を描く
    if opt_pref:
        add_pref(ax, linestyle='-', facecolor='none', linewidth=0.8)

    #
    # clevs = [0.5, 10., 20., 50., 100., 200., 300., 400., 2000.]
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
        # fig.suptitle(title, size=24)

    # カラーバーを付ける
    t2c.colorbar(fig, anchor=(0.30, 0.25), size=(0.35, 0.02))

    # ファイルへの書き出し
    plt.savefig(output_filename, dpi=300, bbox_inches='tight')
    plt.close()


def main(tinfo=None,
         tinfof=None,
         area="Japan",
         opt_markerlabel=True,
         output_dir='.'):
    """指定された時刻で作図

    Parameters:
    ----------
    tinfo: str
        図のタイトルに表示する時刻
        (形式：2021/03/12 16:10:00JST)
    tinfof: str
        ファイル名の一部に用いる時刻
        (形式：20210312161000)
    opt_markerlabel: bool
        地点のプロットの横に降水量を表示するかどうか
    area: str
        図を描く領域
    output_dir: str
        出力ディレクトリ
    ----------
    """
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
             opt_markerlabel=opt_markerlabel,
             opt_mapcolor=True)


if __name__ == '__main__':
    # オプションの読み込み
    args = parse_command(sys.argv, opt_lab=True)
    # 開始・終了時刻
    time_sta = pd.to_datetime(args.time_sta)
    time_end = pd.to_datetime(args.time_end)
    # 作図する領域
    area = args.sta
    # 出力ディレクトリ名
    output_dir = args.output_dir
    # 降水量を数字で表示するかどうか
    opt_markerlabel = args.mlabel
    # 出力ディレクトリ作成
    os_mkdir(output_dir)

    # データの時間間隔
    time_step = timedelta(hours=1)
    # time_step = timedelta(hours=3)
    # time_step = timedelta(minutes=10)
    time = time_sta
    while True:
        if time <= time_end:
            tinfo = time.strftime("%Y/%m/%d %H:%M:%SJST")
            tinfof = time.strftime("%Y%m%d%H%M%S")
            print(tinfo)
            main(tinfo,
                 tinfof,
                 area=area,
                 opt_markerlabel=opt_markerlabel,
                 output_dir=output_dir)
        else:
            break
        time = time + time_step
