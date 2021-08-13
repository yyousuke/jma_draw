#
#  2021/06/11 Yamashita
#
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
from matplotlib.colors import ListedColormap
from .cutil import ColUtils


class val2col():
    """カラーマップの設定（グラデーション）

    Parameters:
    ----------
    tmin: float
        カラーマップの下限
    tmax: float
        カラーマップの上限
    tstep: float
        カラーマップのラベルを描く間隔
    cmap: str
        色テーブルの名前
    ----------
    """
    def __init__(self, tmin=0., tmax=20., tstep=2, cmap='jet'):
        self.tmin = tmin
        self.tmax = tmax
        self.tstep = tstep
        self.cmap = cmap
        try:
            self.cm = plt.get_cmap(self.cmap)
        except:
            cutils = ColUtils(cmap)  # 色テーブルの選択
            self.cm = cutils.get_ctable()  # 色テーブルの取得

    def conv(self, val):
        """データをカラーに変換

        Parameters:
        ----------
        val: float
            データ
        ----------
        Returns:
        ----------
        cmap
            カラーマップ
        ----------
        """
        n = (val - self.tmin) / (self.tmax - self.tmin) * self.cm.N
        n = max(min(n, self.cm.N), 0)
        return self.cm(int(n))

    def colorbar(self,
                 fig=None,
                 anchor=(0.35, 0.24),
                 size=(0.3, 0.02),
                 fmt="{f:.0f}",
                 label=True):
        """カラーバーを描く

        Parameters:
        ----------
        fig: matplotlib Figure
            プロット領域を作成した際の戻り値
        anchor: tuple(float, float)
            カラーバーの位置
        size: tuple(float, float)
            カラーバーの大きさ
        fmt: str
            カラーバーの目盛り線ラベルの書式
        label: bool
            カラーバーの目盛り線ラベルを描くかどうか
        ----------
        """
        if fig is None:
            raise Exception('fig is needed')
        ax = fig.add_axes(anchor + size)
        gradient = np.linspace(0, 1, self.cm.N)
        gradient_array = np.vstack((gradient, gradient))
        ticks = list()
        labels = list()
        ll = np.arange(self.tmin, self.tmax, self.tstep)
        for t in ll:
            ticks.append((t - self.tmin) / (self.tmax - self.tmin) * self.cm.N)
            if label:
                labels.append(fmt.format(f=t))
        # カラーバーを描く
        ax.imshow(gradient_array, aspect='auto', cmap=self.cm)
        ax.yaxis.set_major_locator(mticker.NullLocator())
        ax.yaxis.set_minor_locator(mticker.NullLocator())
        ax.set_xticks(ticks)
        if label:
            ax.set_xticklabels(labels)
        else:
            ax.xaxis.set_major_formatter(mticker.NullFormatter())
            ax.xaxis.set_minor_formatter(mticker.NullFormatter())
        #ax.set_axis_off()

    def clabel(self,
               fig=None,
               anchor=(0.34, 0.24),
               size=(0.1, 0.02),
               text=None,
               ha='right',
               va='bottom',
               fontsize=14):
        """カラーバーにラベルを付ける

        Parameters:
        ----------
        fig: matplotlib Figure
            プロット領域を作成した際の戻り値
        anchor: tuple(float, float)
            カラーバーラベルの位置
        size: tuple(float, float)
            カラーバーラベルの大きさ
        text: str
            カラーバーラベルに描く文字列
        ha: str
            カラーバーラベルの水平位置の揃え方
        va: str
            カラーバーラベルの鉛直位置の揃え方
        fontsize: int
            カラーバーラベルの文字サイズ
        ----------
        """
        if fig is None:
            raise Exception('fig is needed')
        ax = fig.add_axes(anchor + size)
        ax.text(0.0, 0.0, text, ha=ha, va=va, fontsize=fontsize)
        ax.set_axis_off()



class collevs():
    """カラーマップの設定（指定したレベル）

    Parameters:
    ----------
    clevs: list(float, float,,,)
        カラーマップの境の値
    tmax: list(float, float, float,,,)
        カラーマップの色
    ----------
    """

    def __init__(self, clevs=[], ccols=[]):
        self.clevs_min = clevs[0]
        self.clevs = clevs
        self.ccols = ccols
        if len(clevs) != len(ccols) + 1:
            print(len(clevs), len(ccols))
            raise ValueError('len(clevs) must be len(ccols)+1')

    def conv(self, val):
        """データをカラーに変換

        Parameters:
        ----------
        val: float
            データ
        ----------
        Returns:
        ----------
        cmap
            カラーマップ
        ----------
        """
        if val < float(self.clevs[0]):
            col = 'gray'
            #col = self.ccols[0]
        for n in np.arange(len(self.ccols)):
            if val >= float(self.clevs[n]) and val < float(self.clevs[n + 1]):
                col = self.ccols[n]
        return col

    def colorbar(self,
                 fig=None,
                 anchor=(0.35, 0.24),
                 size=(0.3, 0.02),
                 fontsize=11):
        """カラーバーを描く

        Parameters:
        ----------
        fig: matplotlib Figure
            プロット領域を作成した際の戻り値
        anchor: tuple(float, float)
            カラーバーの位置
        size: tuple(float, float)
            カラーバーの大きさ
        ----------
        """
        if fig is None:
            raise Exception('fig is needed')
        ax = fig.add_axes(anchor + size)
        gradient = np.linspace(0, 1, len(self.clevs) - 1)
        gradient_array = np.vstack((gradient, gradient))
        ticks = list()
        labels = list()
        ll = self.clevs[:-1]
        for n, t in enumerate(ll):
            ticks.append(n - 0.5)
            if t >= 1.:
                labels.append("{f:.0f}".format(f=t))
            else:
                labels.append("{f:.1f}".format(f=t))
        # カラーバーを描く
        cmap = ListedColormap(self.ccols)
        ax.imshow(gradient_array, aspect='auto', cmap=cmap)
        ax.yaxis.set_major_locator(mticker.NullLocator())
        ax.yaxis.set_minor_locator(mticker.NullLocator())
        ax.set_xticks(ticks)
        ax.set_xticklabels(labels, fontsize=fontsize)
        #ax.set_axis_off()
