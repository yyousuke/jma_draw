# jma_ame_nrt_map

最近の全アメダス地点データを取得し作図するプログラム
（数日前より古いデータは取得できないので注意）

# アメダスデータの取得

get_jma_json.pyでは、最近のアメダスデータを取得する。既に取得している場合には再取得は行わない

opt_latest = Trueとすれば、最新の時刻データのみを取得

opt_latest = False とすれば、時刻範囲を指定可能

その場合、開始・終了時刻は次のように設定する（7/1の10:30から7/2の20:30まで取得する場合）

time_sta = datetime(2021, 7, 1, 10, 30, 0)

time_end = datetime(2021, 7, 2, 20, 30, 0)

取得する時間間隔は

time_step = timedelta(minutes=10) # 10分毎

% python3 get_jma_json.py 

出力：

時刻.json（ダウンロードしたファイル）

時刻.csv（変換したcsvファイル）


＊単独の時刻データを取得したい場合

get_jma_json_1time.py

デフォルトのlatest = Noneを、次のように取得したい時刻に変更することもできる。

latest = "2021-05-02T14:30:00+09:00"


# アメダスデータの自動取得

get_jma_json_auto.pyでは、過去1日分のアメダスデータを取得する。既に取得している場合には再取得は行わない。

crontabなどに登録して自動実行することを前提に作られており、プログラムの実行場所に依存しないように、出力ディレクトリ等は絶対パスで与える。

output_dir = "データを出力するディレクトリの絶対パス"

cronで毎時15分に実行する設定

% crontab -eで編集

15  * * * *  プログラムを置いたディレクトリの絶対パス/get_jma_json_auto.py > /dev/null 2>& 1
(動作テストなど、ログを出したい場合には/dev/null以降を書かない)


# 風と気温の作図（basemap）

basemap_jma_temp+wind.py

開始・終了時刻を指定すると、その範囲内で作図。作図する時刻間隔はtime_stepで指定する

areaは、現在のところJapanとTokyoのみ対応している

% python3 basemap_jma_temp+wind.py

出力：

Japan_時刻.png（area="Japan"の場合）

Tokyo_時刻.png（area="Tokyo"の場合）


# 風と気温の作図（cartopy）

catopy_jma_temp+wind.py

開始・終了時刻（time_sta、time_end）を指定すると、その範囲内で作図。staで作図エリアを指定する。

作図：

% python3 catopy_jma_temp+wind.py --time_sta 開始時刻 --time_end 終了時刻 --sta 作図エリア名
--wind True --output_dir 出力ディレクトリ名

wind は、矢羽を描くかどうか（TrueかFalseで指定）。--wind False とすると、矢羽は描かず気温のマーカーのみになる。

--output_dir で出力ディレクトリを変更できる

作図する時刻間隔はtime_stepで指定する

time_step = timedelta(hours=3) # 3時間毎

staで指定可能なものは以下

"Japan"  全国、"Rumoi" 北海道（北西部）、"Abashiri" 北海道（東部）、"Sapporo" 北海道（南西部）、"Akita" 東北地方（北部）、"Sendai" 東北地方（南部）、"Tokyo" 関東地方、"Kofu" 甲信地方、"Niigata" 北陸地方（東部）、"Kanazawa" 北陸地方（西部）、"Nagoya" 東海地方、"Osaka" 近畿地方、"Okayama" 中国地方、"Kochi" 四国地方、"Fukuoka" 九州地方（北部）、"Kagoshima" 九州地方（南部）、"Naze" 奄美地方、"Naha" 沖縄本島地方、"Daitojima"   大東島地方、"Miyakojima" 宮古・八重山地方

他に、西日本を広域的に表示するWest、首都圏を拡大するTokyo_a、Tokyo_b、Chibaと静岡付近を拡大するShizuoka_aが指定可能

カラーバーに設定する気温の範囲は下限：tmin、上限：tmax、ラベルの値を描く間隔はtstepで与える

矢羽を描く値は、短矢羽：half、長矢羽：full、旗矢羽：flagで設定する

出力：

地域_temp+wind_時刻.png（opt_barbs=Trueの場合）

地域_temp_時刻.png（opt_barbs=Falseの場合）


# 降水量の作図（cartopy）

cartopy_jma_rain3h.py、cartopy_jma_rain24h.py

3時間積算降水量と24時間積算降水量を作図する

開始・終了時刻（time_sta、time_end）を指定すると、その範囲内で作図。staで作図エリアを指定する。

作図：

% python3 cartopy_jma_rain3h.py --time_sta 開始時刻 --time_end 終了時刻 --sta 作図エリア名
--mlabel  False --output_dir 出力ディレクトリ名

% python3 cartopy_jma_rain24h.py --time_sta 開始時刻 --time_end 終了時刻 --sta 作図エリア名
--mlabel  False --output_dir 出力ディレクトリ名

--mlabel True とすると、降水量のマーカーの隣に数字で降水量を表示する

--output_dir で出力ディレクトリを変更できる

作図する時間間隔を変更する場合には、time_stepを変える必要がある

time_step = timedelta(hours=1) # 1時間毎（3時間積算降水量）

time_step = timedelta(hours=3) # 3時間毎（24時間積算降水量）

出力：

地域_rain3h_時刻.png（cartopy_jma_rain3h.pyの場合）

地域_rain24h_時刻.png（cartopy_jma_rain24h.pyの場合）

#  積算降水量の作図（cartopy）

cartopy_jma_cumrain.py

1時間積算降水量から積算降水量を算出し作図する

開始・終了時刻（time_sta、time_end）を指定すると、その範囲内で開始時刻からの積算降水量を作図。staで作図エリアを指定する。

作図：

% python3 cartopy_jma_cumrain.py --time_sta 開始時刻 --time_end 終了時刻 --sta 作図エリア名
--mlabel  False --output_dir 出力ディレクトリ名

--mlabel True とすると、降水量のマーカーの隣に数字で降水量を表示する

--output_dir で出力ディレクトリを変更できる

作図する時間間隔を変更する場合には、time_stepを変える必要がある

time_step = timedelta(hours=1) # 1時間毎

出力：

地域_cumrain_時刻.png

# 時系列データの作図

map_tvar_station.py 

開始・終了時刻（time_sta、time_end）を指定すると、その範囲内で作図。アメダス地点名（sta）で作図する地点名を指定。

作図：

python3 map_tvar_station.py --time_sta 開始時刻 --time_end 終了時刻 --sta アメダス地点名
--cumrain False --output_dir 出力ディレクトリ名

--cumrain True とすると1時間降水量ではなく積算降水量をプロットする

--output_dir で出力ディレクトリを変更できる

作図する時間間隔を変更する場合には、time_stepを変える必要がある

time_step = timedelta(hours=1) # 1時間毎


