

（１）アメダスデータの自動取得

get_jma_json.pyでは、指定した時刻範囲内のアメダスデータを取得することができる。
既に取得している場合には再取得は行わない。

開始・終了時刻は次のように設定する

time_sta = datetime(2021, 6, 30, 0, 0, 0)

time_end = datetime(2021, 7, 4, 21, 0, 0)

取得する時間間隔は

time_step = timedelta(minutes=10) # 10分毎

最新のもののみ取得する場合

opt_latest = True



* 単独の時刻データを取得したい場合

get_jma_json_1time.pyでは、最新のアメダスデータを取得する。

デフォルトのlatest = Noneを、次のように取得したい時刻に変更することもできる。
（数日前より古いデータは取得できないので注意）

latest = "2021-05-02T14:30:00+09:00"


% python3 get_jma_json.py 

出力：
時刻.json（ダウンロードしたファイル）
時刻.csv（変換したcsvファイル）


（２）気温と風の作図

cartopy_jma_temp+wind.pyで、開始・終了時刻を指定すると、その範囲内で作図。作図する時刻間隔はtime_stepで指定する。

areaは、現在のところJapanとTokyoのみ対応している。

% python3 cartopy_jma_temp+wind.py

出力：
Japan_時刻.png（area="Japan"の場合）



* Basemapを使ったもの

basemap_jma_temp+wind.py

開始・終了時刻、作図する時刻間隔はcartopyのものと同じ

% python3 basemap_jma_temp+wind.py

出力：
Japan_時刻.png（area="Japan"の場合）
Tokyo_時刻.png（area="Tokyo"の場合）



（３）24時間積算降水量の作図

cartopy_jma_rain24h.pyでareaを指定する。
今のところ、Japan、Tokyo、Tokai、Shizuokaに対応

開始・終了時刻は次のように設定する

time_sta = datetime(2021, 6, 30, 0, 0, 0)

time_end = datetime(2021, 7, 4, 21, 0, 0)

作図する時間間隔は

time_step = timedelta(hours=3) # 3時間毎


