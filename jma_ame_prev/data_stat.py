#!/usr/bin/env python3
from amesta import AmedasStation

# アメダス地点リスト
sta_list = [
    "Sapporo", "Akita", "Tokyo", "Yokohama", "Nagoya", "Osaka", "Fukuoka"
]


if __name__ == '__main__':

    d = dict()
    for sta in sta_list:
        # AmedasStation Classの初期化
        amedas = AmedasStation(sta)

        # AmedasStation.retrieve_hourメソッドを使い、歴代1位の値、日付を取得
        ret = amedas.retrieve_stat()
        d.update(ret)

    # 取得した月最大24時間降水量データを表示
    print(d)
