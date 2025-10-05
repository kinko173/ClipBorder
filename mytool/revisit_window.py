import json
import os
import sys
import winreg

# Python embeddableでの実行を想定した適切なパス取得
if getattr(sys, 'frozen', False):
    # PyInstallerでパッケージ化された場合
    BASE_DIR = os.path.dirname(sys.executable)
else:
    # 通常のPythonスクリプトとして実行される場合
    # Python embeddableの場合、スクリプトの場所を基準にする
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

LOCK_FILE = os.path.join(BASE_DIR, "controller.lock")
"""
os.environ["TCL_LIBRARY"] = os.path.join(BASE_DIR, "tcl", "tcl8.6")
os.environ["TK_LIBRARY"]  = os.path.join(BASE_DIR, "tcl", "tk8.6")
"""
import tkinter as tk
from tkinter import messagebox, ttk

from tkinter import simpledialog
from api_key_manager import (
    save_llm_api_key, save_url_api_key,
    load_llm_api_key, validate_llm_api_key,
    load_url_api_key, validate_url_api_key,
    setup_key_invalid, WelcomeWindow,
)

# レジストリのスタートアップに登録する関数
def register_startup():
    """check_config_and_run.pyをWindowsスタートアップに登録（未登録の場合のみ）"""
    try:
        # レジストリキーを開く
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_READ | winreg.KEY_WRITE)
        
        app_name = "AntiClickfixMonitor"
        
        # すでに登録されているか確認
        try:
            existing_value, _ = winreg.QueryValueEx(key, app_name)
            winreg.CloseKey(key)
            print(f"[INFO] スタートアップに既に登録されています: {existing_value}")
            return  # 既に登録されている場合は何もしない
        except FileNotFoundError:
            # 登録されていない場合、新規登録を行う
            pass
        
        # check_config_and_run.pyのフルパスを取得
        if getattr(sys, 'frozen', False):
            # EXE化されている場合、実行ファイルのパスを使用
            startup_path = sys.executable
        else:
            # Python embeddableの場合、python_env内のpython.exeを使用
            check_config_path = os.path.join(BASE_DIR, "check_config_and_run.py")
            python_exe = os.path.join(BASE_DIR, "python_env", "python.exe")
            startup_path = f'"{python_exe}" "{check_config_path}"'
        
        # レジストリに登録
        winreg.SetValueEx(key, app_name, 0, winreg.REG_SZ, startup_path)
        winreg.CloseKey(key)
        print(f"[INFO] スタートアップに登録しました: {startup_path}")
        
    except Exception as e:
        print(f"[ERROR] スタートアップ登録に失敗しました: {e}")

# --- 設定GUI（二回目以降）---
class Revisitwindow:
    def __init__(self):
        # スタートアップに登録（未登録の場合のみ）
        register_startup()
        
        self.root = tk.Tk()
        self.root.title("ClipBorder")
        self.root.geometry("380x280")
        self.root.resizable(False, False)
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        tk.Label(
            self.root,
            text="設定",
            font=("Arial", 16, "bold"),
            fg="#2E86C1"
        ).pack(pady=10)

        tk.Label(
            self.root,
            text=(
                "ここでは各種設定を行うことができます。\n\n"
                "1. クリップボード監視機能のon/off切り替え\n"
                "2. 監視対象としないURLおよびテキストの設定\n"
                "3. LLM APIおよびURL検知用のAPIの設定\n\n"
                "※ 設定は何度でも変更可能です。"
            ),
            font=("Arial", 11),
            justify="left",
            anchor="w"
        ).pack(padx=20, pady=10, fill="x")

        # func() ON/OFF切替ボタン
        self.switch_states_status = False
        self.switch_states_button = tk.Button(
            self.root,
            text="機能のON/OFF切り替え",
            command=self.call_toggle_config,
            bg="#F5B7B1",   # 背景：赤
            fg="black",     # 文字：白
            activebackground="#C0392B",  # 押したときの背景色
            activeforeground="white"     # 押したときの文字色
        )
        self.switch_states_button.pack(side="left",padx=10)

        # ホワイトリスト設定ボタン
        self.whitelist_button = tk.Button(
            self.root,
            text="ホワイトリスト設定",
            command=self.set_whitelist,
            bg="#85C1E9",   # 背景：青
            fg="black",
            activebackground="#2E86C1",
            activeforeground="white"
        )
        self.whitelist_button.pack(side="left",padx=10)

        # API鍵設定ボタン
        self.api_button = tk.Button(
            self.root,
            text="APIキー設定",
            command=self.set_api_keys,
            bg="#A9DFBF",   # 背景：緑
            fg="black",
            activebackground="#1E8449",
            activeforeground="white"
        )
        self.api_button.pack(side="left",padx=10)

    def set_whitelist(self):
        WHITELIST_FILE = os.path.join(BASE_DIR, "whitelist.json")

        # ホワイトリストを読み込む関数
        def load_whitelist() -> dict:
            try:
                with open(WHITELIST_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except FileNotFoundError:
                #return {"urls": [], "text": []}
                return {"texts": [], "urls": []}

        # ホワイトリストを保存する関数
        def save_whitelist(entries: dict):
            with open(WHITELIST_FILE, "w",encoding="utf-8") as f:
                json.dump(entries, f, indent=2, ensure_ascii=False)

        # 現在のリスト
        current_list = load_whitelist()
        print(f"(curenr:{current_list})")
        current_key = tk.StringVar(value="urls")

        # ウィンドウ作成
        wl_window = tk.Toplevel(self.root)
        wl_window.title("ホワイトリスト管理")
        wl_window.geometry("")
        wl_window.resizable(False, False)

        tk.Label(wl_window, text="現在のホワイトリスト：", font=("Arial", 11, "bold")).pack(pady=5)

        # キー選択（プルダウン）
        tk.Label(wl_window, text="対象を選択してください：", font=("Arial", 11)).pack(pady=5)
        #変更渕
        """
        key_selector = ttk.Combobox(wl_window, textvariable=current_key, values=["texts", "urls"], state="readonly", width=10)
        key_selector.pack(pady=5)
        """
        
        options = ["texts", "urls"]
        key_selector = tk.OptionMenu(wl_window, current_key, *options)
        key_selector.config(width=10)
        key_selector.pack(pady=5)
        

        # スクロール付きリスト
        list_frame = tk.Frame(wl_window)
        list_frame.pack(padx=10, pady=5, fill="both", expand=True)

        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side="right", fill="y")

        listbox = tk.Listbox(list_frame, width=55, height=8, yscrollcommand=scrollbar.set)
        listbox.pack(side="left", fill="both", expand=True)

        scrollbar.config(command=listbox.yview)

        # リスト更新関数
        def refresh_list(*args):
            listbox.delete(0, tk.END)
            for item in current_list[current_key.get()]:
                listbox.insert(tk.END, item)

        refresh_list()
        #key_selector.bind("<<ComboboxSelected>>", refresh_list)
        current_key.trace_add("write", refresh_list)  # ← 変更箇所
    
        # 新規追加
        def add_item():
            new_item = simpledialog.askstring(
                "ホワイトリスト追加",
                f"{current_key.get()} に追加する文字列を入力してください：",
                parent=wl_window
            )
            if not new_item:
                return
            new_item = new_item.strip()

            if new_item in current_list[current_key.get()]:
                messagebox.showinfo("重複", f"'{new_item}' は既に {current_key.get()} に登録されています。", parent=wl_window)
                return

            current_list[current_key.get()].append(new_item)
            save_whitelist(current_list)
            refresh_list()
            #消してみた渕
            #messagebox.showinfo("追加完了", f"'{new_item}' を {current_key.get()} に追加しました。", parent=wl_window)

        # 選択項目削除
        def remove_item():
            selected_indices = listbox.curselection()
            if not selected_indices:
                messagebox.showwarning("選択なし", "削除する項目を選択してください。", parent=wl_window)
                return

            for index in reversed(selected_indices):
                item = listbox.get(index)
                listbox.delete(index)
                current_list[current_key.get()].remove(item)

            save_whitelist(current_list)
            #消してみた渕
            #messagebox.showinfo("削除完了", "選択した項目を削除しました。", parent=wl_window)

        # 操作用ボタン（下部に配置）
        btn_frame = tk.Frame(wl_window)
        btn_frame.pack(pady=10)

        add_btn = tk.Button(btn_frame, text="新規追加", width=12, command=add_item)
        remove_btn = tk.Button(btn_frame, text="削除", width=12, command=remove_item)
        cancel_btn = tk.Button(btn_frame, text="閉じる", width=12, command=wl_window.destroy)

        add_btn.grid(row=0, column=0, padx=5)
        remove_btn.grid(row=0, column=1, padx=5)
        cancel_btn.grid(row=0, column=2, padx=5)  

        tk.Frame(wl_window, height=20).pack()

    def save_api_keys_with_validation(self, llm_key: str, url_key: str) -> bool:

        # 未入力チェック
        if not llm_key and not url_key:
            messagebox.showwarning("未入力", "LLM APIキーとURL検知用 APIキーが入力されていません。")
            return
        elif not llm_key:
            messagebox.showwarning("未入力", "LLM APIキーが入力されていません。")
            return
        elif not url_key:
            messagebox.showwarning("未入力", "URL検知用 APIキーが入力されていません。")
            return

        # LLMキー検証
        if llm_key and not validate_llm_api_key(llm_key):
            messagebox.showerror("エラー", "LLM APIキーが無効です。")
            return

        # URLキー検証
        if url_key and not validate_url_api_key(url_key):
            messagebox.showerror("エラー", "URL検知用 APIキーが無効です。")
            return

        if llm_key:
            save_llm_api_key(llm_key)
        if url_key:
            save_url_api_key(url_key)

    def set_api_keys(self):
        """API鍵設定（llm_api_key.json, url_api_key.json を編集する）"""
        key_window = tk.Toplevel(self.root)
        key_window.title("APIキー設定")
        key_window.geometry("")
        key_window.resizable(False, False)

        tk.Label(key_window, text="APIキー設定", font=("Arial", 14, "bold"), fg="#2E86C1").pack(pady=10)

        frame = tk.Frame(key_window)
        frame.pack(pady=10, padx=20, fill="x")

        tk.Label(frame, text="LLM APIキー：", font=("Arial", 11)).grid(row=0, column=0, sticky="w")
        llm_entry = tk.Entry(frame, width=50)
        llm_entry.grid(row=0, column=1, padx=5, pady=5)
        llm_entry.insert(0, load_llm_api_key() or "")

        tk.Label(frame, text="URL検知用 APIキー：", font=("Arial", 11)).grid(row=1, column=0, sticky="w")
        url_entry = tk.Entry(frame, width=50)
        url_entry.grid(row=1, column=1, padx=5, pady=5)
        url_entry.insert(0, load_url_api_key() or "")

        btn_frame = tk.Frame(key_window)
        btn_frame.pack(pady=15)

        def save_and_close():
            llm_key = llm_entry.get().strip()
            url_key = url_entry.get().strip()
            if self.save_api_keys_with_validation(llm_key, url_key):
                key_window.destroy()

        tk.Button(btn_frame, text="保存", width=15, command=save_and_close).pack(side="left", padx=10)
        tk.Button(btn_frame, text="キャンセル", width=15, command=key_window.destroy).pack(side="left", padx=10)
    
    def start(self):
        """GUI を表示して操作可能にする"""
        self.root.mainloop()

    def call_toggle_config(self):
        from anti_clickfix import AntiClickfixController

        if os.path.exists(LOCK_FILE):
            print("すでにコントローラーが起動しています。")
            return

        # 起動中のフラグとしてロックファイルを作成
        with open(LOCK_FILE, "w") as f:
            f.write(str(os.getpid()))
        # コントローラーGUIを起動
        try:
            controller = AntiClickfixController()
            controller.run()
        finally:
            # 終了時にロックファイルを削除
            if os.path.exists(LOCK_FILE):
                os.remove(LOCK_FILE)

    def on_close(self):
        """ウィンドウを閉じるときの処理（Watcher停止予定）"""
        print("[DEBUG] Closing window... (ここでWatcher.stopを呼ぶ予定)")
        self.root.destroy()
 

