import os
from collections import defaultdict
import pandas as pd
import numpy as np
from tqdm import tqdm
import matplotlib.pyplot as plt
import plotly.graph_objects as go

# TODO:グラフ関数を一般化すべき


class AssetSim():

    def __init__(self, return_distribution_dict, invest_plan, asset_plan,
                 initial_year, initial_cash, initial_invest_asset,
                 inflation_rate):
        """
        return_distributions:株式投資のリターン分布リスト{"sp500":sp500_return_distribution, "nasdaq":nasdaq_return_distribution}
        initial_year:開始年  
        initial_cash:初期現金資産
        initial_invest:初期投資資産
        initial_asset:初期資産  
        """
        self.return_distribution_dict = return_distribution_dict
        # 配列化
        self.return_distribution_detail = defaultdict(dict)
        for k, return_distribution in self.return_distribution_dict.items():
            self.return_distribution_detail[k]["indices"] = np.arange(
                len(return_distribution))
            self.return_distribution_detail[k]["share"] = return_distribution[
                'Share'].to_numpy()
            self.return_distribution_detail[k][
                "rate"] = return_distribution['rate'].to_numpy() / 100.0

        self.invest_plan = invest_plan
        self.asset_plan = asset_plan
        self.initial_year = initial_year
        self.initial_cash_asset = initial_cash
        self.initial_invest_asset = initial_invest_asset
        self.initial_total_asset = initial_cash + initial_invest_asset
        self.initial_inflation_rate = inflation_rate

        self.initialize()

    def initialize(self):
        """
        return_distribution以外を初期化する.  
        """
        self.year = self.initial_year
        self.cash_asset = self.initial_cash_asset
        self.invest_asset = self.initial_invest_asset
        self.total_asset = self.initial_total_asset
        self.inflation_rate = self.initial_inflation_rate

    def get_multi_role_play_assets(self, n: int):
        """
        n回ロールプレイをして各年の資産シミュレーションをn列作成
        """
        self.n = n
        all_assets_by_year = pd.DataFrame()
        all_life_assets_list = []
        for i in tqdm(range(n)):
            a_life_assets_dict = self.get_role_play_assets()
            # 初めてDataFrameを作成するときに年の情報をインデックスとして追加
            if i == 0:
                all_assets_by_year['year'] = a_life_assets_dict['years']
            # 各年の資産額をDataFrameに追加 (列名は試行回数)
            all_life_assets_list.append(a_life_assets_dict['assets'])
        # 辞書にまとめておく
        sim_columns = {
            f'simulation_{i+1}': simulation_data
            for i, simulation_data in enumerate(all_life_assets_list)
        }
        all_assets_by_year = pd.concat(
            [all_assets_by_year, pd.DataFrame(sim_columns)],
            axis=1,
            join="outer")
        all_assets_by_year = all_assets_by_year.set_index('year')
        self.all_assets_by_year = all_assets_by_year

    def get_all_assets_by_year(self):
        return self.all_assets_by_year

    def get_achive_ratio(self, asset_threshold):
        """
        各年で資産がasset_thresholdを超える確率を計算
        """
        achievement_counts = (self.all_assets_by_year.iloc[:, 1:]
                              >= asset_threshold).sum(axis=1)

        # 達成率を計算 (達成回数 / シミュレーション総数)
        achievement_ratio = achievement_counts / self.n

        self.achieve_ratio_df = pd.DataFrame(achievement_ratio,
                                             columns=["achieve_ratio"
                                                      ]).reset_index()

    def plot_multi_role_play_assets(self, asset_threshold, year: int):
        """
        複数のシミュレーション結果をまとめたDataFrameを描画する。
        """
        self.plot_asset_distribution(year, is_show=True)
        self.plot_achive_ratio(asset_threshold, is_show=True)

    def get_role_play_assets(self):
        """
        1年分の資産シミュレーションを行う
        - asset_plan: 資産計画
        """
        self.initialize()

        # income, cost, saving_per_year, invest_per_year = 10000000, 8000000, 500000, 1500000
        years = []
        cash_assets = []
        invest_assets = []
        total_assets = []
        profits = []
        rates = []

        for asset_plan_value, invest_plan_a_year in zip(
                self.asset_plan.values(), self.invest_plan.values()):
            cost = asset_plan_value[0]
            income = asset_plan_value[1]
            saving_per_year = asset_plan_value[2]
            invest_per_year = asset_plan_value[3]

            self.cash_asset, self.invest_asset, self.total_asset = self.update_assets_one_year(
                cost, income, saving_per_year, invest_per_year,
                invest_plan_a_year)

            years.append(self.year)
            cash_assets.append(self.cash_asset)
            invest_assets.append(self.invest_asset)
            total_assets.append(self.total_asset)
            profits.append(self.invest_profit_a_year)
            rates.append(self.rate_a_year)

        a_life_assets_dict = {
            "years": years,
            "cash": cash_assets,
            "invest": invest_assets,
            "assets": total_assets,
            "profits": profits,
            "rates": rates
        }
        self.a_life_assets_dict = a_life_assets_dict
        return a_life_assets_dict

    def get_role_play_asset_result_df(self):
        return pd.DataFrame(self.a_life_assets_dict)

    def plot_role_play_assets(self,
                              save_name: str = None,
                              is_show: bool = True,
                              mode: str = "matplotlib"):
        """
        1年分の資産シミュレーション結果を描画
        """
        result = pd.DataFrame(self.a_life_assets_dict)
        if mode == "matplotlib":
            fig, ax1 = plt.subplots(figsize=(10, 10))
            ax1.plot(result['years'],
                     result['assets'],
                     color='blue',
                     label='assets')
            ax1.plot(result['years'],
                     result['invest'],
                     color='black',
                     label='total_invests')
            ax1.plot(result['years'],
                     result['cash'],
                     color='green',
                     label='cash')

            ax1.set_xlabel('years')
            ax1.set_ylabel('assets / invest / cash')
            ax1.tick_params(axis='y')

            # ax2（右側y軸）作成
            ax2 = ax1.twinx()
            ax2.plot(result['years'],
                     result['profits'],
                     color='red',
                     label='profits')
            ax2.set_ylabel('profits', color='red')
            ax2.tick_params(axis='y', labelcolor='red')

            plt.title('Assets and Profits Over Years')

            # 凡例を一つにまとめる
            lines_1, labels_1 = ax1.get_legend_handles_labels()
            lines_2, labels_2 = ax2.get_legend_handles_labels()
            ax1.legend(lines_1 + lines_2, labels_1 + labels_2, loc='best')

            if is_show:
                plt.show()
            if save_name:
                plt.savefig(save_name + ".png")
            plt.clf()
            plt.close()
        elif mode == "plotly":
            fig = go.Figure()

            # assets, invest, cash（左y軸）
            fig.add_trace(
                go.Scatter(x=result['years'],
                           y=result['assets'],
                           mode='lines',
                           name='assets',
                           line=dict(color='blue')))
            fig.add_trace(
                go.Scatter(x=result['years'],
                           y=result['invest'],
                           mode='lines',
                           name='total_invests',
                           line=dict(color='black')))
            fig.add_trace(
                go.Scatter(x=result['years'],
                           y=result['cash'],
                           mode='lines',
                           name='cash',
                           line=dict(color='green')))

            # profits（右y軸）
            fig.add_trace(
                go.Scatter(x=result['years'],
                           y=result['profits'],
                           mode='lines',
                           name='profits',
                           line=dict(color='red'),
                           yaxis='y2'))

            # レイアウト設定
            fig.update_layout(
                title='Assets and Profits Over Years',
                xaxis=dict(title='years'),
                yaxis=dict(title='assets / invest / cash', side='left'),
                yaxis2=dict(title='profits', overlaying='y', side='right'),
                legend=dict(x=0, y=1.1, orientation='h'),
                width=900,  # 幅（ピクセル）
                height=700,
            )

            if is_show:
                fig.show()

            if save_name:
                # save_nameはhtml推奨（静的画像は別途設定必要）
                fig.write_html(save_name + ".html")

    def update_assets_one_year(self, cost, income, saving_per_year,
                               invest_per_year, invest_plan_a_year):
        """
        一年経過時の資産額を返す
        """
        # 一年経過
        self.year += 1

        # インフレを加味した支出
        inflation_coeff = self.inflation_rate**(self.year - self.initial_year)
        cost = cost * inflation_coeff

        # cashが尽きたらinvestを取り崩し
        if self.cash_asset <= 0:
            if (invest_asset_tmp :=
                (self.invest_asset + self.cash_asset)) >= 0:
                self.invest_asset = invest_asset_tmp
                self.cash_asset = 0
            else:
                self.cash_asset = invest_asset_tmp
                self.invest_asset = 0

        # 投資の年利を反映
        self.invest_profit_a_year, self.rate_a_year = self._get_profit_a_year(
            invest_plan_a_year)
        self.invest_asset += self.invest_profit_a_year

        # 収入と支出の差分
        raw_profit = income - cost

        # 運用・貯金
        if raw_profit <= saving_per_year:  #残金の貯金(赤字も貯金方式)
            self.cash_asset += raw_profit
        elif raw_profit > saving_per_year and raw_profit <= invest_per_year + saving_per_year:  # 満額貯金・余剰投資
            self.cash_asset += saving_per_year
            self.invest_asset += raw_profit - saving_per_year
        elif raw_profit > invest_per_year + saving_per_year:  # 満額貯金・満額投資・余剰金の貯金
            self.cash_asset += raw_profit - invest_per_year
            self.invest_asset += invest_per_year

        # その年の資産額を返す
        self.total_asset = self.cash_asset + self.invest_asset

        return self.cash_asset, self.invest_asset, self.total_asset

    def _get_profit_a_year(self, invest_plan_a_year):
        """
        資産(asset)が株式利益分布(return_distribution)に従って  
        ある年に増える利益(profit)、選ばれた利益率(rate)を返す。  
        """
        #TODO:invest_plan_a_year,self.return_distribution_detail[k]["rate"]のそれぞれの値の
        # 各種比率がそれぞれでトータルで1になるよう補正するように変更(今はトータル1になることを前提にしている)
        profits = []
        rate_list = []
        for k, v in invest_plan_a_year.items():
            # 計算用の配列
            indices = self.return_distribution_detail[k]["indices"]
            share = self.return_distribution_detail[k]["share"]
            rates = self.return_distribution_detail[k]["rate"]
            # 利益率をshareの確率に従い選ぶ
            idx = np.random.choice(indices, p=share)
            rate = rates[idx]
            rate_list.append(rate)
            # 利益を計算
            invest = self.invest_asset * v
            profit = invest * rate
            profits.append(profit)
        # 合算
        invest_profit_a_year = sum(profits)
        rate_a_year = sum(
            [k * v for k, v in zip(rate_list, invest_plan_a_year.values())])
        return invest_profit_a_year, rate_a_year

    def plot_asset_distribution(
        self,
        year: int,
        save_name: str = None,
        is_show: bool = True,
        mode: str = "matplotlib",
    ):
        """
        指定した年の各シミュレーションにおける資産額の分布をヒストグラムで表示する。

        Args:
            data: 各シミュレーションの資産額をまとめたDataFrame (indexが年)。
            year: 資産分布を表示したい年。
        """
        data = self.all_assets_by_year
        if year in data.index:
            assets_at_year = data.loc[year]
            # 年の列を除外して資産額のみを取得
            assets_values = assets_at_year.drop(index=assets_at_year.index[
                assets_at_year.index.isin(['year'])])
            if mode == "matplotlib":
                plt.figure(figsize=(10, 6))
                plt.hist(assets_values, bins=20, edgecolor='black')
                plt.title(f"{year}y assets distribution")
                plt.xlabel('assets')
                plt.ylabel('frequency')
                plt.grid(axis='y', alpha=0.75)
                if is_show:
                    plt.show()
                if save_name:
                    plt.savefig(save_name + ".png")
                plt.clf()
                plt.close()
            elif mode == "plotly":
                fig = go.Figure(
                    data=[go.Histogram(x=assets_values, nbinsx=50)])
                fig.update_layout(title=f"{year}y assets distribution",
                                  xaxis_title='assets',
                                  yaxis_title='frequency',
                                  bargap=0.1,
                                  width=900,
                                  height=700)
                if is_show:
                    fig.show()
                if save_name:
                    fig.write_html(save_name + ".html")  # HTML保存が無難です
        else:
            print(f"データに{year}年が見つかりません。")

    def plot_achive_ratio(
        self,
        asset_threshold,
        save_name: str = None,
        is_show: bool = True,
        mode: str = "matplotlib",
    ):
        """
        各年で資産がasset_thresholdを超えたシミュレーションの数を計算
        all_assets_by_year: 資産分布をまとめたDataFrame (indexが年)
        asset_threshold: 資産額の閾値
        n: シミュレーション総数
        """
        self.get_achive_ratio(asset_threshold)

        if mode == "matplotlib":
            fig = plt.figure(figsize=(10, 6))
            plt.plot(self.achieve_ratio_df["year"],
                     self.achieve_ratio_df['achieve_ratio'])
            plt.xlabel('year')
            plt.ylabel('achieve_ratio')
            plt.title(f"achieve_ratio {asset_threshold} over years")
            if is_show:
                plt.show()
            if save_name:
                fig.savefig(save_name + ".png")
            plt.clf()
            plt.close()
        elif mode == "plotly":
            fig = go.Figure()
            fig.add_trace(
                go.Scatter(x=self.achieve_ratio_df["year"],
                           y=self.achieve_ratio_df['achieve_ratio'],
                           mode='lines',
                           name='achieve_ratio'))
            fig.update_layout(
                title=f"achieve_ratio {asset_threshold} over years",
                xaxis_title='year',
                yaxis_title='achieve_ratio',
                width=900,
                height=700)
            if is_show:
                fig.show()
            if save_name:
                fig.write_html(save_name + ".html")  # HTML形式で保存

    def get_asset_transition(self, achieve_percents: list = [10, 90, 99]):
        """
        achieve_ratiosの確率で超える資産額推移
        """
        #各年(各行)の資産額を昇順にしてまとめてachieve_ratioの番目の数値を取得する
        self.asset_transition_df = pd.DataFrame()
        for achieve_percent in achieve_percents:
            achieve_ratios = 1 - achieve_percent / 100
            self.asset_transition_df[
                f"achieve_ratio_{achieve_percent}"] = self.all_assets_by_year.iloc[:, 1:].quantile(
                    achieve_ratios, axis=1, interpolation='linear')

    def plot_asset_transition(
        self,
        achieve_percents: list = [50, 90, 99],
        save_name: str = None,
        is_show: bool = True,
        mode: str = "matplotlib",
    ):
        """
        achieve_ratiosの確率で超える資産額推移を描画

        Parameters
        ----------
        achieve_percents : list, optional
            achieve_ratiosの確率(%)を指定, by default [50, 90, 99]
        save_name : str, optional
            保存するファイル名, by default None
        is_show : bool, optional
            描画結果を表示するか否か, by default True
        """
        self.get_asset_transition(achieve_percents)
        df = self.asset_transition_df.reset_index()

        if mode == "matplotlib":
            # Create a figure
            fig = plt.figure(figsize=(10, 6))

            for achieve_percent in achieve_percents:
                plt.plot(df["year"],
                         df[f"achieve_ratio_{achieve_percent}"],
                         label=f"{achieve_percent}%")
            plt.xlabel('year')
            plt.ylabel('assets')
            plt.title('assets over years')
            plt.legend()
            if is_show:
                plt.show()
            if save_name:
                fig.savefig(save_name + ".png")
            plt.clf()
            plt.close()
        elif mode == "plotly":
            fig = go.Figure()
            for achieve_percent in achieve_percents:
                fig.add_trace(
                    go.Scatter(x=df["year"],
                               y=df[f"achieve_ratio_{achieve_percent}"],
                               mode='lines',
                               name=f"{achieve_percent}%"))
            fig.update_layout(title='assets over years',
                              xaxis_title='year',
                              yaxis_title='assets',
                              legend=dict(orientation='h', y=1.1),
                              width=900,
                              height=700)
            if is_show:
                fig.show()
            if save_name:
                fig.write_html(save_name + ".html")  # HTML保存推奨

    def get_crash_ratio(self):
        """
        破産する確率
        """
        asset_threshold = 0
        self.get_achive_ratio(asset_threshold)
        crash_ratio_df = self.achieve_ratio_df
        crash_ratio_df["crash_ratio"] = 1 - crash_ratio_df["achieve_ratio"]
        return crash_ratio_df

    def plot_crash_ratio(self,
                         save_name: str = None,
                         is_show: bool = True,
                         mode: str = "matplotlib"):
        """
        破産する確率を描画
        """

        self.crash_ratio_df = self.get_crash_ratio()

        if mode == "matplotlib":
            fig = plt.figure(figsize=(10, 6))
            plt.plot(self.crash_ratio_df["year"],
                     self.crash_ratio_df['crash_ratio'])
            plt.xlabel('year')
            plt.ylabel('crash_ratio')
            plt.title('crash_ratio over years')
            if is_show:
                plt.show()
            if save_name:
                fig.savefig(save_name + ".png")
            plt.clf()
            plt.close()
        elif mode == "plotly":
            fig = go.Figure()
            fig.add_trace(
                go.Scatter(x=self.crash_ratio_df["year"],
                           y=self.crash_ratio_df['crash_ratio'],
                           mode='lines',
                           name='crash_ratio'))
            fig.update_layout(title='crash_ratio over years',
                              xaxis_title='year',
                              yaxis_title='crash_ratio',
                              width=900,
                              height=700)
            if is_show:
                fig.show()
            if save_name:
                fig.write_html(save_name + ".html")  # HTML形式で保存


def single_life_example():

    # 支出データ読み込み
    from input_generator import InputGenerator
    # from asset.input_generator import InputGenerator
    import glob
    import pandas as pd
    maindir = glob.glob("01_*/output/01_*")[0]
    database_dir = glob.glob("01_*/database")[0]
    IG = InputGenerator()
    # 支出データ読み込み
    asset_csv_in = f"{maindir}/asset_plan.csv"
    invest_csv_in = f"{maindir}/invest_plan.csv"
    _, asset_plan, invest_plan = IG.get_asset_plan(invest_csv_in, asset_csv_in)
    print(f"asset_plan[0]:\n{asset_plan[0]}\n")
    print(f"invest_plan[0]:\n{invest_plan[0]}")

    #株価利益分布
    invest_names = ["sp500", "nasdaq"]
    return_distribution_dict = {
        k: pd.read_csv(f"{database_dir}/{k}.csv")
        for k in invest_names
    }
    return_distribution_dict

    #実行
    initial_year = 2025
    initial_cash = 2500000
    initial_invest_asset = 0
    initial_invest_asset = 9500000
    AS = AssetSim(return_distribution_dict, invest_plan, asset_plan,
                  initial_year, initial_cash, initial_invest_asset)

    AS.get_role_play_assets()
    AS.plot_role_play_assets(is_show=True, mode="matplotlib")


def multi_life_example():

    # 支出データ読み込み
    # from asset.input_generator import InputGenerator
    from input_generator import InputGenerator
    import glob
    import pandas as pd
    maindir = glob.glob("01_*")[0]
    IG = InputGenerator()
    # 支出データ読み込み
    asset_csv_in = f"{maindir}/asset_plan.csv"
    invest_csv_in = f"{maindir}/invest_plan.csv"
    _, asset_plan, invest_plan = IG.get_asset_plan(asset_csv_in, invest_csv_in)
    print(f"asset_plan[0]:\n{asset_plan[0]}\n")
    print(f"invest_plan[0]:\n{invest_plan[0]}")

    #株価利益分布
    invest_names = ["sp500", "nasdaq"]
    return_distribution_dict = {
        k: pd.read_csv(f"{maindir}/{k}.csv")
        for k in invest_names
    }
    return_distribution_dict

    #実行
    # initial_year = 2025
    # initial_cash = 2500000
    # initial_invest_asset = 9500000
    initial_year = 2025
    initial_cash = 2500000
    initial_invest_asset = 0
    n = 1000
    achieve_percents = [70, 80, 90, 95, 99]

    AS = AssetSim(return_distribution_dict, invest_plan, asset_plan,
                  initial_year, initial_cash, initial_invest_asset)

    AS.get_multi_role_play_assets(n)
    AS.plot_multi_role_play_assets(asset_threshold=50000000, year=2040)
    AS.plot_asset_transition(achieve_percents)
    AS.plot_crash_ratio()


if __name__ == "__main__":
    pass
    single_life_example()
    # multi_life_example()
