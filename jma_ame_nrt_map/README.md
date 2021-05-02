

（１）アメダスデータの取得

get_jma_json.pyでは、最新のアメダスデータを取得する。

デフォルトのlatest = Noneを、次のように取得したい時刻に変更することもできる。
（数日前より古いデータは取得できないので注意）

latest = "2021-05-02T14:30:00+09:00"


% python3 get_jma_json.py 

出力：
時刻.json（ダウンロードしたファイル）
時刻.csv（変換したcsvファイル）


（２）作図

basemap_jma_temp+wind.pyで、開始・終了時刻を指定すると、その範囲内で作図。作図する時刻間隔はtime_stepで指定する。

areaは、現在のところJapanとTokyoのみ対応している。

% python3 basemap_jma_temp+wind.py

出力：
Japan_時刻.png（area="Japan"の場合）
Tokyo_時刻.png（area="Tokyo"の場合）



