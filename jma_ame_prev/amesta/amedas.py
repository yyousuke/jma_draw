#
#  2018/07/19 Yamashita
#  アメダス地点の情報を返す
#
from pandas import Series, DataFrame
import pandas as pd
from io import StringIO

pd.set_option('display.max_columns', 50)


class AmedasStation():
    """アメダス地点情報の取得"""

    def __init__(self, sta):
        """アメダス地点情報を返す
        Parameters:
        ----------
        sta: str
           アメダス地点名
        ----------
        """
        self.sta = sta
        self.stacode = None
        self.areacode = None
        self.groupcode = None
        self.precno = None
        self.blockno = None
        if sta == "Sapporo":
            self.stacode = "14163"
            self.areacode = "000"
            self.groupcode = "12"
            self.precno = "14"
            self.blockno = "47412"
        if sta == "Aomori":
            self.stacode = "31312"
            self.areacode = "000"
            self.groupcode = "20"
            self.precno = "31"
            self.blockno = "47575"
        if sta == "Akita":
            self.stacode = "32402"
            self.areacode = "000"
            self.groupcode = "21"
            self.precno = "32"
            self.blockno = "47582"
        if sta == "Sendai":
            self.stacode = "34392"
            self.areacode = "000"
            self.groupcode = "23"
            self.precno = "34"
            self.blockno = "47590"
        if sta == "Yamagata":
            self.stacode = "35426"
            self.areacode = "000"
            self.groupcode = "24"
            self.precno = "35"
            self.blockno = "47588"
        if sta == "Kumagaya":
            self.stacode = "43056"
            self.areacode = "000"
            self.groupcode = "29"
            self.precno = "43"
            self.blockno = "47626"
        if sta == "Tokyo":
            self.stacode = "44132"
            self.areacode = "000"
            self.groupcode = "30"
            self.precno = "44"
            self.blockno = "47662"
        if sta == "Yokohama":
            self.stacode = "46106"
            self.areacode = "000"
            self.groupcode = "32"
            self.precno = "46"
            self.blockno = "47670"
        if sta == "Nagoya":
            self.stacode = "51106"
            self.areacode = "000"
            self.groupcode = "36"
            self.precno = "51"
            self.blockno = "47636"
        if sta == "Niigata":
            self.stacode = "54232"
            self.areacode = "000"
            self.groupcode = "39"
            self.precno = "54"
            self.blockno = "47604"
        if sta == "Toyama":
            self.stacode = "55102"
            self.areacode = "000"
            self.groupcode = "40"
            self.precno = "55"
            self.blockno = "47607"
        if sta == "Kanazawa":
            self.stacode = "56227"
            self.areacode = "000"
            self.groupcode = "41"
            self.precno = "56"
            self.blockno = "47605"
        if sta == "Fukui":
            self.stacode = "57066"
            self.areacode = "000"
            self.groupcode = "42"
            self.precno = "57"
            self.blockno = "47616"
        if sta == "Kyoto":
            self.stacode = "61286"
            self.areacode = "000"
            self.groupcode = "44"
            self.precno = "61"
            self.blockno = "47759"
        if sta == "Osaka":
            self.stacode = "62078"
            self.areacode = "000"
            self.groupcode = "45"
            self.precno = "62"
            self.blockno = "47772"
        if sta == "Okayama":
            self.stacode = "66408"
            self.areacode = "000"
            self.groupcode = "49"
            self.precno = "66"
            self.blockno = "47768"
        if sta == "Hiroshima":
            self.stacode = "67437"
            self.areacode = "000"
            self.groupcode = "50"
            self.precno = "67"
            self.blockno = "47765"
        if sta == "Matsue":
            self.stacode = "68132"
            self.areacode = "000"
            self.groupcode = "51"
            self.precno = "68"
            self.blockno = "47741"
        if sta == "Fukuoka":
            self.stacode = "82182"
            self.areacode = "000"
            self.groupcode = "58"
            self.precno = "82"
            self.blockno = "47807"
        if sta == "Kagoshima":
            self.stacode = "88317"
            self.areacode = "000"
            self.groupcode = "64"
            self.precno = "88"
            self.blockno = "47827"

    def retrieve_mon(self, var):
        """月平均データの取得

        Parameters:
        ----------
        var: str
           変数名
        ----------
        Returns:
        ----------
        dat: pandas.DataFrame
            アメダス地点、変数名に対応するデータ
        ----------
        """
        url_top = "http://www.data.jma.go.jp/obd/stats/etrn/view/"
        filename = "monthly_s3.php"
        vno = ""
        uni = ""
        if var == "tave":
            vno = "a1"
            uni = "C"
        if var == "tmax":
            vno = "a2"
            uni = "C"
        if var == "tmin":
            vno = "a3"
            uni = "C"
        if var == "wind":
            vno = "a4"
            uni = "m/s"
        if var == "slp":
            vno = "a5"
            uni = "hPa"
        if var == "ps":
            vno = "a6"
            uni = "hPa"
        if var == "RH":
            vno = "a7"
            uni = "%"
        if var == "es":
            vno = "a8"
            uni = "hPa"
        if var == "ccover":
            vno = "a9"
            uni = ""
        if var == "sr":
            vno = "p2"
            uni = "%"
        if var == "sunf":
            vno = "p3"
            uni = "MJ/m2"
        if var == "sun":
            vno = "p4"
            uni = "h"
        if var == "prep":
            vno = "p5"
            uni = "mm"
        if var == "snowd":
            vno = "p5"
            uni = "cm"
        # monthly amedas
        url = url_top + filename + "?prec_no=" + self.precno + "&block_no=" + \
              self.blockno + "&year=&month=&day=&view=" + vno
        #print(url)
        # データの取り出し
        dataset = pd.io.html.read_html(url)
        dat = DataFrame(dataset[0], dtype=str)
        #
        # 欠損値の置き換え
        num_cols = len(dat.iloc[0])
        for i in range(num_cols):
            dat.iloc[:, i] = dat.iloc[:, i] \
                    .str.replace("×", "NaN", regex=False) \
                    .str.replace("--", "NaN", regex=False) \
                    .str.replace("///", "NaN", regex=False) \
                    .str.replace("]", "", regex=False) \
                    .str.replace(")", "", regex=False)
        # csv形式で書き出し再読み込み
        csv = dat.to_csv(index=False)
        col_names = ('jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug',
                     'sep', 'oct', 'nov', 'dec', 'ann')
        dat = pd.read_csv(StringIO(csv),
                          skiprows=[0, 1],
                          names=col_names,
                          index_col=[1])
        # 取り出したデータを返却
        return dat

    def retrieve_day(self, year, month):
        """日平均データの取得

        Parameters:
        ----------
        year: str or int
           年
        month: str or int
           月
        ----------
        Returns:
        ----------
        dat: pandas.DataFrame
            アメダス地点、年月に対応するデータ
        ----------
        """
        url_top = "http://www.data.jma.go.jp/obd/stats/etrn/view/"
        filename = "daily_s1.php"
        # daily amedas
        url = url_top + filename + "?prec_no=" + self.precno + "&block_no=" + \
            self.blockno + "&year=" + str(year) + \
            "&month=" + str(month) + "&day=&view="
        #print(url)
        # データの取り出し
        dataset = pd.io.html.read_html(url)
        dat = DataFrame(dataset[0], dtype=str)
        #
        # 欠損値の置き換え
        num_cols = len(dat.iloc[0])
        for i in range(num_cols - 5):
            dat.iloc[:, i] = dat.iloc[:, i] \
                    .str.replace("×", "NaN", regex=False) \
                    .str.replace("--", "NaN", regex=False) \
                    .str.replace("///", "NaN", regex=False) \
                    .str.replace("]", "", regex=False) \
                    .str.replace(")", "", regex=False)
        # csv形式で書き出し再読み込み
        csv = dat.to_csv(index=False)
        col_names = ('day', 'ps', 'slp', 'prep', 'pmax1h', 'pmax10m', 'tave',
                     'tmax', 'tmin', 'RH', 'RHmin', 'wind', 'wmax', 'wd',
                     'wsmax', 'wsd', 'sun', 'snow', 'snowd', 'wday', 'wnight')
        dat = pd.read_csv(StringIO(csv),
                          skiprows=[0, 1, 2, 3],
                          names=col_names,
                          index_col=[1])
        # 取り出したデータを返却
        return dat

    def retrieve_hour(self, year, month, day):
        """1時間毎のデータの取得

        Parameters:
        ----------
        year: str or int
           年
        month: str or int
           月
        day: str or int
           日
        ----------
        Returns:
        ----------
        dat: pandas.DataFrame
            アメダス地点、年月日に対応するデータ
        ----------
        """
        url_top = "https://www.data.jma.go.jp/obd/stats/etrn/view/"
        filename = "hourly_s1.php"
        # hourly amedas
        url = url_top + filename + "?prec_no=" + self.precno + "&block_no=" + \
              self.blockno + "&year=" + str(year) + "&month=" + str(month) + \
              "&day=" + str(day) + "&view="

        dataset = pd.io.html.read_html(url)
        dat = DataFrame(dataset[0], dtype=str)
        # 欠損値の置き換え
        num_cols = len(dat.iloc[0])
        for i in range(num_cols - 1):
            dat.iloc[:, i] = dat.iloc[:, i] \
                    .str.replace("×", "NaN", regex=False) \
                    .str.replace("--", "NaN", regex=False) \
                    .str.replace("///", "NaN", regex=False) \
                    .str.replace("]", "", regex=False) \
                    .str.replace(")", "", regex=False)
        # 風向の置き換え
        list_org = ["静穏", "北北東", "東北東", "東南東", "南南東", "南南西", "西南西", \
        "西北西", "北北西", "北東", "南東",  "南西",  "北西",  "北",  "東",   "南",    "西"]
        list_new = ["NaN",  "22.5",   "67.5",   "112.5",  "157.5",  "202.5",  "247.5", \
        "292.5",  "337.5",  "45.0", "135.0", "225.0", "315.0", "0.0", "90.0", "180.0", "270.0"]
        for i in range(17):
            dat.iloc[:, 9] = dat.iloc[:,
                                      9].str.replace(list_org[i], list_new[i])
        # csv形式で書き出し再読み込み
        csv = dat.to_csv(index=False)
        col_names = ('hour', 'ps', 'slp', 'prep', 'temp', 'dewt', 'psw', 'RH',
                     'ws', 'wd', 'sun', 'sunf', 'snow', 'snowd', 'wday',
                     'ccover', 'vis')
        dat = pd.read_csv(StringIO(csv), skiprows=[0, 1], names=col_names)
        # 取り出したデータを返却
        return dat

    def retrieve_stat(self, month=None):
        """統計データの取得（月最大24時間降水量）

        Parameters:
        ----------
        input_filename: int
            月（Noneの場合は通年）
        ----------
        Returns:
        ----------
        dict
            歴代1位の値を地点名をキーとした辞書で返す
        ----------
	"""
        url_top = "http://www.data.jma.go.jp/obd/stats/etrn/view/"
        filename = "rank_s.php"
        # 統計データ
        if month is None:
            url = url_top + filename + "?prec_no=" + self.precno + \
                  "&block_no=" + self.blockno + "&year=&month=&day=&view="
        else:
            url = url_top + filename + "?prec_no=" + self.precno + \
                  "&block_no=" + self.blockno + "&year=&month=" + \
                  str(month) + "&day=&view=h0"
        #print(url)
        # データの取り出し
        dataset = pd.io.html.read_html(url)
        dat = DataFrame(dataset[0], dtype=str)
        #
        if month is None:
            work = str(dat.iloc[4, 1])
        else:
            work = str(dat.iloc[3, 1])
        work = work.replace(")", "").split("(")
        return {self.sta: work}
