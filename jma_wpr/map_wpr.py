#!/usr/bin/env python3
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib.dates as mdates
import matplotlib as mpl
import copy

# 地点
#sta_id = "47626"
#sta_name = "Kumagaya"
sta_id = "47636" # 名古屋 
sta_name = "Nagoya"
#sta_id = "47656" # 静岡
#sta_name = "Shizuoka"
# 入力ファイル名
input_file_u = "u_" + sta_id + ".csv"
input_file_v = "v_" + sta_id + ".csv"
input_file_w = "w_" + sta_id + ".csv"
# 出力ファイル名
output_filename = "wpr." + sta_name + ".png"
# タイトル
title = "2021/5/1 " + sta_name
#title = "2021/03/28-29 " + sta_name
#
# x軸の範囲
xmin = 121
xmax = 211
#xmin = None
#xmax = None
# y軸の範囲
ymin = 0
ymax = 8000

# ファイル読み込み
u = pd.read_csv(input_file_u, index_col=[0], parse_dates=[0])  # 東西風速
v = pd.read_csv(input_file_v, index_col=[0], parse_dates=[0])  # 南北風速
w = pd.read_csv(input_file_w, index_col=[0], parse_dates=[0])  # 鉛直速度
u = u.iloc[xmin:xmax, :]
v = v.iloc[xmin:xmax, :]
w = w.iloc[xmin:xmax, :]
# 時間ー高度面
time = w.index
height = np.array(w.columns, dtype=float) # 文字列として読み込まれたものを変換
# 時間ー高度面
#time = pd.read_csv('time.csv', header=None)
#height = pd.read_csv('height.csv', header=None, dtype=float) # 文字列として読み込まれたものを変換
print(time.shape)
print(height.shape)
# 品質管理情報を使い、欠損値、疑問値を除く
#wd = wd[qua == 0]
#ws = ws[qua == 0]
#w = np.array(w[qua == 0]).T
# x, y軸メッシュデータ
X, Y = np.meshgrid(time, height)
u = np.array(u).T
v = np.array(v).T
w = np.array(w).T
print(X.shape)
print(Y.shape)
print(u.shape)
#

# プロットエリアの定義
fig = plt.figure(figsize=(12, 5))
ax = fig.add_subplot(1, 1, 1)

# 矢羽を描く
ax.invert_xaxis() # 時間軸を右から左へ
ax.barbs(X.flatten(), Y.flatten(), u.flatten(), v.flatten(),
         sizes=dict(emptybarb=0.0), length=3.5,
         color='k', linewidth=0.8,
         zorder=2)
         #sizes=dict(emptybarb=0.0), length=2.5,
#plt.barbs(X.flatten()[::8], Y.flatten()[::8], u.flatten()[::8], v.flatten()[::8],
#          sizes=dict(emptybarb=0.0, width=0.1), length=4, color='k')
#plt.quiver(X.flatten(), Y.flatten(), u.flatten(), v.flatten())
ax.set_ylabel("Height (m)", fontsize=14)

# 鉛直速度を描く
#opt_scatter = True
opt_scatter = False
if opt_scatter: # 散布図のマーカー
    cmap = copy.copy(mpl.cm.get_cmap("coolwarm"))
    cs = ax.scatter(X.flatten(), Y.flatten(), c=w.flatten(),
                    marker='s', s=4,
                    vmin=-4, vmax=4,
                    cmap=cmap,
                    zorder=1)
else: # 陰影
    #cmap = copy.copy(mpl.cm.get_cmap("bwr"))
    cmap = copy.copy(mpl.cm.get_cmap("coolwarm"))
    cmap.set_over('r')
    cmap.set_under('b')
    cs = ax.contourf(X, Y, w, 
                    levels=[-4, -3, -2, -1, 0, 1, 2, 3, 4],
                    vmin=-4, vmax=4, 
                    cmap=cmap, extend='both',
                    corner_mask=False,
                    zorder=1)
# levels=[-4, -2, 0, 2, 4],
# カラーバー
cbar = fig.colorbar(cs, orientation='vertical')
cbar.set_label("Vertical velocity (m/s)", fontsize=12)

# y軸の範囲
ax.set_ylim([ymin, ymax])

# x軸の目盛り
#ax.xaxis.set_major_locator(ticker.AutoLocator())
#ax.xaxis.set_minor_locator(ticker.AutoMinorLocator())
ax.xaxis.set_major_locator(ticker.MultipleLocator(1 / 24))
#ax.xaxis.set_major_locator(ticker.MultipleLocator(1 / 8))
ax.xaxis.set_minor_locator(ticker.MultipleLocator(1 / 24))
ax.set_xticklabels(ax.get_xticklabels(), rotation=70, size="small")
ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d %HZ'))
#ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d %Hh'))
ax.xaxis.set_minor_formatter(ticker.NullFormatter())

# y軸の目盛り
ax.yaxis.set_major_locator(ticker.MultipleLocator(1000))
ax.yaxis.set_minor_locator(ticker.MultipleLocator(200))
#ax.yaxis.set_major_locator(ticker.AutoLocator())
#ax.yaxis.set_minor_locator(ticker.AutoMinorLocator())

# タイトル
ax.set_title(title, fontsize=20)

# プロット範囲の調整
plt.subplots_adjust(hspace=0.8, bottom=0.2)

# ファイルへの書き出し
plt.savefig(output_filename, dpi=300, bbox_inches='tight')
plt.show()
