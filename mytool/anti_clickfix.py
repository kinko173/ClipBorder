import sys 
import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))

script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

# Python embeddableの場合、python_envディレクトリを基準にする
if getattr(sys, 'frozen', False):
    # PyInstallerでパッケージ化された場合
    base_dir = os.path.dirname(sys.executable)
else:
    # Python embeddableの場合、python_envディレクトリを使用
    base_dir = os.path.join(script_dir, "python_env")

os.environ['PATH'] = os.path.join(base_dir, "DLLs") + ";" + os.path.join(base_dir, "tcl") + ";" + os.environ['PATH']

from api_key_manager import (
    load_llm_api_key, validate_llm_api_key,
    load_url_api_key, validate_url_api_key,
    setup_key_invalid, WelcomeWindow,
)

from clipboard_watcher import ClipboardWatcher
from revisit_window import Revisitwindow
from config_manager import get_is_active, set_is_active
import subprocess
import time
import sys
import os
import tkinter as tk
from tkinter import messagebox
import threading

print("sys.argv:", sys.argv)
print("sys.path:", sys.path)
print("cwd:", os.getcwd())

class AntiClickfixController:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("ClipBorder")
        self.root.geometry("400x220")
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # 監視制御変数
        self.is_active_old = False
        self.clipboard_process = None
        self.monitoring_active = True
        
        # 起動時に既存の状態を確認
        #self.check_existing_state()
        
        # GUI要素
        self.create_widgets()
        
        # バックグラウンドで監視ループを開始
        self.monitoring_thread = threading.Thread(target=self.monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        
        # 状態更新タイマー
        self.update_status()
        
    def check_existing_state(self):
        """起動時に既存のクリップボード監視状態を確認"""
        try:
            current_state = get_is_active()
            self.is_active_old = current_state == 1
            
            if self.is_active_old:
                print("既存のクリップボード監視が動作中です")
                # 既存プロセスが本当に動作しているかチェック
                self.check_existing_process()
            else:
                print("クリップボード監視は停止状態です")
                
        except Exception as e:
            print(f"起動時状態確認エラー: {e}")
            self.is_active_old = False
    
    def check_existing_process(self):
        """既存のクリップボード監視プロセスが動作しているかチェック"""
        try:
            script_name = "clipboard_watcher_process.py"
            
            # Windowsのtasklistコマンドを使用してプロセスをチェック
            result = subprocess.run(['tasklist', '/fo', 'csv'], 
                                  capture_output=True, text=True, encoding='shift_jis')
            
            if result.returncode == 0:
                # 出力からpythonプロセスを探す
                lines = result.stdout.split('\n')
                for line in lines:
                    if 'python' in line.lower() and script_name in line:
                        print(f"既存のクリップボード監視プロセスを発見")
                        return True
                        
                # より詳細にチェック（WMICコマンドを使用）
                wmic_result = subprocess.run([
                    'wmic', 'process', 'where', 'name="python.exe"', 
                    'get', 'commandline', '/format:csv'
                ], capture_output=True, text=True, encoding='shift_jis')
                
                if wmic_result.returncode == 0:
                    for line in wmic_result.stdout.split('\n'):
                        if script_name in line:
                            print(f"既存のクリップボード監視プロセスを発見（詳細チェック）")
                            return True
                            
            print("既存のクリップボード監視プロセスが見つかりません")
            # config.jsonでは有効だがプロセスが見つからない場合は停止状態に戻す
            if get_is_active() == 1:
                print("config.jsonを停止状態に更新します")
                set_is_active(0)
                self.is_active_old = False
            return False
            
        except Exception as e:
            print(f"既存プロセスチェックエラー: {e}")
            # エラーの場合は安全のため既存プロセスなしと仮定
            return False
        
    def create_widgets(self):
        """GUI要素を作成"""
        # タイトル
        title_label = tk.Label(self.root, text="ClipBorder Controller", 
                              font=("Arial", 16, "bold"))
        title_label.pack(pady=10)
        
        # 現在の状態表示
        self.status_label = tk.Label(self.root, text="", font=("Arial", 12))
        self.status_label.pack(pady=10)
        
        # プロセス状態表示
        self.process_label = tk.Label(self.root, text="", font=("Arial", 10))
        self.process_label.pack(pady=5)
        
        # ボタンフレーム
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=10)
        
        # 開始ボタン
        self.start_btn = tk.Button(button_frame, text="監視開始", command=self.start_and_close, 
                                   bg="green", fg="white", width=12, height=2)
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        # 停止ボタン
        self.stop_btn = tk.Button(button_frame, text="監視停止", command=self.stop_and_close,
                                  bg="red", fg="white", width=12, height=2)
        self.stop_btn.pack(side=tk.LEFT, padx=5)

    def update_status(self):
        """現在の状態を定期更新"""
        try:
            is_active = get_is_active()
            if is_active == 1:
                self.status_label.config(text="状態: ON", fg="green")
            else:
                self.status_label.config(text="状態: OFF", fg="red")
                
            # プロセス状態 - より詳細な表示
            if self.clipboard_process and self.clipboard_process.poll() is None:
                self.process_label.config(text="クリップボード監視中", fg="blue")
            elif is_active == 1:
                # config.jsonでは有効だが、管理中プロセスがない場合
                self.process_label.config(text="クリップボード監視中", fg="blue")
            else:
                self.process_label.config(text="停止中", fg="gray")
                
        except Exception as e:
            print(f"Status update error: {e}")
            
        # 1秒後に再更新
        if self.monitoring_active:
            self.root.after(1000, self.update_status)
    
    def start_monitoring(self):
        """監視を開始"""
        try:
            if set_is_active(1):
                messagebox.showinfo("成功", "クリップボード監視を開始しました")
            else:
                messagebox.showerror("エラー", "設定の保存に失敗しました")
        except Exception as e:
            messagebox.showerror("エラー", f"監視開始エラー: {e}")
    
    def stop_monitoring(self):
        """監視を停止"""
        try:
            if set_is_active(0):
                messagebox.showinfo("成功", "クリップボード監視を停止しました")
            else:
                messagebox.showerror("エラー", "設定の保存に失敗しました")
        except Exception as e:
            messagebox.showerror("エラー", f"監視停止エラー: {e}")
    def start_and_close(self):
        self.start_monitoring()  # 監視開始
        self.on_closing()        # 終了処理

    def stop_and_close(self):
        self.stop_monitoring()   # 監視停止
        self.on_closing()        # 終了処理
    
    def monitoring_loop(self):
        """バックグラウンドでの監視制御ループ"""
        print("Starting anti-clickfix monitoring...")
        
        while self.monitoring_active:
            try:
                # config.jsonのis_activeを取得
                is_active_current = get_is_active()
                is_active = is_active_current == 1
                
                # 前回がFalseで今回がTrueの場合、クリップボード監視を開始
                if not self.is_active_old and is_active:
                    print("Starting clipboard watcher process...")
                    script_path = os.path.join(os.path.dirname(__file__), "clipboard_watcher_process.py")
                    # Python embeddable の python.exe を使用
                    python_exe = os.path.join(os.path.dirname(__file__), "python_env", "python.exe")
                    self.clipboard_process = subprocess.Popen(
                        [python_exe, script_path],
                        creationflags=subprocess.CREATE_NO_WINDOW
                        ) #, creationflags=subprocess.CREATE_NEW_CONSOLE)
                    print("Clipboard watcher process started")
                
                # 前回の状態を保存
                self.is_active_old = is_active
                
                # プロセスが終了していないかチェック
                if self.clipboard_process and self.clipboard_process.poll() is not None:
                    print("Clipboard watcher process ended")
                    self.clipboard_process = None
                
                time.sleep(2)
                
            except Exception as e:
                print(f"Error in monitoring loop: {e}")
                time.sleep(2)
    
    def on_closing(self):
        """アプリケーション終了時の処理"""
        print("Anti-Clickfix Controller を終了します")
        print("クリップボード監視プロセスは継続して動作します")

        time.sleep(1)

        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        LOCK_FILE = os.path.join(BASE_DIR, "controller.lock")
        if os.path.exists(LOCK_FILE):
            os.remove(LOCK_FILE)
        
        self.monitoring_active = False
        
        # クリップボード監視プロセスは終了させない（継続させる）
        # config.jsonの状態もそのまま維持
        
        self.root.destroy()
        # sys.exit(0) を削除 - 他のプロセスに影響させない
    
    def run(self):
        """GUIを開始"""
        self.root.mainloop()

if __name__ == "__main__":
    llm_api_key = load_llm_api_key()
    url_api_key = load_url_api_key()
    
    #変更高尾 #変更渕
    if (llm_api_key and url_api_key):
        llm_api_key = load_llm_api_key()
        url_api_key = load_url_api_key()
        if not validate_llm_api_key(llm_api_key):
            if not setup_key_invalid(llm=True):
                sys.exit(0)
            llm_api_key = load_llm_api_key()
        if not validate_url_api_key(url_api_key):
            if not setup_key_invalid(url=True):
                sys.exit(0)
            url_api_key = load_url_api_key()
        if not (llm_api_key and url_api_key):
            sys.exit(0)  # ユーザーが設定しなかった場合は終了
        win2 = Revisitwindow()
        win2.start()
        sys.exit(0)

    if not (llm_api_key and url_api_key):
        win = WelcomeWindow()
        llm_api_key = load_llm_api_key()
        url_api_key = load_url_api_key()
        if not (llm_api_key and url_api_key):
            sys.exit(0)  # ユーザーが設定しなかった場合は終了
    
    win2 = Revisitwindow()
    win2.start()
