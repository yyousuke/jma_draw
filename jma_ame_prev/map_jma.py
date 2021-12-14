#!/usr/bin/env python3
from pandas import Series, DataFrame
import pandas as pd
import numpy as np
from datetime import datetime, timedelta, timezone
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import math
from amesta import AmedasStation

plt.rcParams['xtick.direction'] = 'in'  # x軸目盛線を内側
plt.rcParams['xtick.major.width'] = 1.2  # x軸主目盛線の長さ
plt.rcParams['ytick.direction'] = 'in'  # y軸目盛線を内側
plt.rcParams['ytick.major.width'] = 1.2  # y軸主目盛線の長さ

# アメダス地点
#sta = "Sapporo"
sta = "Tokyo"
#sta = "Yokohama"
#sta = "Nagoya"
#sta = "Osaka"
#sta = "Fukuoka"
#
# 作図する日付
date = "yesterday"
#date = "20210123"

# 矢羽を描くかどうか
plt_barbs = True  # true: 矢羽を描く

#barbs_kt = False # true: kt, false: m/s
barbs_kt = True  # true: kt, false: m/s

# 積雪量データを描くかどうか
#opt_snow = False
opt_snow = True

# 時刻設定
JST = timezone(timedelta(hours=+9), 'JST')
date_JST = datetime.now(JST)
if date == "yesterday":
    tstr = date_JST - timedelta(days=1)
else:
    try:
        tstr = pd.to_datetime(date)
    except:
        raise Exception('Unknown input type')

# ファイル名などに表示する時刻
dstr = tstr.strftime("%Y/%m/%d")
fdate = tstr.strftime("%m%d")
yyyy = tstr.strftime("%Y")
mm = tstr.strftime("%m")
dd = tstr.strftime("%d")
# 整数値
year = tstr.year
mon = tstr.month
day = tstr.day


def plot(dataset):
    """地点データの作図を行う"""
    # データの取り出し
    try:
        #index = dataset.hour
        index = np.arange(len(dataset.hour)) + 1
        temp = dataset.temp
        prep = dataset.prep
        sun = dataset.sun
        if opt_snow:
            snowd = dataset.snowd
        RH = dataset.RH
        pres = dataset.ps
        ws = dataset.ws
        wd = dataset.wd
    except:
        raise Exception('Unknown index')
    #print(ws)
    #print(wd)
    u = ws * np.cos((270.0 - wd) / 180.0 * np.pi)
    v = ws * np.sin((270.0 - wd) / 180.0 * np.pi)

    # 作図
    # (0) プロットエリアの定義
    #fig, ax1 = plt.subplots()
    fig = plt.figure(figsize=(6, 6))
    ax1 = fig.add_subplot(3, 1, 1)
    # タイトルを付ける
    ax1.set_title(dstr + ' ' + sta)
    #plt.title(loc2, fontdict = {"fontproperties": fontprop})
    #
    # (1) 降水量と気温
    # (1-1) 降水量(mm)
    ax1.bar(index,
            prep,
            color='b',
            width=0.5,
            alpha=0.4,
            label='Precipitation')
    if max(prep) >= 40:
        ax1.set_ylim(
            [0, math.ceil(prep.max() - math.fmod(prep.max(), 10) + 50)])
    elif max(prep) >= 20:
        ax1.set_ylim([0, 50])
    elif max(prep) >= 10:
        ax1.set_ylim([0, 30])
    else:
        ax1.set_ylim([0, 10])
    ax1.set_ylabel('Precipitation (mm)')
    # 凡例
    ax1.legend(loc='upper left')
    #
    ax2 = ax1.twinx()  # 2つのプロットを関連付ける
    # (1-2) 気温（K）
    ax2.set_ylim([math.floor(temp.min() - 1), math.ceil(temp.max()) + 2])
    ax2.plot(index, temp, color='r', label='Temperature')
    ax2.set_ylabel('Temperature ($\mathrm{^{\circ}C}$)')
    # 凡例
    ax2.legend(loc='upper right')
    #plt.legend(loc='lower center')
    #
    #
    # (2) 日照時間（h）, 相対湿度(%)、風向・風速(矢羽)
    ax3 = fig.add_subplot(3, 1, 2)
    # (2-1) 日照時間（h）
    ax3.set_ylim([0, 1.0])
    ax3.bar(index, sun, color='r', width=0.5, alpha=0.4, label='Sun light')
    ax3.set_ylabel('Sun light (h)')
    # 凡例
    ax3.legend(loc='upper left')
    #
    ax4 = ax3.twinx()  # 2つのプロットを関連付ける
    # (2-2) 相対湿度（%）
    ax4.set_ylim([0, 100])
    ax4.plot(index, RH, color='b', label='RH')
    ax4.set_ylabel('RH (%)')
    # 凡例
    ax4.legend(loc='lower left')
    #
    # (2-3) 矢羽
    y = 50
    if plt_barbs:
        if barbs_kt:
            # kt
            ax4.barbs(index,
                      y,
                      u,
                      v,
                      color='k',
                      length=5,
                      sizes=dict(emptybarb=0.001),
                      barb_increments=dict(half=2.57222,
                                           full=5.14444,
                                           flag=25.7222))
        else:
            # m/s
            ax4.barbs(index,
                      y,
                      u,
                      v,
                      color='k',
                      length=5,
                      sizes=dict(emptybarb=0.001))
    #
    #
    # (3) 積雪深（cm）、地表気圧（hPa）
    # (3-1) 積雪深（cm）
    if opt_snow:
        ax5 = fig.add_subplot(3, 1, 3)
        ax5.bar(index,
                snowd,
                color='g',
                width=0.5,
                alpha=0.4,
                label='Snow depth')
        if max(snowd) >= 140:
            ax5.set_ylim(
                [0,
                 math.ceil(snowd.max() - math.fmod(snowd.max(), 10) + 50)])
        elif max(snowd) >= 40:
            ax5.set_ylim([0, 150])
        elif max(snowd) >= 15:
            ax5.set_ylim([0, 50])
        else:
            ax5.set_ylim([0, 20])
        ax5.set_ylabel('Snow depth  (cm)')
        # 凡例
        ax5.legend(loc='upper left')
        #
        ax6 = ax5.twinx()  # 2つのプロットを関連付ける
        # for pressure
        leg_loc = "upper center"
    else:
        # 気圧の作図用
        ax6 = fig.add_subplot(3, 1, 3)
        leg_loc = "best"
    #
    # (3-2) 地表気圧（hPa）
    ax6.set_ylim([
        math.floor(pres.min() - math.fmod(pres.min(), 5) - 5),
        math.ceil(pres.max() - math.fmod(pres.min(), 5)) + 5
    ])
    #ax6.set_ylim([math.floor(pres.min()-math.fmod(pres.min(),2)), math.ceil(pres.max())+1])
    ax6.plot(index, pres, color='k', label='Pressure')
    ax6.set_ylabel('pressure (hPa)')
    # 凡例
    ax6.legend(loc=leg_loc)
    #
    # (4) 全体の調整
    # y軸の目盛り線
    ax1.yaxis.set_major_locator(ticker.AutoLocator())
    ax1.yaxis.set_minor_locator(ticker.AutoMinorLocator())
    ax2.yaxis.set_major_locator(ticker.AutoLocator())
    ax2.yaxis.set_minor_locator(ticker.AutoMinorLocator())
    ax3.yaxis.set_major_locator(ticker.AutoLocator())
    ax3.yaxis.set_minor_locator(ticker.AutoMinorLocator())
    ax4.yaxis.set_major_locator(ticker.AutoLocator())
    ax4.yaxis.set_minor_locator(ticker.AutoMinorLocator())
    if opt_snow:
        ax5.yaxis.set_major_locator(ticker.AutoLocator())
        ax5.yaxis.set_minor_locator(ticker.AutoMinorLocator())
    ax6.yaxis.set_major_locator(ticker.AutoLocator())
    ax6.yaxis.set_minor_locator(ticker.AutoMinorLocator())
    # x軸の目盛り線
    ax1.xaxis.set_major_locator(ticker.MultipleLocator(3))
    ax1.xaxis.set_minor_locator(ticker.MultipleLocator(1))
    ax3.xaxis.set_major_locator(ticker.MultipleLocator(3))
    ax3.xaxis.set_minor_locator(ticker.MultipleLocator(1))
    ax6.xaxis.set_major_locator(ticker.MultipleLocator(3))
    ax6.xaxis.set_minor_locator(ticker.MultipleLocator(1))
    # x軸の目盛り線ラベル（一番下の大目盛線ラベルだけを残す）
    ax1.xaxis.set_major_formatter(ticker.NullFormatter())
    ax1.xaxis.set_minor_formatter(ticker.NullFormatter())
    ax3.xaxis.set_major_formatter(ticker.NullFormatter())
    ax3.xaxis.set_minor_formatter(ticker.NullFormatter())
    ax6.xaxis.set_minor_formatter(ticker.NullFormatter())
    #
    # プロット範囲の調整
    plt.subplots_adjust(top=None, bottom=0.15, wspace=0.25, hspace=0.15)
    #
    # (5) ファイルへの書き出し
    fig_fname = "figure_" + sta + "_" + fdate + ".pdf"
    plt.savefig(fig_fname)
    #
    plt.show()


#
if __name__ == '__main__':

    # AmedasStation Classの初期化
    amedas = AmedasStation(sta)

    # AmedasStation.retrieve_hourメソッドを使い、データを取得
    dataset = amedas.retrieve_hour(yyyy, mon, day)
    print(dataset)

    # 作図
    plot(dataset)
