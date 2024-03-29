# jma_sat

## 実行環境の準備

下記のパッケージを導入する

- opencv

- Pillow

- json

- urllib

- Numpy

- Pandas

- matplotlib

## 作図の準備

get_jma_jp.pyを編集

- **最新の画像だけを取得するかどうか**: opt_latest = True | False

    取得開始する時刻以降の全時刻の画像を使用する場合はTrue（注意）

    最新の画像だけを取得する場合はFalse

- **取得開始する時刻（UTC）**：start_time_UTC = "時刻"

    時刻は次のような形式で与える
    
    "20180902210000" （UTC） 、または、"2018-01-21 00:00:00"（UTC、ISO形式）

- **地図を重ねるかどうか**: opt_map = True | False

    地図を重ねる場合はTrue、衛星画像のみの場合はFalse

- **画像の種類**: mtype（画像取得）、mtypef（ファイル名の一部に表示されるもの）

    mtype：赤外画像（"l"）、可視画像（"s"）、水蒸気画像（"v"）、トゥルーカラー再現画像（"tc"）、雲頂強調画像（"ct"）

    mtypef：赤外画像（"l"）、可視画像（"s"）、水蒸気画像（"v"）、トゥルーカラー再現画像（"t"）、雲頂強調画像（"m"）

- **日本付近の拡大画像を取得するかどうか**: opt_jp = True | False

    日本付近の場合はTrue（ズームレベル6のみ）、全球画像の場合はFalse（ズームレベル3〜5）

- **ズームレベル**: z = 整数

    全球：3〜5、日本域最大：6

- **タイル座標**: x=整数、y=整数

    x方向の開始位置とy方向の開始位置の座標
    
    z/x/yの位置は[タイル画像確認ページ](https://maps.gsi.go.jp/development/tileCoordCheck.html "国土地理院")で確認できる

- **タイルの数**: nmax = 整数

    取得するタイルの数を指定する（1、4、9など）

- **画像ファイルを保存するかどうか**: opt_filesave = True | False

    ファイルに保存する場合はTrue、画面に表示する場合はFalse

## 作図

- 使用方法：

    % python3 get_jma_jp.py

- 出力：

    ./日付/jp_(画像の種類)(時刻).png

