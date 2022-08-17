#!/opt/local/bin/python3
#
# 最近のアメダスデータを自動取得する（cronなどで定時取得することを想定）
# デフォルトでは1日前から最新のものまで10分毎のデータを取得する設定
# （既に取得されているものは再取得しない）
#
# cronで毎時15分に実行する設定
# % crontab -e
# 15  * * * *  /Users/path_to_program/get_jma_json_auto.py > /dev/null 2>& 1
#
from pandas import DataFrame
import pandas as pd
import numpy as np
import os
import time
import json
import urllib.request
from datetime import timedelta

# 出力するディレクトリ
output_dir = "/path_to_output"  # 配置するディレクトリに設定

# output_dir = "."


# dir_name: 作成するディレクトリ名
def os_mkdir(dir_name):
    if not os.path.isdir(dir_name):
        if os.path.isfile(dir_name):
            os.remove(dir_name)
        print("mkdir " + dir_name)
        os.makedirs(dir_name)


# データ取得部分
class AmedasStation():
    """AMeDASデータを取得し、ndarrayに変換する"""

    def __init__(self, latest=None, outdir_path="."):
        """
        Parameters:
        ----------
        latest: str
            取得する時刻（形式：20210819120000）
        output_dir_path: str
            出力ディレクトリのパス
        ----------
        """
        url = "https://www.jma.go.jp/bosai/amedas/data/latest_time.txt"
        if latest is None:
            latest = np.loadtxt(urllib.request.urlopen(url), dtype="str")
        print(latest)
        self.latest_time = pd.to_datetime(latest).strftime("%Y%m%d%H%M%S")
        print(self.latest_time)
        self.outdir_path = outdir_path

    def retrieve(self, cnt=2):
        """アメダスデータ取得
        Parameters:
        ----------
        cnt: int
            再取得カウント
        ----------
        Returns:
        ----------
        df: ndarray
            アメダスデータ
        ----------
        """
        outdir_path = self.outdir_path
        if cnt <= 0:  # 0の場合は終了
            raise RuntimeError('maximum count')
        url_top = "https://www.jma.go.jp/bosai/amedas/data/map/"
        file_name = self.latest_time + ".json"
        # 既に取得している場合
        if os.path.exists(os.path.join(outdir_path, file_name)):
            return None
        # アメダスデータの取得
        try:
            url = url_top + file_name
            print(url)
            urllib.request.urlretrieve(url,
                                       os.path.join(outdir_path, file_name))
        except OSError:
            time.sleep(10.0)  # 10秒間待つ
            self.retrieve(cnt=cnt - 1)  # cntを減らして再帰
        #
        # 取得したファイルを開く
        try:
            with open(os.path.join(outdir_path, file_name), 'rt') as fin:
                data = fin.read()
        except OSError as e:
            raise OSError(e)
        df = DataFrame(json.loads(data)).T
        # アメダス地点情報の取得
        df_location = self.location()
        df["lon"] = df_location.loc[:, "lon"]
        df["lat"] = df_location.loc[:, "lat"]
        df["kjName"] = df_location.loc[:, "kjName"]
        df["knName"] = df_location.loc[:, "knName"]
        df["enName"] = df_location.loc[:, "enName"]
        # csvファイルとして保存
        df.to_csv(os.path.join(outdir_path, self.latest_time + ".csv"))
        #
        # 取り出したデータを返却
        return df

    def location(self):
        """アメダス地点情報の取得"""
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
        except OSError as e:
            raise OSError(e)
        df = DataFrame(json.loads(data))
        # 取り出したデータを返却
        return df.T


if __name__ == '__main__':

    # 最新の時刻を取得
    # AmedasStation Classの初期化
    amedas = AmedasStation()
    #
    # 終了時刻:  日本時間の部分を取り出しdatetimeに変換
    time_end = pd.to_datetime(amedas.latest_time.split("+")[0])
    # 開始時刻:  1日前までを取得
    time_sta = time_end - timedelta(days=1)
    # time_sta = time_end - timedelta(hours=1)
    print(time_sta)
    print(time_end)
    #
    # 取得する間隔
    time_step = timedelta(minutes=10)
    # 指定した時刻範囲でアメダスデータを取得
    time_now = time_sta
    while True:
        if time_now <= time_end:
            latest = time_now.strftime("%Y-%m-%dT%H:%M:%S+09:00")
            print(latest)
            # 出力ディレクトリ（日付別/a）
            fdate = time_now.strftime("%y%m%d")
            outdir_path = os.path.join(output_dir, fdate, "a")
            os_mkdir(outdir_path)
            # AmedasStation Classの初期化
            amedas = AmedasStation(latest, outdir_path=outdir_path)
            # AmedasStation.retrieveメソッドを使い、アメダスデータを取得
            df = amedas.retrieve()
            if df is not None:
                time.sleep(10.0)  # 10秒間待つ
        else:
            break
        time_now = time_now + time_step
