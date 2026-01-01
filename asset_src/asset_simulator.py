import os, sys
import numpy as np
import pandas as pd
from IPython.display import display
import plotly.graph_objects as go

# from asset.asset_src.assetsim import AssetSim
# from asset.asset_src.input_generator import InputGenerator
# from asset.asset_src.tbase_for_asset import Base_class

from assetsim import AssetSim
from input_generator import InputGenerator
from tbase_for_asset import Base_class


class AssetSimulator(Base_class):
    """
    資産シミュレーター
    - js_in  
        - 
    """

    def __init__(self, js_in):
        super().__init__(js_in)

    def _read_asset_plan(self):
        IG = InputGenerator()
        # 支出データ読み込み
        self.asset_plan_df, self.asset_plan, self.invest_plan_df, self.invest_plan = IG.get_asset_plan(
            self.asset_plan_in)
        self.stock_list = self.invest_plan_df.columns

    def _read_return_distribution(self):
        self.return_distribution_dict = {
            k: pd.read_csv(f"{self.sock_database_path}/{k}.csv")
            for k in self.stock_list
        }

    def _cal_main(self):
        AS_cond = {
            "return_distribution_dict": self.return_distribution_dict,
            "invest_plan": self.invest_plan,
            "asset_plan": self.asset_plan,
            "initial_year": self.initial_year,
            "initial_cash": self.initial_cash,
            "initial_invest_asset": self.initial_invest_asset,
            "inflation_rate": self.inflation_rate
        }
        AS = AssetSim(**AS_cond)

        # 一回の人生を計算
        if self.single_life_mode:
            AS.get_role_play_assets()
            AS.plot_role_play_assets(
                save_name=f"{self.output_dir}/one_life_asset",
                is_show=self.is_show,
                mode=self.fig_mode)

        # number_of_lifeの人生を計算
        if self.multi_life_mode:
            AS.get_multi_role_play_assets(self.number_of_life)
            for check_year in self.check_years:
                AS.plot_asset_distribution(
                    check_year,
                    save_name=
                    f"{self.output_dir}/asset_distribution_in_{check_year}y",
                    is_show=self.is_show,
                    mode=self.fig_mode)
            AS.plot_achive_ratio(
                self.asset_threshold,
                save_name=
                f"{self.output_dir}/achive_ratio_{self.asset_threshold}",
                is_show=self.is_show,
                mode=self.fig_mode)
            achieve_percents_name = "_".join(
                [str(x) for x in self.achieve_percents])
            AS.plot_asset_transition(
                self.achieve_percents,
                save_name=
                f"{self.output_dir}/asset_transition_{achieve_percents_name}",
                is_show=self.is_show,
                mode=self.fig_mode)
            AS.plot_crash_ratio(save_name=f"{self.output_dir}/crash_ratio",
                                is_show=self.is_show,
                                mode=self.fig_mode)

    def cal_asset(self):
        self._read_asset_plan()
        self._read_return_distribution()
        self._cal_main()

    def check_plan(self, is_show: bool = False):
        self._read_asset_plan()
        result = self.asset_plan_df
        years_df = pd.DataFrame(
            {"years": [self.initial_year + i for i in range(len(result))]})
        result = pd.concat([years_df, result], axis=1, join='outer')
        fig = go.Figure()
        # assets, invest, cash（左y軸）
        fig.add_trace(
            go.Scatter(x=result['years'],
                       y=result['income'],
                       mode='lines',
                       name='income',
                       line=dict(color='blue')))
        fig.add_trace(
            go.Scatter(x=result['years'],
                       y=result['saving_per_year'],
                       mode='lines',
                       name='saving_per_year',
                       line=dict(color='black')))
        fig.add_trace(
            go.Scatter(x=result['years'],
                       y=result['invest_per_year'],
                       mode='lines',
                       name='invest_per_year',
                       line=dict(color='green')))
        fig.add_trace(
            go.Scatter(x=result['years'],
                       y=result['outcome'],
                       mode='lines',
                       name='outcome',
                       line=dict(color='red')))

        # レイアウト設定
        fig.update_layout(
            title='asset plan',
            xaxis=dict(title='years'),
            yaxis=dict(
                title='income / saving_per_year / invest_per_year / outcome',
                side='left'),
            yaxis2=dict(title='profits', overlaying='y', side='right'),
            legend=dict(x=0, y=1.1, orientation='h'),
            width=900,  # 幅（ピクセル）
            height=700,
        )

        if is_show:
            fig.show()

        # if save_name:
        fig.write_html(f"{self.output_dir}/check_plan" + ".html")


if __name__ == "__main__":
    import glob
    from tbase import save_dict_as_json

    maindir = glob.glob("01_*")[0]
    cond = {
        "output_dir": "<asset_path>/asset",
        "asset_plan_in": "<asset_path>/asset/asset_plan.csv",
        "sock_database_path": "01_assets/database",
        "stock_list": ["sp500", "nasdaq"],
        "fig_mode": "matplotlib",
        "is_show": False,
        "single_life_mode": True,
        "initial_year": 2025,
        "initial_cash": 2500000,
        "initial_invest_asset": 0,
        "multi_life_mode": True,
        "number_of_life": 1000,
        "check_years": [2050],
        "asset_threshold": 50000000,
        "achieve_percents": [70, 80, 90, 95, 99]
    }
    os.makedirs(cond["output_dir"], exist_ok=True)
    out_dir = cond["output_dir"]
    js_in = f"{out_dir}/condition.json"
    save_dict_as_json(cond, js_in)
    AS = AssetSimulator(js_in)
    AS.cal_asset()
