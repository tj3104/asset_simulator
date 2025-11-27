import os, glob, sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm


def monthly_to_annual_returns(monthly_return_rates, bins=100):
    """
    return_ratesからhistの頻度に従った確率である月リターン率を計算する。
    それを12回繰り返して年次の利益率を計算
    それを10000回行って年間のreturnsの頻度と利益率の分布データを得る
    ヒストグラムの頻度から確率分布を作成
    ヒストグラム（bin=20）で分布データを作成
    """
    monthly_return_rates = monthly_return_rates / 100  # パーセントから小数に変換
    hist, bin_edges = np.histogram(monthly_return_rates, bins)
    monthly_prob = hist / np.sum(hist)
    monthly_return_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
    annual_return_rates = []
    num_trials = 10000
    months_per_year = 12

    for _ in tqdm(range(num_trials)):
        # 12ヶ月分の月次リターンをヒストグラムの確率分布からサンプリング
        sampled_monthly_return_rates = np.random.choice(monthly_return_centers,
                                                        size=months_per_year,
                                                        p=monthly_prob)
        # 年次リターンを計算（複利計算）
        annual_return_rate = (np.prod(1 + sampled_monthly_return_rates) -
                              1) * 100  # 年率に変換
        annual_return_rates.append(annual_return_rate)
    return annual_return_rates


def get_annual_return_distribution(macrotrends_dir,
                                   database_dir,
                                   name,
                                   bins=100,
                                   monthly_histogram=True,
                                   annual_histogram=True):
    """
    macrotrends_dir: Macrotrendsのデータが保存されているディレクトリ
    database_dir: 結果を保存するディレクトリ
    name: データの名前（例: "SP500"）
    bins: ヒストグラムのビン数
    monthly_histogram: 月次リターンのヒストグラムを表示するかどうか
    annual_histogram: 年次リターンのヒストグラムを表示するかどうか
    """
    df = pd.read_csv(f"{macrotrends_dir}/{name}.csv")
    monthly_data = df["Value"].to_list()
    # 各月の利益率（リターン）を計算
    monthly_data = np.array(monthly_data)
    monthly_returns_rate = 100 * (monthly_data[1:] -
                                  monthly_data[:-1]) / monthly_data[:-1]

    annual_return_rates = monthly_to_annual_returns(monthly_returns_rate, bins)

    annual_hist, bin_edges = np.histogram(annual_return_rates, bins)
    annual_return_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
    annual_prob = annual_hist / np.sum(annual_hist)

    result_df = pd.DataFrame({
        "rate": annual_return_centers,
        "Share": annual_prob
    })
    # Shareが0の行を削除
    result_df = result_df[result_df["Share"] > 0]
    result_df.to_csv(f"{database_dir}/{name}_macrotrends.csv", index=False)

    # ヒストグラムを表示（必要なら）
    if monthly_histogram:
        plt.hist(monthly_returns_rate, bins)
        plt.xlabel("Monthly Return")
        plt.ylabel("Frequency")
        plt.title("Distribution of Monthly Returns")
        plt.show()
        plt.clf()
        plt.close()

    if annual_histogram:
        plt.hist(annual_return_rates, bins)
        plt.xlabel("Annual Return")
        plt.ylabel("Frequency")
        plt.title("Distribution of Simulated Annual Returns")
        plt.show()
        plt.clf()
        plt.close()


def m2y_example():
    maindir = os.path.dirname(os.path.abspath(__file__))
    macrotrends_dir = glob.glob(f"{maindir}/macrotrends_m")[0]
    database_dir_ = glob.glob(f"{maindir}/database")[0]

    # names = ["SP500", "NASDAQ", "DowJones", "Nikkei225"]
    names = ["Nikkei225"]
    bins = 50
    for name in names:
        print(f"Processing {name}...")
        get_annual_return_distribution(macrotrends_dir,
                                       database_dir_,
                                       name,
                                       bins,
                                       monthly_histogram=False,
                                       annual_histogram=True)


def d2m(input_path, output_path, name):
    """
    - description:
        日足のデータを月足のデータに変換する
    """
    # 日足のデータを読み込む
    df = pd.read_csv(f"{input_path}/{name}.csv")
    date = pd.to_datetime(df["Date"])
    # 同じ月のデータはその月の最初のデータ行を採用する
    month_starts = date.dt.to_period("M").drop_duplicates().index
    df_monthly = df.loc[month_starts].reset_index(drop=True)
    # 月足データを保存する
    df_monthly.to_csv(f"{output_path}/{name}.csv", index=False)


def d2m_example():
    maindir = os.path.dirname(os.path.abspath(__file__))
    input_path = f"{maindir}/macrotrends_d"
    output_path = f"{maindir}/macrotrends_m"
    names = ["Nikkei225"]
    for name in names:
        d2m(input_path, output_path, name)


def detail2d(input_path, output_path, name):
    """
    - description:
        詳細日足データを日足データに変換する
    """
    # 詳細日足のデータを読み込む
    df = pd.read_csv(f"{input_path}/{name}.csv")
    # dateとvolume列を抽出する
    df_daily = df.loc[:, ["date", "volume"]]
    df_daily.columns = ["Date", "Value"]
    # 日足データを保存する
    df_daily.to_csv(f"{output_path}/{name}.csv", index=False)


def detail2d_example():
    """
    detailデータをdailyに変換する例
    """
    maindir = os.path.dirname(os.path.abspath(__file__))
    input_path = f"{maindir}/macrotrends_detail"
    output_path = f"{maindir}/macrotrends_d"
    names = ["TSLA", "NVDA"]
    for name in names:
        detail2d(input_path, output_path, name)


if __name__ == "__main__":
    # m2y_example()
    # d2m_example()
    # detail2d_example()
    pass
