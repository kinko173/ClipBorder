import os
import sys
import json
import requests
import tkinter as tk
from tkinter import simpledialog, messagebox

#LLM_CONFIG_FILE = "llm_api_key.json"
#URL_CONFIG_FILE = "url_api_key.json"
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

LLM_CONFIG_FILE = os.path.join(BASE_DIR, "llm_api_key.json")
URL_CONFIG_FILE = os.path.join(BASE_DIR, "url_api_key.json")

# --- APIキー保存・読み込み ---
def save_llm_api_key(api_key: str):
    with open(LLM_CONFIG_FILE, "w") as f:
        json.dump({"llm_api_key": api_key}, f)

def load_llm_api_key():
    if not os.path.exists(LLM_CONFIG_FILE):
        return None
    with open(LLM_CONFIG_FILE, "r") as f:
        data = json.load(f)
    return data.get("llm_api_key")

def save_url_api_key(api_key: str):
    with open(URL_CONFIG_FILE, "w") as f:
        json.dump({"url_api_key": api_key}, f)

def load_url_api_key():
    if not os.path.exists(URL_CONFIG_FILE):
        return None
    with open(URL_CONFIG_FILE, "r") as f:
        data = json.load(f)
    return data.get("url_api_key")

# --- APIキー検証（簡易） ---
def validate_llm_api_key(api_key: str) -> bool:
    try:
        from groq import Groq
        client = Groq(api_key=api_key)

        # 軽量なリクエストで検証（モデル一覧を取得）
        models = client.models.list()
        if hasattr(models, "data") and len(models.data) > 0:
            return True
        else:
            return False
            
    except Exception as e:
        print("Groq接続エラー:", e)
        return False

def validate_url_api_key(api_key: str) -> bool:
    # URL検知用APIキーの簡易検証
    print(f"api:{api_key}")
    """
    URL検知サービス用APIキーを軽く叩いて検証する。
    実際のエンドポイントは利用するサービスに合わせて変更すること。
    """
    payload = {"url": "https://urlhaus-api.abuse.ch/v1/url/"}  # JSON形式
    try:
        headers = {"Auth-Key": api_key}
        # 軽量なテストリクエスト
        resp = requests.post("https://urlhaus-api.abuse.ch/v1/url/", headers=headers, data=payload, timeout=5)

        if resp.status_code == 200:
            return True
        elif resp.status_code == 401:
            print("認証エラー: APIキーが無効です")
            return False
        else:
            print(f"予期しない応答: {resp.status_code} {resp.text}")
            return False

    except Exception as e:
        print("URL検知API接続エラー:", e)
        return False

# --- APIキーが無効な場合に再設定 ---
def setup_key_invalid(llm=False, url=False):
    """
    llm=TrueならLLM APIキー、url=TrueならURL APIキーを再設定。
    両方Trueでも順に入力可能。
    GUI画面で入力し、未入力ならFalseを返す。
    """
    class KeyInputWindow:
        def __init__(self, llm_flag, url_flag):
            self.llm_flag = llm_flag
            self.url_flag = url_flag
            self.result = None  # True or False
            self.root = tk.Tk()
            self.root.title("APIキー再設定")
            self.root.geometry("550x250")
            self.root.resizable(False, False)

            tk.Label(
                self.root,
                text="⚠️ APIキーの再設定",
                font=("Arial", 14, "bold"),
                fg="#C0392B"
            ).pack(pady=10)

            tk.Label(
                self.root,
                text="無効なAPIキーが検出されました。下記に入力してください。",
                font=("Arial", 11),
                justify="left",
                anchor="w"
            ).pack(padx=20, pady=5, fill="x")

            frame = tk.Frame(self.root)
            frame.pack(padx=20, pady=10, fill="x")

            row_idx = 0  # 行番号のカウンタ

            if self.llm_flag:
                # 手順説明
                tk.Label(
                    frame,
                    text="※LLM APIキーの取得方法については、\n  Anti-Clickfix GitHub リポジトリの説明をご参照ください\n",
                    font=("Arial", 10),
                    fg="#555555",
                    justify="left",
                    anchor="w"   # これを追加するとラベル内テキストも左寄せ
                ).grid(row=row_idx, column=1, sticky="w", padx=5, pady=(0,5))
                row_idx += 1

                # 入力ラベルとEntry
                tk.Label(frame, text="LLM APIキー：", font=("Arial", 11)).grid(row=row_idx, column=0, sticky="w")
                self.llm_entry = tk.Entry(frame, width=50)
                self.llm_entry.grid(row=row_idx, column=1, padx=5, pady=5)
                self.llm_entry.insert(0, load_llm_api_key() or "")
                row_idx += 1

            if self.url_flag:
                # 手順説明
                tk.Label(
                    frame,
                    text="※URL検知サービス用 APIキーの取得方法については、\n  Anti-Clickfix GitHub リポジトリの説明をご参照ください\n",
                    font=("Arial", 10),
                    fg="#555555",
                    justify="left",
                    anchor="w"   # これを追加するとラベル内テキストも左寄せ
                ).grid(row=row_idx, column=1, sticky="w", padx=5, pady=(0,5))
                row_idx += 1

                # 入力ラベルとEntry
                tk.Label(frame, text="URL検知 APIキー：", font=("Arial", 11)).grid(row=row_idx, column=0, sticky="w")
                self.url_entry = tk.Entry(frame, width=50)
                self.url_entry.grid(row=row_idx, column=1, padx=5, pady=5)
                self.url_entry.insert(0, load_url_api_key() or "")
                row_idx += 1


            btn_frame = tk.Frame(self.root)
            btn_frame.pack(pady=15)

            tk.Button(btn_frame, text="保存して開始", width=20, command=self.save_keys).pack(padx=10)
            #tk.Button(btn_frame, text="キャンセル", width=15, command=self.cancel).pack(side="left", padx=10)

            self.root.mainloop()

        def save_keys(self):
            if self.llm_flag:
                llm_key = self.llm_entry.get().strip()
                if not llm_key:
                    messagebox.showwarning("未入力", "LLM APIキーが入力されませんでした。")
                    self.result = False
                    self.root.destroy()
                    return
                if not validate_llm_api_key(llm_key):
                    messagebox.showerror("エラー", "LLM APIキーが無効です。")
                    return
                save_llm_api_key(llm_key)

            if self.url_flag:
                url_key = self.url_entry.get().strip()
                if not url_key:
                    messagebox.showwarning("未入力", "URL APIキーが入力されませんでした。")
                    self.result = False
                    self.root.destroy()
                    return
                if not validate_url_api_key(url_key):
                    messagebox.showerror("エラー", "URL APIキーが無効です。")
                    return
                save_url_api_key(url_key)

            messagebox.showinfo("完了", "APIキーを保存しました。")
            self.result = True
            self.root.destroy()

        def cancel(self):
            self.result = False
            self.root.destroy()

    win = KeyInputWindow(llm, url)
    return win.result


# --- 初回設定GUI ---
class WelcomeWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("初回設定")
        self.root.geometry("550x400")
        self.root.resizable(False, False)
        
        tk.Label(
            self.root,
            text="✨ Anti-Clickfix ✨",
            font=("Arial", 16, "bold"),
            fg="#2E86C1"
        ).pack(pady=10)

        tk.Label(
            self.root,
            text=(
                "初回起動時に LLM と URL検知用の APIキー設定が必要です。\n\n"
                "1. LLMとURL検知用のAPIキーの取得\n\n"
                "※APIキーの取得方法については、\n  Anti-Clickfix GitHub リポジトリの説明をご参照ください\n\n"
                "2. 下の入力欄に取得したAPIキーを入力\n\n"
                "※ 設定は一度行えば次回以降不要です。"
            ),
            font=("Arial", 10),
            justify="left",
            anchor="w"
        ).pack(padx=20, pady=10, fill="x")

        # 入力フレーム
        frame = tk.Frame(self.root)
        frame.pack(pady=20, padx=20, fill="x")

        tk.Label(frame, text="LLM APIキー：", font=("Arial", 11)).grid(row=0, column=0, sticky="w")
        self.llm_entry = tk.Entry(frame, width=50)
        self.llm_entry.grid(row=0, column=1, padx=5, pady=5)
        self.llm_entry.insert(0, load_llm_api_key() or "")

        tk.Label(frame, text="URL検知 APIキー：", font=("Arial", 11)).grid(row=1, column=0, sticky="w")
        self.url_entry = tk.Entry(frame, width=50)
        self.url_entry.grid(row=1, column=1, padx=5, pady=5)
        self.url_entry.insert(0, load_url_api_key() or "")

        # ボタン
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=20)

        #変更渕
        tk.Button(btn_frame, text="保存して開始", width=20, command=self.save_keys,bg="#F5B7B1", fg="black").pack(padx=10)
        #tk.Button(btn_frame, text="終了", width=15, command=self.later).pack(side="left", padx=10) 

        self.root.mainloop()

####これより下，変更高尾

    def save_keys(self):
        llm_key = self.llm_entry.get().strip()
        url_key = self.url_entry.get().strip()
        """
        if self.save_api_keys_with_validation(llm_key, url_key):
            self.root.destroy()
        """
    #APIキーを検証して保存する。
    #成功時 True, 失敗時 False を返す。
    #def save_api_keys_with_validation(llm_key: str, url_key: str) -> bool:

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

        messagebox.showinfo("完了", "APIキーを保存しました。")
        self.root.destroy()
    #削除渕
    """
    def later(self):
        messagebox.showinfo("注意", "APIキーが設定されていないため、一部機能は利用できません。")
        self.root.destroy()
    """