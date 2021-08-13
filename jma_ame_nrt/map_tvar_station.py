#!/usr/bin/env python3
import pandas as pd
import numpy as np
import math
import os
import sys
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as mticker
from matplotlib.colors import ListedColormap
from utils import os_mkdir
from utils import parse_command
from utils import common

plt.rcParams['xtick.direction'] = 'in'  # x軸目盛線を内側
plt.rcParams['xtick.major.width'] = 1.2  # x軸主目盛線の長さ
plt.rcParams['ytick.direction'] = 'in'  # y軸目盛線を内側
plt.rcParams['ytick.major.width'] = 1.2  # y軸主目盛線の長さ


def str_rep(inp):
    return inp.replace("[", "").replace("]", "").replace(",", "").split()


def read_data(input_filename, sta=None):
    """AMeDAS csvデータを読み込む

    Parameters:
    ----------
    input_filename: str
        入力ファイル名
    sta: str
        アメダス地点名
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
    # 地点データ選択
    df = df[df.loc[:, 'enName'] == sta]
    #print(df)
    lon_in = df.loc[:, "lon"]
    lat_in = df.loc[:, "lat"]
    try:
        temp_in = df.loc[:, "temp"]
    except:
        temp_in = [np.nan]
    try:
        wd_in = df.loc[:, "windDirection"]
        ws_in = df.loc[:, "wind"]
    except:
        wd_in = [np.nan]
        ws_in = [np.nan]
    try:
        prep_in = df.loc[:, "precipitation1h"]
    except:
        prep_in = [np.nan]
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


def draw(index,
         temp,
         prep,
         u,
         v,
         output_filename="test.png",
         opt_barbs=False,
         opt_cumrain=False,
         title=None):
    """matplotlibを用いて作図を行う

    Parameters:
    ----------
    temp: ndarray
        気温データ
    prep: ndarray
        降水量データ
    u: ndarray
        東西風データ
    v: ndarray
        南北風データ
    output_filename: str
        出力ファイル名
    opt_barbs: bool
        矢羽を描くかどうか
    opt_cumrain: bool
        降水量を積算降水量にするかどうか
    title: str
        図のタイトル（Noneなら描かない）
    ----------
    """
    # プロット領域の作成
    fig = plt.figure(figsize=(18, 12))
    ax1 = fig.add_subplot(1, 1, 1)
    #
    # 降水量
    if opt_cumrain:
        ylab = 'Cumulative Precipitation (mm)'
        prep = np.cumsum(prep)
    else:
        ylab = 'Precipitation (mm)'
    ax1.set_ylim([0, math.ceil(prep.max() + math.fmod(prep.max(), 10)) + 1])
    ax1.bar(index,
            prep,
            color='b',
            width=0.03,
            alpha=0.4,
            label='Precipitation')
    ax1.set_ylabel(ylab, fontsize=20)
    #
    # 気温
    ax2 = ax1.twinx()  # 2つのプロットを関連付ける
    ax2.set_ylim([math.floor(temp.min() - 1), math.ceil(temp.max()) + 2])
    ax2.plot(index, temp, color='r', label='Temperature')
    ax2.set_ylabel('Temperature (K)', fontsize=20)

    # 矢羽を描く
    if opt_barbs:
        ax.barbs(index,
                 0.5,
                 u,
                 v,
                 sizes=dict(emptybarb=0.0),
                 length=4,
                 linewidth=1,
                 color='k')

    # y軸の目盛り
    ax1.yaxis.set_major_locator(mticker.AutoLocator())
    ax1.yaxis.set_minor_locator(mticker.AutoMinorLocator())
    ax2.yaxis.set_major_locator(mticker.AutoLocator())
    ax2.yaxis.set_minor_locator(mticker.AutoMinorLocator())
    # x軸の目盛り
    ax1.xaxis.set_major_locator(mticker.AutoLocator())
    ax1.xaxis.set_minor_locator(mticker.AutoMinorLocator())
    ax1.xaxis.set_major_locator(mticker.FixedLocator(
        ax1.get_xticks().tolist()))
    ax1.set_xticklabels(ax1.get_xticklabels(), rotation=70, size="small")
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d %HJST'))
    ax1.xaxis.set_minor_formatter(mticker.NullFormatter())

    # タイトル
    if title is not None:
        plt.title(title, fontsize=24)
        #fig.suptitle(title, fontsize=24)

    # ファイルへの書き出し
    plt.savefig(output_filename, dpi=300, bbox_inches='tight')
    plt.close()


def main(tinfo=None, tinfof=None, sta=None, output_dir='.'):
    """指定された時刻のデータを取得

    Parameters:
    ----------
    tinfo: str
        図のタイトルに表示する時刻
        (形式：2021/03/12 16:10:00JST)
    tinfof: str
        ファイル名の一部に用いる時刻
        (形式：20210312161000)
    area: str
        図を描く地点
    output_dir: str
        出力ディレクトリ
    ----------
    """
    if sta is None:
        raise Exception('sta is needed')
    if tinfof is not None:
        # 入力ファイル名
        input_filename = tinfof + ".csv"
        # データの取得
        lons, lats, temp, u, v, prep = read_data(input_filename, sta=sta)
        print(lons.shape, lats.shape, temp.shape, u.shape, v.shape, prep.shape)
        #
        return lons, lats, temp, u, v, prep
    else:
        return np.nan, np.nan, np.nan, np.nan, np.nan, np.nan


if __name__ == '__main__':
    # オプションの読み込み
    args = parse_command(sys.argv, opt_cum=True)
    # 開始・終了時刻
    time_sta = pd.to_datetime(args.time_sta)
    time_end = pd.to_datetime(args.time_end)
    # アメダス地点名
    sta = args.sta
    # 出力ディレクトリ名
    output_dir = args.output_dir
    # 降水量を積算降水量にするかどうか
    opt_cumrain = args.cumrain
    #opt_cumrain = False

    # 出力ディレクトリ作成
    os_mkdir(output_dir)

    # データの時間間隔
    time_step = timedelta(hours=1)
    #time_step = timedelta(minutes=10)
    index = []
    prep = []
    temp = []
    uwnd = []
    vwnd = []
    tinfot = time_sta.strftime("%Y/%m/%d %HJST") + "-" + time_end.strftime(
        "%Y/%m/%d %HJST")
    #
    time = time_sta
    while True:
        if time <= time_end:
            tinfo = time.strftime("%Y/%m/%d %H:%M:%SJST")
            tinfof = time.strftime("%Y%m%d%H%M%S")
            print(tinfo)
            # 指定した時刻の地点データ取得
            lons, lats, t_in, u_in, v_in, pr_in = main(tinfo,
                                                       tinfof,
                                                       sta=sta,
                                                       output_dir=output_dir)
            #
            index.append(time)
            prep.append(pr_in)
            temp.append(t_in)
            uwnd.append(u_in)
            vwnd.append(v_in)
        else:
            break
        time = time + time_step
    #
    nt = len(index)
    index = np.vstack(index).reshape(nt)
    prep = np.vstack(prep).reshape(nt)
    temp = np.vstack(temp).reshape(nt)
    uwnd = np.vstack(uwnd).reshape(nt)
    vwnd = np.vstack(vwnd).reshape(nt)
    print(index)
    print(prep)
    print(temp)
    print(uwnd)
    print(vwnd)
    print(index.shape, prep.shape, temp.shape, uwnd.shape, vwnd.shape)
    # 出力ファイル名
    output_filepath = os.path.join(output_dir, "tvar_" + sta + ".png")
    # 作図
    draw(index,
         temp,
         prep,
         uwnd,
         vwnd,
         output_filename=output_filepath,
         opt_cumrain=opt_cumrain,
         title=tinfot + " (" + sta + ")")
