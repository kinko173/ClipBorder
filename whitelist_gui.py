import os
import json
import sys
import tkinter as tk
from tkinter import messagebox

#WHITELIST_FILE = "whitelist.json"

"""
try:
    BASE_DIR = os.path.dirname(__file__)  # .py 実行時
except NameError:
    BASE_DIR = os.path.dirname(sys.executable)  # EXE 実行時
"""
# Python embeddableでの実行を想定した適切なパス取得
if getattr(sys, 'frozen', False):
    # PyInstallerでパッケージ化された場合
    BASE_DIR = os.path.dirname(sys.executable)
else:
    # 通常のPythonスクリプトとして実行される場合
    # Python embeddableの場合、スクリプトの場所を基準にする
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

WHITELIST_FILE = os.path.join(BASE_DIR, "whitelist.json")

# --- ホワイトリスト読み込み ---
def load_whitelist():
    if not os.path.exists(WHITELIST_FILE):
        return {"texts": [], "urls": []}
    with open(WHITELIST_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

# --- ホワイトリスト保存 ---
def save_whitelist(whitelist):
    with open(WHITELIST_FILE, "w", encoding="utf-8") as f:
        json.dump(whitelist, f, indent=2, ensure_ascii=False)

# --- 選択項目を追加 ---
def add_selected(var_list, wl, win):
    for t, text, var in var_list:
        if var.get():
            if t == "text" and text not in wl["texts"]:
                wl["texts"].append(text)
            elif t == "url" and text not in wl["urls"]:
                wl["urls"].append(text)
    save_whitelist(wl)
    messagebox.showinfo("完了", "選択した項目をホワイトリストに登録しました。")
    win.destroy()

# --- ホワイトリスト登録画面 ---
def whitelist_window(options):
    wl = load_whitelist()
    win = tk.Toplevel()
    win.title("ホワイトリスト登録")
    win.geometry("500x400")
    win.resizable(False, False)
    win.configure(bg="#E8F8F5")  # 薄緑背景

    tk.Label(win, text="✅ ホワイトリストに登録する項目を選択してください",
             font=("Arial", 12, "bold"), bg="#E8F8F5").pack(pady=10)

    # スクロール可能フレーム
    frame = tk.Frame(win, bg="#E8F8F5")
    frame.pack(fill="both", expand=True, padx=10, pady=5)
    canvas = tk.Canvas(frame, bg="#E8F8F5")
    scrollbar = tk.Scrollbar(frame, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas, bg="#E8F8F5")
    scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0,0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    var_list = []
    print(f"option:{options}")
    for t, text in options:
        var = tk.BooleanVar()
        cb = tk.Checkbutton(scrollable_frame, text=f"[{t.upper()}] {text}", variable=var,
                            anchor="w", justify="left", wraplength=450, bg="#E8F8F5", font=("Arial",11))
        cb.pack(fill="x", pady=2)
        var_list.append((t, text, var))

    # 下部ボタン
    btn_frame = tk.Frame(win, bg="#E8F8F5")
    btn_frame.pack(pady=10)
    tk.Button(btn_frame, text="登録", width=15,
              command=lambda: add_selected(var_list, wl, win)).pack(side="left", padx=10)
    tk.Button(btn_frame, text="閉じる", width=15, command=win.destroy).pack(side="left", padx=10)