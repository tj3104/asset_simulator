import os, sys, glob

sys.path.append(f"{os.path.dirname(__file__)}/asset_src")

import numpy as np
import pandas as pd
from IPython.display import display
import plotly.graph_objects as go

from asset_src.asset_simulator import AssetSimulator
from asset_src.tbase_for_asset import save_dict_as_json, read_json_as_dict


def get_exe_dir():
    if getattr(sys, 'frozen', False):
        # PyInstallerでexe化されている場合
        exe_path = sys.executable
    else:
        # 通常のPythonスクリプト実行の場合
        exe_path = __file__
    return os.path.dirname(os.path.abspath(exe_path))


def make_js_in():
    maindir = get_exe_dir()
    cond = {
        "output_dir": f"{maindir}/result",
        "asset_plan_in": f"{maindir}/asset_plan.csv",
        "sock_database_path": f"{maindir}/database",
        "fig_mode": "plotly",
        "is_show": False,
        "single_life_mode": True,
        "initial_year": 2025,
        "initial_cash": 2500000,
        "initial_invest_asset": 0,
        "inflation_rate": 1.02,
        "multi_life_mode": True,
        "number_of_life": 1000,
        "check_years": [2026, 2030, 2040, 2050, 2060, 2070, 2080, 2090],
        "asset_threshold": 50000000,
        "achieve_percents": [70, 80, 90, 95, 99]
    }
    js_in = f"{maindir}/condition.json"
    save_dict_as_json(cond, js_in)


def main():
    maindir = get_exe_dir()
    js_in = f"{maindir}/condition.json"
    cond = read_json_as_dict(js_in)
    os.makedirs(cond["output_dir"], exist_ok=True)
    AS = AssetSimulator(js_in)
    AS.check_plan()
    AS.cal_asset()


if __name__ == "__main__":
    maindir = get_exe_dir()
    print(f"{maindir=}")
    js_in = f"{maindir}/condition.json"
    if os.path.exists(js_in):
        main()
    else:
        make_js_in()
        main()
