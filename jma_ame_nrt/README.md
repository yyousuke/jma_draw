# jma_ame_nrt_map

最近の全アメダス地点データを取得し作図するプログラム
（数日前より古いデータは取得できないので注意）

## アメダスデータの取得

get_jma_json.pyでは、最近のアメダスデータを取得する。既に取得している場合には再取得は行わない

- **最新の時刻データのみを取得する場合**：プログラム中でopt_latest = True

- **指定した時刻範囲で取得する場合**：opt_latest = False

    その場合、開始・終了時刻は次のように設定する（7/1の10:30から7/2の20:30まで取得する場合）

    time_sta = datetime(2021, 7, 1, 10, 30, 0)

    time_end = datetime(2021, 7, 2, 20, 30, 0)

- **取得する時間間隔を変更する場合**：time_stepの間隔を変更（デフォルトでは10分毎）

    time_step = timedelta(minutes=10) # 10分毎

- 使用方法：

    % python3 get_jma_json.py 

- 出力：

    時刻.json（ダウンロードしたファイル）

    時刻.csv（変換したcsvファイル）


### 単独の時刻データを取得したい場合

get_jma_json_1time.pyを使う

デフォルトのlatest = Noneを、次のように取得したい時刻に変更することもできる

latest = "2021-05-02T14:30:00+09:00"


## アメダスデータの自動取得

get_jma_json_auto.pyでは、過去1日分のアメダスデータを取得する。既に取得している場合には再取得は行わない

crontabなどに登録して自動実行することを前提に作られており、プログラムの実行場所に依存しないように、出力ディレクトリ等は絶対パスで与える

- **出力ディレクトリ**：output_dir = "データを出力するディレクトリの絶対パス"

### cronで毎時15分に実行する設定

% crontab -eで編集

    15  * * * *  プログラムを置いたディレクトリの絶対パス/get_jma_json_auto.py > /dev/null 2>& 1

(動作テストなど、ログを出したい場合には > /dev/null以降を書かない)


## 風と気温の作図（basemap）

プログラム名：basemap_jma_temp+wind.py

開始・終了時刻を指定すると、その範囲内で作図。作図する時刻間隔はtime_stepで指定する

areaは、現在のところJapanとTokyoのみ対応している

- 使用方法：

    % python3 basemap_jma_temp+wind.py

- 出力：

    Japan_時刻.png（area="Japan"の場合）

    Tokyo_時刻.png（area="Tokyo"の場合）


## 風と気温、降水量の作図（cartopy）

catopy_jma_temp+wind.pyでは、風を矢羽、気温をマーカーでプロットする

catopy_jma_temp+wind+rain.pyでは、風を矢羽、気温をマーカー、降水量をテキストでプロットする

- 使用方法（気温と風）：

    % python3 catopy_jma_temp+wind.py --time_sta 開始時刻 --time_end 終了時刻 --sta 作図エリア名

    --addwind True --temprange 18.,38.,2. --output_dir 出力ディレクトリ名

- 使用方法（気温のみ）：

    % python3 catopy_jma_temp+wind.py --time_sta 開始時刻 --time_end 終了時刻 --sta 作図エリア名

    --addwind False --mlabel True --temprange 18.,38.,2. --output_dir 出力ディレクトリ名

- 使用方法（気温と風、降水量）：

    % python3 catopy_jma_temp+wind+rain.py --time_sta 開始時刻 --time_end 終了時刻 --sta 作図エリア名

    --addwind True --addrain True --temprange 18.,38.,2. --output_dir 出力ディレクトリ名

- 出力：

    地域_temp+wind_時刻.png（--addwind Trueの場合）

    地域_temp_時刻.png（--addwind Falseの場合）

    地域_temp+wind+rain_時刻.png（--addwind True、--addrain Trueの場合）

### オプション

- **--time_sta**：作図開始時刻

- **--time_end**：作図終了時刻

    時刻指定は次のような形式で行う

    例：7/1の09:00から18:00の場合：--time_sta 20210701090000 --time_end 20210701180000

- **--sta**：作図エリアを指定

- **--addwind**：矢羽を描くかどうか（TrueかFalseで指定）。--addwind False とすると、矢羽は描かず気温のマーカーのみになる

- **--mlabel**：気温のマーカーの横に気温をテキストで描くかどうか（TrueかFalseで指定）。catopy_jma_temp+wind.pyのみのオプション

- **--addrain**：気温のマーカーの横に降水量をテキストで描くかどうか（TrueかFalseで指定）。--addrain False とするとプロットされない。catopy_jma_temp+wind+rain.pyのみのオプション

- **--temprange**：カラーバーに設定する気温の範囲（下限,上限,間隔）。下限と上限はカラーバーのラベルの範囲を、間隔は目盛り線ラベルの値を描く間隔を指定する

    --temprange 18.,38.,2.では、下限18、上限38で、間隔は2毎（18.,38.のように目盛り線の間隔は省略可）。最初がマイナスの場合は、/-16,16,2/のように囲う（<>, (), {}, |, /が使用可）

- **--output_dir**：出力ディレクトリを変更できる

- **--sta**：作図エリア名。指定可能なものは以下

    "Japan"  全国、"Rumoi" 北海道（北西部）、"Abashiri" 北海道（東部）、"Sapporo" 北海道（南西部）、"Akita" 東北地方（北部）、"Sendai" 東北地方（南部）、"Tokyo" 関東地方、"Kofu" 甲信地方、"Niigata" 北陸地方（東部）、"Kanazawa" 北陸地方（西部）、"Nagoya" 東海地方、"Osaka" 近畿地方、"Okayama" 中国地方、"Kochi" 四国地方、"Fukuoka" 九州地方（北部）、"Kagoshima" 九州地方（南部）、"Naze" 奄美地方、"Naha" 沖縄本島地方、"Daitojima"   大東島地方、"Miyakojima" 宮古・八重山地方

    他に、西日本を広域的に表示するWest、首都圏を拡大するTokyo_a、Tokyo_b、Chibaと静岡付近を拡大するShizuoka_aが指定可能

### プログラム中の設定で変更可能なもの

- **作図する時間間隔を変更する場合**：プログラム中のtime_stepを変更（デフォルトでは10分毎）

    time_step = timedelta(minutes=10) # 10分毎

- **矢羽を描く値を変更する場合**：プログラム中のhalf、full、flagを変更

    短矢羽：half、長矢羽：full、旗矢羽：flag（デフォルトでは、短矢羽：1m/s、長矢羽：5m/s、旗矢羽：10m/s）

## 降水量の作図（cartopy）

cartopy_jma_rain3h.pyでは3時間積算降水量、cartopy_jma_rain24h.pyでは24時間積算降水量を作図する

- 使用方法：

    % python3 cartopy_jma_rain3h.py --time_sta 開始時刻 --time_end 終了時刻 --sta 作図エリア名

    --mlabel  False --output_dir 出力ディレクトリ名

    % python3 cartopy_jma_rain24h.py --time_sta 開始時刻 --time_end 終了時刻 --sta 作図エリア名

    --mlabel  False --output_dir 出力ディレクトリ名

- 出力：

    地域_rain3h_時刻.png（cartopy_jma_rain3h.pyの場合）

    地域_rain24h_時刻.png（cartopy_jma_rain24h.pyの場合）

### オプション

- **--time_sta**：作図開始時刻

- **--time_end**：作図終了時刻

- **--sta**：作図エリアを指定

- **--mlabel**：True とすると、降水量のマーカーの隣に数字で降水量を表示する

- **--output_dir**：出力ディレクトリを変更できる

### プログラム中の設定で変更可能なもの

- **作図する時間間隔を変更する場合**：プログラム中のtime_stepを変更

    time_step = timedelta(hours=1) # 1時間毎（3時間積算降水量の場合のデフォルト）

    time_step = timedelta(hours=3) # 3時間毎（24時間積算降水量の場合のデフォルト）


##  積算降水量の作図（cartopy）

cartopy_jma_cumrain.pyでは、1時間積算降水量から積算降水量を算出し作図する

- 使用方法：

    % python3 cartopy_jma_cumrain.py --time_sta 開始時刻 --time_end 終了時刻 --sta 作図エリア名

    --mlabel  False --output_dir 出力ディレクトリ名

- 出力：

    地域_cumrain_時刻.png

### オプション

- **--time_sta**：降水量の積算開始時刻

- **--time_end**：積算降水量の作図終了時刻

- **--sta**：作図エリアを指定

- **--mlabel**：True とすると、降水量のマーカーの隣に数字で降水量を表示する

- **--output_dir**：出力ディレクトリを変更できる

### プログラム中の設定で変更可能なもの

- **作図する時間間隔を変更する場合**：プログラム中のtime_stepを変更（デフォルトでは1時間毎）

    time_step = timedelta(hours=1) # 1時間毎


## 時系列データの作図

map_tvar_station.pyでは、指定したアメダス地点名（sta）、開始・終了時刻（time_sta、time_end）の範囲で、1時間降水量もしくは積算降水量の時系列図を作成する

- 使用方法：

    python3 map_tvar_station.py --time_sta 開始時刻 --time_end 終了時刻 --sta アメダス地点名

    --cumrain False --output_dir 出力ディレクトリ名

- 出力：

    tvar_地域.png

### オプション

- **--time_sta**：作図開始時刻

- **--time_end**：作図終了時刻

- **--cumrain**：True とすると1時間降水量ではなく積算降水量をプロットする

- **--output_dir**：出力ディレクトリを変更できる

### プログラム中の設定で変更可能なもの

- **作図する時間間隔を変更する場合**：プログラム中のtime_stepを変更（デフォルトでは1時間毎）

    time_step = timedelta(hours=1) # 1時間毎


## 直近のデータのみ取得し作図まで行う場合

map_latest_cartopy.pyでは、直近のアメダスデータを取得し、指定した作図エリア（sta）で水平面図を作成する

- 使用方法：

    % python3 map_latest_cartopy.py --sta アメダス地点名

    --addwind True --temprange 18.,38.,2. --output_dir 出力ディレクトリ名

- 出力：

    地域_temp+wind_時刻.png（--addwind Trueの場合）

    地域_temp_時刻.png（--addwind Falseの場合）

### オプション

- **--sta**：地点名

- **--addwind**： 矢羽を描くかどうか（TrueかFalseで指定）。--addwind False とすると、矢羽は描かず気温のマーカーのみになる

- **--temprange**：カラーバーのラベルの範囲と目盛り線の間隔を指定できる

    --temprange 18.,38.,2.では、最小18、最大38で、目盛り線の間隔は2毎（18.,38.のように目盛り線の間隔は省略可）。最初がマイナスの場合は、/-16,16,2/のように囲う（<>, (), {}, |, /が使用可）

- **--output_dir**：出力ディレクトリを変更できる

### プログラム中の設定で変更可能なもの

- **取得する降水量データ**：rainstepを変更する（デフォルトは前1時間降水量、10m、1h、3h、24hが指定可能）

    amedas.read_data(rainstep="1h") # 前1時間降水量

