#!/usr/bin/env python3
from pandas import Series, DataFrame
import pandas as pd
import numpy as np
import math
import json
import urllib.request
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from mpl_toolkits.basemap import Basemap

#area = "Japan"
area = "Tokyo"


class temp2col():
    def __init__(self, tmin=0., tmax=20., tstep=2, cmap='jet'):
        self.tmin = tmin
        self.tmax = tmax
        self.tstep = tstep
        self.cmap = cmap

    def conv(self, temp):
        self.cm = plt.get_cmap(self.cmap)
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
        ax.yaxis.set_major_locator(ticker.NullLocator())
        ax.yaxis.set_minor_locator(ticker.NullLocator())
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


def draw(lons, lats, d, u, v, output_filename="test.png", title=None):

    # プロット領域の作成
    fig = plt.figure(figsize=(18, 12))
    #fig = plt.figure(figsize=(9, 6))
    ax = fig.add_axes((0.1, 0.3, 0.8, 0.6))

    # Basemap呼び出し
    if area == "Japan":
        ms = 1  # マーカーサイズ
        length = 4  # 矢羽のサイズ
        lw = 0.6  # 矢羽の幅
        # ランベルト正角円錐図法
        m = Basemap(projection='lcc',
                    resolution='i',
                    lat_0=35,
                    lon_0=135,
                    llcrnrlat=20,
                    urcrnrlat=50,
                    llcrnrlon=120,
                    urcrnrlon=150)
        # 緯度線を引く
        m.drawparallels(np.arange(-90, 90, 5),
                        color="gray",
                        fontsize='small',
                        labels=[True, False, False, False])

        # 経度線を引く
        m.drawmeridians(np.arange(0, 360, 5),
                        color="gray",
                        fontsize='small',
                        labels=[False, False, False, True])
    elif area == "Tokyo":
        ms = 6  # マーカーサイズ
        length = 7  # 矢羽のサイズ
        lw = 1.5  # 矢羽の幅
        # ランベルト正角円錐図法
        m = Basemap(projection='lcc',
                    resolution='f',
                    lat_0=35,
                    lon_0=140,
                    llcrnrlat=34.8,
                    urcrnrlat=36.8,
                    llcrnrlon=139.2,
                    urcrnrlon=141.2)
        # 緯度線を引く
        m.drawparallels(np.arange(-90, 90, 0.5),
                        color="gray",
                        fontsize='small',
                        labels=[True, False, False, False])

        # 経度線を引く
        m.drawmeridians(np.arange(0, 360, 0.5),
                        color="gray",
                        fontsize='small',
                        labels=[False, False, False, True])
    else:
        print('Unknown input type')
        quit()

    # 海岸線を描く
    m.drawcoastlines(color='k', linewidth=0.8)

    # 背景に色を付ける
    #m.drawmapboundary(fill_color='aqua')

    # 大陸に色を付ける
    #m.fillcontinents(color='w')

    #
    # 図法の座標へ変換
    x, y = m(lons, lats)
    # temp2colクラスの初期化（気温の範囲はtmin、tmaxで設定、tstepで刻み幅）
    t2c = temp2col(cmap='jet', tmin=4., tmax=24.)
    # マーカーをプロット
    for xc, yc, dc in zip(x, y, d):
        if math.isnan(dc):
            print("Warn ", dc)
        else:
            c = t2c.conv(dc)
            m.plot(xc, yc, marker='o', color=c, markersize=ms)

    # 矢羽を描く
    m.barbs(x,
            y,
            u,
            v,
            sizes=dict(emptybarb=0.0),
            length=length,
            linewidth=lw,
            color='k')

    # タイトル
    if title is not None:
        fig.suptitle(title, size=24)

    # カラーバーを付ける
    t2c.colorbar(fig)

    # ファイルへの書き出し
    plt.savefig(output_filename, dpi=300, bbox_inches='tight')
    plt.close()


# 時刻の形式
# tinfo = "2021/03/12 16:10:00JST"
# tinfof = "20210312161000"
def main(tinfo=None, tinfof=None):
    if tinfof is not None:
        # 入力ファイル名
        input_filename = tinfof + ".csv"
        # 出力ファイル名
        output_filename = area + "_" + tinfof + ".png"
        # データの取得
        lons, lats, temp, u, v = read_data(input_filename)
        print(lons.shape, lats.shape, temp.shape, u.shape, v.shape)
        draw(lons, lats, temp, u, v, output_filename, title=tinfo)


if __name__ == '__main__':

    # 開始・終了時刻
    time_sta = datetime(2021, 5, 2, 10, 0, 0)
    time_end = datetime(2021, 5, 2, 14, 30, 0)
    time_step = timedelta(minutes=10)
    time = time_sta
    while True:
        if time <= time_end:
            tinfo = time.strftime("%Y/%m/%d %H:%M:%SJST")
            tinfof = time.strftime("%Y%m%d%H%M%S")
            print(tinfo)
            main(tinfo, tinfof)
        else:
            break
        time = time + time_step
