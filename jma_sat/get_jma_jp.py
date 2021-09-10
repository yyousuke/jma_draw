#!/usr/bin/env python3
#
# get_jma_jp
# 日本周辺のひまわり画像を最大解像度（ズームレベル６）で表示する
# 2021/03/29 初版　山下陽介（国立環境研究所）
# 2021/07/09 ズームレベル６対応
#
# Google Colaboratoryで動作するバージョンは、次のリンクから取得可能
# https://colab.research.google.com/drive/1NtZSQR-JREDH1PnL7T-eInR-CW046iKK
#
import os
import sys
import time
import cv2
import json
import numpy as np
import pandas as pd
import itertools
import urllib.request
from PIL import Image
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

# 最新の画像だけを取得するかどうか
opt_latest = False  # 取得開始する時刻以降の全時刻の画像を使用する場合（注意）
#opt_latest = True  # 最新の画像だけを取得する場合
# 取得開始する時刻（UTC）
start_time_UTC = "20210827 22:00:00"

opt_map = False  # 地図を重ねるかどうか
#opt_map = True # 地図を重ねるかどうか

# 画像の種類
#mtype = "l"  # 赤外
#mtypef = "l"  # 赤外
mtype = "tc"  # 可視トゥルーカラー再現画像
mtypef = "t"  # 可視トゥルーカラー再現画像
#mtype = "ct"  # 雲頂強調
#mtypef = "m"  # 雲頂強調
#
# 取得するタイル座標の設定
opt_jp = True  # Trueではズームレベル6を取得
#opt_jp = False # Falseではズームレベル3〜5を取得
z = 6  # ズームレベル(全球：3〜5、日本域最大：6, 6ではopt_jp=Trueが必要）
x = 55  # x方向の開始位置
y = 26  # y方向
nmax = 4  # タイルの数

# 画像ファイルを保存するかどうか
opt_filesave = True  # ファイルに保存（opt_latest = Falseの場合はデータサイズに注意）

#opt_filesave = False # 画面に表示（opt_latest = Falseの場合は全部表示されるので注意）


def os_mkdir(path_to_dir):
    """ディレクトリを作成する

    Parameters:
    ----------
    path_to_dir: str
        作成するディレクトリ名
    ----------
    """
    if not os.path.exists(path_to_dir):
        os.makedirs(path_to_dir)


def get_fileinfo(opt_jp=False):
    """時刻データダウンロード

    Parameters:
    ----------
    opt_jp: bool
        日本付近の最高解像度データを取得するかどうか
    ----------
    Returns:
    ----------
    basetimes: pandas.Series(str, str, ...)
        時刻データから取得したbasetime
    validtimes: pandas.Series(str, str, ...)
        時刻データから取得したvalidtime
    ----------
    """
    # ダウンロード
    if opt_jp:  # 日本付近のデータ
        url = "https://www.jma.go.jp/bosai/himawari/data/satimg/targetTimes_jp.json"
    else:  # 全球画像データ
        url = "https://www.jma.go.jp/bosai/himawari/data/satimg/targetTimes_fd.json"
    urllib.request.urlretrieve(url, "targetTimes.json")
    #
    # JSON形式読み込み
    with open("targetTimes.json", 'rt') as fin:
        data = fin.read()
    df = pd.DataFrame(json.loads(data))
    print(df)
    basetimes = df.loc[:, 'basetime']
    validtimes = df.loc[:, 'validtime']
    return basetimes, validtimes


def get_jpg(basetime=None,
            validtime=None,
            mtype="l",
            tile="3/7/3",
            opt_jp=False):
    """ひまわり画像の取得

    Parameters:
    ----------
    basetime: str
        時刻データから取得したもの
    validtime: str
        時刻データから取得したもの
    mtype: str
        赤外画像（"l"）、可視画像（"s"）、水蒸気画像（"v"）、
        トゥルーカラー再現画像（"tc"）、雲頂強調画像（"ct"）
    tile: str
        タイル番号
       （確認ページ、https://maps.gsi.go.jp/development/tileCoordCheck.html）
    opt_jp: bool
        日本付近の最高解像度データを取得するかどうか
    ----------
    Returns:
    ----------
    im: PIL.PngImagePlugin.PngImageFile
        ダウンロードした画像データ
    ----------
    """
    if basetime is None or validtime is None:
        raise ValueError("basetime and validtime are needed")
    #
    urlbase = "https://www.jma.go.jp/bosai/himawari/data/satimg/"
    if mtype == "l":  # 赤外画像
        band_prod = "B13/TBB"
    elif mtype == "s":  # 可視画像
        band_prod = "B03/ALBD"
    elif mtype == "v":  # 水蒸気画像
        band_prod = "B08/TBB"
    elif mtype == "tc":  # トゥルーカラー再現画像
        band_prod = "REP/ETC"
    elif mtype == "ct":  # 雲頂強調画像
        band_prod = "SND/ETC"
    else:
        raise ValueError("Invalid mtyp")
    # URL
    if opt_jp:  # 日本付近のデータ
        url = urlbase + basetime + "/jp/" + validtime + "/" + band_prod + "/" + tile + ".jpg"
    else:  # 全球画像データ
        url = urlbase + basetime + "/fd/" + validtime + "/" + band_prod + "/" + tile + ".jpg"
    print(url)
    im = Image.open(urllib.request.urlopen(url))
    return im


def get_tile(tile="3/7/3", mtype="std"):
    """地理院タイル画像の取

    Parameters:
    ----------
    tile: str
        タイル番号
       （確認ページ、https://maps.gsi.go.jp/development/tileCoordCheck.html）
    mtype: str
        地図のタイプ
       （std：標準地図、pale：淡色地図、blank：白地図(5-)、seamlessphoto：写真）
    ----------
    Returns:
    ----------
    im: PIL.PngImagePlugin.PngImageFile
        ダウンロードした画像データ
    ----------
    """

    urlbase = "https://cyberjapandata.gsi.go.jp/xyz/"
    #"https://cyberjapandata.gsi.go.jp/xyz/std/6/57/23.png"
    if basetime is None or validtime is None:
        raise ValueError("Invalid mtyp")
        return None
    # URL
    url = urlbase + mtype + "/" + tile + ".png"
    print(url)
    im = Image.open(urllib.request.urlopen(url))
    return im


def pil2cv(im):
    """PIL型 -> OpenCV型"""
    im = np.array(im, dtype=np.uint8)
    if im.ndim == 2:  # モノクロ
        pass
    elif im.shape[2] == 3:  # カラー
        im = cv2.cvtColor(im, cv2.COLOR_RGB2BGR)
    elif im.shape[2] == 4:  # 透過
        im = cv2.cvtColor(im, cv2.COLOR_RGBA2BGRA)
    return im


def map_blend(im1, im2, alpha=0.5, beta=0.5, gamma=0.0):
    """画像のブレンド

    Parameters:
    ----------
    im1: numpy.ndarray
        画像データ1
    im2: numpy.ndarray
        画像データ2
    alpha: float
        ブレンドする比率（画像データ1）
    beta: float
        ブレンドする比率（画像データ2）
    gamma: float
        全体に足す値
    ----------
    Returns:
    ----------
    im: numpy.ndarray
        ブレンドした画像データ
        im = im1 * alpha + im2 * beta + gamma
    ----------
    """
    # ブレンド
    im = cv2.addWeighted(im1, alpha, im2, beta, gamma)
    return im


def check_tile(z, x, y):
    """有効なタイルかどうかをチェックする
      （404エラー回避のため）

    Parameters:
    ----------
    z: int
        ズームレベル
    x: int
        経度方向のタイル座標
    y: int
        緯度方向のタイル座標
    ----------
    """
    valid = False
    if z == 6:
        if y >= 21 and y <= 29 and x >= 51 and x <= 60:
            valid = True
    elif z == 5:
        if y >= 0 and y <= 31 and x >= 19 and x <= 31:
            valid = True
    elif z == 4:
        if y >= 0 and y <= 15 and x >= 9 and x <= 15:
            valid = True
    elif z == 3:
        if y >= 0 and y <= 7 and x >= 4 and x <= 7:
            valid = True
    return valid


def draw_tile(z=5, y=12, x=27, nmax=4, file_path=None, mtype="blank"):
    """地理院タイルの作成

    Parameters:
    ----------
    z: int
        ズームレベル
    x: int
        経度方向のタイル座標：開始座標（左上）タイルの値
    y: int
        緯度方向のタイル座標：開始座標（左上）タイルの値
    nmax: int
        タイルの数
    file_path: str
        保存するファイルのパス（Noneの場合は、ファイル保存しない）
    mtype: str
        取得する画像の種類
    ----------
    """
    nx = max(int(np.sqrt(nmax)), 1)
    ny = max(int(np.sqrt(nmax)), 1)
    x_size = 9
    y_size = 9
    if nx * ny < nmax:
        nx = nx + 1
        y_size = 6
        if nx * ny < nmax:
            ny = ny + 1
            y_size = 9
    # プロットエリアの定義
    fig = plt.figure(figsize=(8, 8))
    # 軸の追加
    xx = x
    yy = y
    for n in np.arange(nmax):
        if xx == x + nx:
            xx = x
            yy = yy + 1
        ax = fig.add_subplot(ny, nx, n + 1)
        ax.xaxis.set_major_locator(ticker.NullLocator())
        ax.yaxis.set_major_locator(ticker.NullLocator())
        # 軸を表示しない
        plt.axis('off')
        plt.gca().spines['top'].set_visible(False)
        plt.gca().spines['bottom'].set_visible(False)
        plt.gca().spines['left'].set_visible(False)
        plt.gca().spines['right'].set_visible(False)
        #
        tile = str(z) + "/" + str(xx) + "/" + str(yy)
        opt_draw = False
        if check_tile(z, xx, yy):
            try:
                # 地理院タイルの取得
                im = get_tile(tile, mtype=mtype)
                time.sleep(1.0)  # 1秒間待つ
                opt_draw = True
            except:
                raise Exception("not found")
        else:
            raise ValueError("invalid tile")

        # 画像を表示
        if opt_draw:
            ax.imshow(im, aspect='equal')
        xx = xx + 1

    # プロット範囲の調整
    plt.subplots_adjust(top=1.0,
                        bottom=0.0,
                        left=0.0,
                        right=1.0,
                        wspace=0.0,
                        hspace=0.0)
    # ファイル書き出し
    if file_path is not None:
        plt.savefig(file_path, dpi=150, bbox_inches='tight')


def draw_sat(z=5,
             y=12,
             x=27,
             nmax=4,
             basetime=None,
             validtime=None,
             file_path=None,
             opt_jp=False,
             mtype="tc"):
    """衛星画像を取得し結合する

    Parameters:
    ----------
    z: int
        ズームレベル
    x: int
        経度方向のタイル座標：開始座標（左上）タイルの値
    y: int
        緯度方向のタイル座標：開始座標（左上）タイルの値
    nmax: int
        タイルの数
    basetime: str
        時刻データから取得したもの
    validtime: str
        時刻データから取得したもの
    file_path: str
        保存するファイルのパス（Noneの場合は、ファイル保存しない）
    opt_jp: bool
        日本付近の最高解像度データを取得するかどうか
    mtype: str
        取得する画像の種類
    ----------
    """
    nx = max(int(np.sqrt(nmax)), 1)
    ny = max(int(np.sqrt(nmax)), 1)
    x_size = 9
    y_size = 9
    if nx * ny < nmax:
        nx = nx + 1
        y_size = 6
        if nx * ny < nmax:
            ny = ny + 1
            y_size = 9
    if basetime is None or validtime is None:
        raise ValueError('basetime & validtime are required')
    # プロットエリアの定義
    fig = plt.figure(figsize=(x_size, y_size))
    # 軸の追加
    xx = x
    yy = y
    for n in np.arange(nmax):
        if xx == x + nx:
            xx = x
            yy = yy + 1
        ax = fig.add_subplot(ny, nx, n + 1)
        ax.xaxis.set_major_locator(ticker.NullLocator())
        ax.yaxis.set_major_locator(ticker.NullLocator())
        # 軸を表示しない
        plt.axis('off')
        plt.gca().spines['top'].set_visible(False)
        plt.gca().spines['bottom'].set_visible(False)
        plt.gca().spines['left'].set_visible(False)
        plt.gca().spines['right'].set_visible(False)
        #
        tile = str(z) + "/" + str(xx) + "/" + str(yy)
        print(tile)
        opt_draw = False
        if check_tile(z, xx, yy):
            try:
                # 画像の取得
                im = get_jpg(basetime,
                             validtime,
                             mtype=mtype,
                             tile=tile,
                             opt_jp=opt_jp)
                time.sleep(1.0)  # 1秒間待つ
                opt_draw = True
            except:
                raise Exception("not found")
        else:
            raise ValueError("invalid tile")

        # 画像を表示
        if opt_draw:
            ax.imshow(im, aspect='equal')
        xx = xx + 1

    # プロット範囲の調整
    plt.subplots_adjust(top=1.0,
                        bottom=0.0,
                        left=0.0,
                        right=1.0,
                        wspace=0.0,
                        hspace=0.0)
    # ファイル書き出し
    if file_path is not None:
        plt.savefig(file_path, dpi=150, bbox_inches='tight')
    plt.close()


def draw_jp(z=5,
            y=12,
            x=27,
            nmax=4,
            basetime=None,
            validtime=None,
            title=None,
            file_path=None,
            opt_jp=False,
            opt_map=False,
            mtype="tc"):
    """衛星画像の作図

    Parameters:
    ----------
    z: int
        ズームレベル
    x: int
        経度方向のタイル座標：開始座標（左上）タイルの値
    y: int
        緯度方向のタイル座標：開始座標（左上）タイルの値
    nmax: int
        タイルの数
    basetime: str
        時刻データから取得したもの
    validtime: str
        時刻データから取得したもの
    title: str
        図のタイトル（Noneの場合はタイトルを付けない）
    file_path: str
        保存するファイルのパス（Noneの場合は、ファイル保存しない）
    opt_jp: bool
        日本付近の最高解像度データを取得するかどうか
    opt_map: bool
        地図を重ねるかどうか
    mtype: str
        取得する画像の種類
    ----------
    """
    if basetime is None or validtime is None:
        raise ValueError('basetime & validtime are required')

    # 地理院タイルの作成
    if opt_map:
        if not os.path.exists("map_tile.jpg"):
            draw_tile(z=z,
                      y=y,
                      x=x,
                      nmax=nmax,
                      file_path="map_tile.jpg",
                      mtype="blank")

    # 衛星画像の作成
    draw_sat(z=z,
             y=y,
             x=x,
             nmax=nmax,
             basetime=basetime,
             validtime=validtime,
             file_path="map_sat.jpg",
             opt_jp=opt_jp,
             mtype=mtype)

    # プロットエリアの定義
    fig = plt.figure(figsize=(8, 8))
    ax = fig.add_subplot(1, 1, 1)
    ax.xaxis.set_major_locator(ticker.NullLocator())
    ax.yaxis.set_major_locator(ticker.NullLocator())
    # 軸を表示しない
    plt.axis('off')
    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['bottom'].set_visible(False)
    plt.gca().spines['left'].set_visible(False)
    plt.gca().spines['right'].set_visible(False)

    if opt_map:
        # 一時ファイルの読み込み
        src1 = cv2.imread("map_tile.jpg")
        src2 = cv2.imread("map_sat.jpg")
        # 画像変換
        #src1 = pil2cv(src1) #
        src1 = cv2.bitwise_not(src1)  # 白黒反転
        src2 = pil2cv(src2)  # cv2のRGB値へ変換
        src2 = cv2.resize(src2, dsize=(src1.shape[0], src1.shape[1]))

        # 画像をブレンド
        im = map_blend(src1, src2, 0.4, 1.0)
        #im = map_blend(src1, src2, 0.2, 0.8)
    else:
        src = cv2.imread("map_sat.jpg")
        im = pil2cv(src)  # cv2のRGB値へ変換
    # 画像を表示
    ax.imshow(im, aspect='equal')

    # タイトル
    if title is not None:
        ax.set_title(title, fontsize=20, color='k')

    # プロット範囲の調整
    plt.subplots_adjust(top=1.0,
                        bottom=0.0,
                        left=0.0,
                        right=1.0,
                        wspace=0.0,
                        hspace=0.0)
    # ファイル書き出し
    if file_path is not None:
        plt.savefig(file_path, dpi=150, bbox_inches='tight')
    else:
        plt.show()
    plt.close()


if __name__ == '__main__':

    # 時刻データの読み込み
    basetimes, validtimes = get_fileinfo(opt_jp=False)
    if opt_latest:
        basetimes = pd.Series(basetimes.iloc[-1])
        validtimes = pd.Series(validtimes.iloc[-1])
    if start_time_UTC is not None:
        time_start = pd.to_datetime(start_time_UTC)
    else:
        time_start = pd.to_datetime(basetimes.iloc[0])
    #
    for basetime, validtime in zip(basetimes, validtimes):
        print(basetime, validtime)
        # 時刻
        time_UTC = pd.to_datetime(basetime)
        time_JST = time_UTC.tz_localize('GMT').tz_convert('Asia/Tokyo')
        if time_UTC >= time_start:
            # ファイル名などに表示する時刻
            ftime = time_JST.strftime("%Y%m%d-%H%M%S-00")
            UTC = time_UTC.strftime("%Y/%m/%d %H:%M:%S UTC")
            JST = time_JST.strftime("%Y/%m/%d %H:%M:%S JST")
            print(ftime)
            # 出力ディレクトリ
            output_dir = time_JST.strftime("%y%m%d")
            # 出力ディレクトリ作成
            if opt_filesave:
                os_mkdir(output_dir)
            # 出力ファイル
            png_file = 'jp_' + mtypef + ftime + '.png'
            output_filedir = os.path.join(output_dir, png_file)

            # タイトル（時刻表示）
            title = JST + " (" + UTC + ")"
            # 画像の表示
            opt_sleep = False
            if opt_filesave:
                if not os.path.exists(output_filedir):
                    draw_jp(z=z,
                            y=y,
                            x=x,
                            nmax=nmax,
                            basetime=basetime,
                            validtime=validtime,
                            title=title,
                            file_path=output_filedir,
                            opt_jp=opt_jp,
                            opt_map=opt_map,
                            mtype=mtype)
                    opt_sleep = True
            else:
                draw_jp(z=z,
                        y=y,
                        x=x,
                        nmax=nmax,
                        basetime=basetime,
                        validtime=validtime,
                        title=title,
                        file_path=None,
                        opt_jp=opt_jp,
                        opt_map=opt_map,
                        mtype=mtype)
                opt_sleep = True
            if opt_latest:
                opt_sleep = False
            if opt_sleep:
                time.sleep(10.0)  # 10秒間待つ
        else:
            print("skip")
