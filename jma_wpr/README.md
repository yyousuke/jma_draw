# jma_wpr

## 実行環境の準備

下記のパッケージを導入する

- Numpy

- Pandas

- json

- urllib

- matplotlib

## データの取得

get_wpr_json.pyを編集し、地点番号（station_no）を設定する

地点番号一覧は、[気象庁のウィンドプロファイラのページ](https://www.jma.go.jp/bosai/windprofiler/const/station.json "気象庁")から取得できる。

（get_wpr_json.pyを実行後に作成されるstation.jsonにも同じものが入る）

- 使用方法：

    % python3 get_wpr_json.py

- 出力：
    u_地点番号.csv（東西風速）
    
    v_地点番号.csv（南北風速）
    
    w_地点番号.csv（鉛直速度）
    
    station.json（地点番号一覧）
    
    times.json（取得可能なデータの時刻一覧）
    
    height.csv（データの高度一覧）
    
    time.csv（時刻一覧）

## 時間ー高度断面図作成

map_wpr.pyを編集し、地点番号をsta_idに、地点名をsta_nameに設定する

time.csvを確認し、map_wpr.pyを編集して切り出したい時刻番号をxmin、xmaxに設定する

（全時刻を使う場合には、xmin=None、xmax=Noneでよい）

必要な場合には、y軸の範囲を変更（デフォルトでは、ymin=0、ymax=8000）

図に表示したいタイトルをtitleに設定する

- 使用方法：

    % python3 map_wpr.py

- 出力：

    wpr.地点名.png
