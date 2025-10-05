import json
import subprocess
import os
import sys
import warnings
import tkinter.messagebox as messagebox

base_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
CONFIG_FILE = os.path.join(base_dir, "config.json")
CLIPBOARD_SCRIPT = os.path.join(base_dir, "clipboard_watcher_process.py")
LOCK_FILE = os.path.join(base_dir, "controller.lock")

if os.path.exists(LOCK_FILE):
    os.remove(LOCK_FILE)

# Python embeddable の python.exe パスを取得
python_exe = os.path.join(base_dir, "python_env", "python.exe")
# pythonw.exe があればそちらを優先（コンソールなし版、より静か）
pythonw_exe = os.path.join(base_dir, "python_env", "pythonw.exe")
if os.path.exists(pythonw_exe):
    python_exe = pythonw_exe

# config.json を読み込む
with open(CONFIG_FILE, "r", encoding="utf-8") as f:
    config = json.load(f)

# is_active が 1 の場合のみスクリプトを起動
if config.get("is_active") == 1:
    # Python スクリプトを別プロセスとして起動
    try:
        # サブプロセスを起動（ログファイルにリダイレクト）
        process = subprocess.Popen(
            [python_exe, CLIPBOARD_SCRIPT],
            creationflags=subprocess.CREATE_NO_WINDOW,
        )

    except Exception as e:
        # 起動失敗 → メッセージを表示
        messagebox.showerror(
            "ClipBorder起動失敗",
            f"ClipBorder を起動できませんでした。\n\n"
            f"エラー: {e}\n\n"
            "設定画面を開き、一度 OFF に切り替えてから再度 ON にしてください。"
        )
