#!/usr/bin/env python3
#
# Google Colaboratoryで動作するバージョンは、次のリンクから取得可能
# https://colab.research.google.com/drive/11TGDBFeDorzMs3a2EyBa0eieKL3WK8FY?usp=sharing
#
import os
import sys
import time
import json
import numpy as np
import pandas as pd
import itertools
import urllib.request
from PIL import Image
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

# 最新の画像だけを取得するかどうか
opt_latest = False # 取得可能な全時刻の画像を使用する場合（注意）
#opt_latest = True # 最新の画像だけを取得する場合

# 画像ファイルを保存するかどうか
opt_filesave = True # ファイルに保存（opt_latest = Falseの場合はデータサイズに注意）
#opt_filesave = False # 画面に表示（opt_latest = Falseの場合は全部表示されるので注意）


# path_to_dir: 作成するフォルダ名
def os_mkdir(path_to_dir):
    if not os.path.exists(path_to_dir):
        os.makedirs(path_to_dir)

def get_fileinfo():
    # 時刻データダウンロード
    url = "https://www.jma.go.jp/bosai/himawari/data/satimg/targetTimes_fd.json"
    urllib.request.urlretrieve(url, "targetTimes_fd.json")
    #
    # JSON形式読み込み
    with open("targetTimes_fd.json", 'rt') as fin:
        data = fin.read()
    df = pd.DataFrame(json.loads(data))
    print(df)
    basetimes = df.loc[:, 'basetime']
    validtimes = df.loc[:, 'validtime']
    #basetime = json_obj[0]['basetime']
    #validtime = json_obj[0]['validtime']
    return basetimes, validtimes


# ひまわり画像の取得
# basetime、validtime：時刻データから取得したもの
# mtype：赤外画像（"l"）、可視画像（"s"）、水蒸気画像（"v"）
#        トゥルーカラー再現画像（"tc"）、雲頂強調画像（"ct"）
# tile：タイル番号
#（確認ページ、https://maps.gsi.go.jp/development/tileCoordCheck.html）
def get_jpg(basetime=None, validtime=None, mtype="l", tile="3/7/3"):

    urlbase = "https://www.jma.go.jp/bosai/himawari/data/satimg/"
    if mtype == "l": # 赤外画像
        band_prod = "B13/TBB"
    elif mtype == "s": # 可視画像
        band_prod = "B03/ALBD"
    elif mtype == "v": # 水蒸気画像
        band_prod = "B08/TBB"
    elif mtype == "tc": # トゥルーカラー再現画像
        band_prod = "REP/ETC"
    elif mtype == "ct": # 雲頂強調画像
        band_prod = "SND/ETC"
    else:
        print("Invalid mtype") ; quit()
    if basetime is None or validtime is None:
        return None
    # URL
    url = urlbase + basetime + "/fd/" + validtime + "/" + band_prod + "/" + tile + ".jpg"
    print(url)
    im = Image.open(urllib.request.urlopen(url))
    return im


# 有効なタイルかどうかをチェックする
# （404エラー回避のため）
# z, x, y：タイルのズームレベル、タイルのx座標・y座標
def check_tile(z, x, y):
    valid = False
    if z == 5:
        if y >= 0 and y <= 31 and x >= 19 and x <= 31:
            valid = True
    elif z == 4:
        if y >= 0 and y <= 15 and x >= 9 and x <= 15:
            valid = True
    elif z == 3:
        if y >= 0 and y <= 7 and x >= 4 and x <= 7:
            valid = True
    return valid
    

# basetime、validtime：時刻データから取得したもの
# title：図のタイトル（Noneの場合はタイトルを付けない）
# file_path：保存するファイルのパス（Noneの場合は、ファイル保存せず画面に表示）
def draw_jp(z=5, y=12, x=27, basetime=None, validtime=None, title=None, file_path=None):
    if basetime is  None or validtime is None:
        raise Exception('basetime & validtime are required')
    # プロットエリアの定義
    fig = plt.figure(figsize=(10, 5.5))
    #fig = plt.figure(figsize=(10, 10))
    # 軸の追加
    for n in np.arange(2):
        xx = x + n
        ax = fig.add_subplot(1, 2, n+1)
        ax.xaxis.set_major_locator(ticker.NullLocator())
        ax.yaxis.set_major_locator(ticker.NullLocator())
        # 軸を表示しない
        plt.axis('off')
        plt.gca().spines['top'].set_visible(False)
        plt.gca().spines['bottom'].set_visible(False)
        plt.gca().spines['left'].set_visible(False)
        plt.gca().spines['right'].set_visible(False)
        # 画像の取得
        tile = str(z) + "/" + str(xx) + "/" + str(y)
        opt_draw = False
        if check_tile(z, xx, y):
            try:
                im = get_jpg(basetime, validtime, mtype="tc", tile=tile)
                opt_draw = True
            except:
                print("Warn: not found")
        else:
            raise Exception("invalid tile")

        # 画像を表示
        if opt_draw:
            ax.imshow(im, aspect='equal')
        # タイトル
        if title is not None and n == 1:
            ax.text(0.5, 0.7, title, fontsize=20, color='k', ha='center', va='bottom')

    # プロット範囲の調整
    plt.subplots_adjust(top=1.0, bottom=0.0, left=0.0, right=1.0, wspace=0.0, hspace=0.0)
    # ファイル書き出し
    if file_path is not None:
        plt.savefig(file_path, dpi=150, bbox_inches='tight')
    else:
        plt.show()


if __name__ == '__main__':

    # 時刻データの読み込み
    basetimes, validtimes = get_fileinfo()
    if opt_latest:
        basetimes = pd.Series(basetimes.iloc[-1])
        validtimes = pd.Series(validtimes.iloc[-1])
    #
    for basetime, validtime in zip(basetimes, validtimes):
        print(basetime, validtime)
        # 時刻
        time_UTC = pd.to_datetime(basetime)
        time_JST = time_UTC.tz_localize('GMT').tz_convert('Asia/Tokyo')
        # ファイル名などに表示する時刻
        ftime = time_JST.strftime("%Y%m%d-%H%M%S-00")
        UTC = time_UTC.strftime("%Y/%m/%d %H:%M:%S UTC")
        JST = time_JST.strftime("%Y/%m/%d %H:%M:%S JST")
        print(ftime)
        # 出力ディレクトリ
        output_dir = time_JST.strftime("%y%m%d")
        # 出力ディレクトリ作成
        os_mkdir(output_dir)
        # 出力ファイル
        png_file = 'ejp_s' + ftime + '.png'
        output_filedir = os.path.join(output_dir, png_file)
    
        # タイトル（時刻表示）
        title = JST + " (" + UTC + ")"
        # 画像の表示
        z = 5 # ズームレベル(3〜5、全球：4〜6）
        x = 27 # x方向の開始位置
        y = 12 # y方向
        opt_sleep = False
        if opt_filesave:
            if not os.path.exists(output_filedir):
                draw_jp(z=z, y=y, x=x, basetime=basetime, validtime=validtime, title=title, file_path=output_filedir)
                opt_sleep = True
        else:
            draw_jp(z=z, y=y, x=x, basetime=basetime, validtime=validtime, title=title, file_path=None)
            opt_sleep = True
        if opt_latest:
            opt_sleep = False
        if opt_sleep:
            time.sleep(10.0) # 10秒間待つ

