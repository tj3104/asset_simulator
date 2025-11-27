import json
from pathlib import Path


def save_dict_as_json(data: dict,
                      file_path: str,
                      ensure_ascii=False,
                      indent=4):
    """
    辞書をJSONファイルとして保存する。

    Args:
        data (dict): 保存する辞書
        file_path (str): 保存先のパス
        ensure_ascii (bool): TrueにするとASCII文字のみ出力（日本語はエスケープされる）
        indent (int): インデント幅（整形しない場合はNone）
    """
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)  # ディレクトリがなければ作成
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=ensure_ascii, indent=indent)


def get_json_as_dict(file_path: str) -> dict:
    """
    JSONファイルを読み込み辞書として返す。

    Args:
        file_path (str): JSONファイルのパス
    Returns:
        dict: 読み込んだ辞書
    """
    path = Path(file_path)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


class Base_class:

    def __init__(self, js_in):
        json_dict = get_json_as_dict(js_in)
        if not isinstance(json_dict, dict):
            raise TypeError("引数はdict型である必要があります")

        for key, value in json_dict.items():
            if key.isidentifier() and not key.startswith("_"):
                setattr(self, key, value)
