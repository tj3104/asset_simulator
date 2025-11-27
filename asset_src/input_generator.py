# import ipysheet
import pandas as pd
from IPython.display import display


class InputGenerator:

    def __init__(self):
        pass

    def _get_plan_csv(self, csv_in):
        df = pd.read_csv(csv_in, dtype='float64', thousands=",")
        df = df.fillna(0)
        return df

    # def get_input_data_from_sheet(self, rows=5, cols=3):
    #     """
    #     Jupyter Notebook上でExcel風の入力欄を作成。
    #     1行目を列名として使用し、空欄列名は列ごと削除。
    #     入力のない行・列は削除し、残った空欄は0に変換。
    #     """
    #     sheet = ipysheet.sheet(rows=rows, columns=cols)

    #     # 入力用データ（全セル空欄で初期化）
    #     data = [["" for _ in range(cols)] for _ in range(rows)]
    #     self.data_range = ipysheet.cell_range(data,
    #                                           row_start=0,
    #                                           column_start=0)

    #     display(sheet)

    # def get_df(self):
    #     values = pd.DataFrame(self.data_range.value,
    #                           dtype='float64',
    #                           thousands=",")
    #     if values.empty:
    #         return pd.DataFrame()

    #     # 1行目を列名に設定
    #     col_names = values.iloc[0]

    #     # 列名が空欄の列を除外
    #     valid_cols = [
    #         i for i, name in enumerate(col_names) if str(name).strip() != ""
    #     ]
    #     df = values.iloc[1:, valid_cols].copy()
    #     df.columns = col_names[valid_cols]

    #     # 行削除処理（全セルが空欄 or NaN の行）
    #     df = df.replace("", pd.NA)  # 空文字をNaN扱い
    #     df = df.dropna(axis=0, how="all")

    #     # 残った空欄を0に変換
    #     self.df = df.fillna(0)

    #     return self.df

    def _get_total_outcome(self):
        """
        ipysheet上のデータを、pandas.DataFrame形式で取得し、
        全行の合計値を算出して、pandas.Series形式で返す。

        Returns
        -------
        total_outcome: pandas.Series
            ipysheet上のデータの全行の合計値。
        """
        total_outcome = pd.DataFrame()
        total_outcome[
            "outcome"] = self.asset_plan_ini_df.iloc[:,
                                                     self.other_fin_idx:].sum(
                                                         axis=1)
        return total_outcome

    def get_asset_plan(self, asset_csv_in):
        # 入力データをpandas.DataFrame形式で取得
        self.asset_plan_ini_df = self._get_plan_csv(asset_csv_in)
        # データ分割に使うidxの取得
        cols = self.asset_plan_ini_df.columns.to_list()
        self.asset_plan_ini_idx = cols.index("year") + 1
        self.other_fin_idx = self.asset_plan_ini_idx + 3
        self.invest_fin_idx = cols.index("age") - 1

        # asset_planを作成
        other_df = self.asset_plan_ini_df.iloc[:, self.asset_plan_ini_idx:self.
                                               other_fin_idx]
        total_outcome = self._get_total_outcome()
        asset_plan_df = pd.concat([total_outcome, other_df],
                                  axis=1,
                                  join="outer")
        asset_plan = {k: v.to_numpy() for k, v in asset_plan_df.T.items()}

        # invest_planを作成
        self.invest_plan_ini_df = self.asset_plan_ini_df.iloc[:, :self.
                                                              invest_fin_idx]
        invest_plan = {
            k: {
                stock: ratio
                for stock, ratio in zip(v.index, v.values)
            }
            for k, v in self.invest_plan_ini_df.T.items()
        }
        # invest_plan = dict(self.invest_plan_ini_df.T)
        return asset_plan_df, asset_plan, self.invest_plan_ini_df, invest_plan


if __name__ == "__main__":
    import glob
    IG = InputGenerator()
    maindir = glob.glob("01_*")[0]
    # 支出データ読み込み
    asset_csv_in = f"{maindir}/asset_plan.csv"
    invest_csv_in = f"{maindir}/invest_plan.csv"
    asset_plan_df, asset_plan = IG.get_asset_plan(asset_csv_in, invest_csv_in)
    asset_plan_df
