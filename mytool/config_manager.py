import json
import os
import sys

#CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.json")
"""
try:
    BASE_DIR = os.path.dirname(__file__)  # .py 実行時
except NameError:
    BASE_DIR = os.path.dirname(sys.executable)  # EXE 実行時
"""
# PyInstallerでexe化した場合の適切なパス取得
if getattr(sys, 'frozen', False):
    # PyInstallerでパッケージ化された場合
    BASE_DIR = os.path.dirname(sys.executable)
else:
    # 通常のPythonスクリプトとして実行される場合
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

CONFIG_PATH = os.path.join(BASE_DIR, "config.json")

def load_config():
    """config.jsonを読み込む"""
    try:
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Config loading error: {e}")
        return {"is_active": 0}

def save_config(config):
    """config.jsonに保存する"""
    try:
        with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Config saving error: {e}")
        return False

def get_is_active():
    """is_activeの値を取得"""
    config = load_config()
    return config.get("is_active", 0)

def set_is_active(value):
    """is_activeの値を設定"""
    config = load_config()
    config["is_active"] = value
    return save_config(config)
