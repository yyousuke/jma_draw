# jma_ame_prev

## map_jma.py

指定したアメダス地点で時系列図を作成する

- **アメダス地点の設定**：sta = "地点名"

    例：sta = "Tokyo"

- **作図する日付**：date = "日付"または"yesterday"

    例：date = "20210123"

    前日のアメダスデータ作図を行う場合には、date = "yesterday"も指定可能

- **矢羽を描くかどうか**：plt_barbs = True | False

    Trueで矢羽を描く、Falseで描かない

- **矢羽をノット表示にするかどうか**：barbs_kt = True | False

    barbs_kt = True でノット表示、Falseでm/s表示

- **積雪量データを描くかどうか**：opt_snow = True | False

    opt_snow = Trueで描く、Falseで描かない

## data_stat.py

指定したアメダス地点で歴代1位の月最大24時間降水量の値、その日付を取得して表示

- **表示したいアメダス地点リスト**：sta_list = ["地点名1", "地点名2" ]
