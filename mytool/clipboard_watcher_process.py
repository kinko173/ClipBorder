import json
import time
import sys
import os

# スクリプトのディレクトリをsys.pathに追加（モジュールインポートのため）
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

from clipboard_watcher import ClipboardWatcher

def load_config():
    """config.jsonを読み込む"""
    config_path = os.path.join(os.path.dirname(__file__), "config.json")
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Config loading error: {e}")
        return {"is_active": 0}

def save_config(config):
    """config.jsonに保存する"""
    config_path = os.path.join(os.path.dirname(__file__), "config.json")
    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Config saving error: {e}")
        return False

def set_inactive():
    """config.jsonのis_activeを0に設定"""
    try:
        config = load_config()
        config["is_active"] = 0
        if save_config(config):
            print("Config updated: is_active set to 0")
        else:
            print("Failed to update config")
    except Exception as e:
        print(f"Error setting config inactive: {e}")

def main():
    """独立したクリップボード監視プロセス"""
    print("Clipboard watcher process started")
    
    # 終了処理のためのシグナルハンドラを設定
    import signal
    import atexit
    
    def cleanup_handler(signum=None, frame=None):
        """プロセス終了時のクリーンアップ"""
        print("Performing cleanup before exit...")
        set_inactive()
    
    # 終了時のクリーンアップを登録
    atexit.register(cleanup_handler)
    signal.signal(signal.SIGTERM, cleanup_handler)
    signal.signal(signal.SIGINT, cleanup_handler)
    
    # クリップボード監視を開始
    print("aaaaaaaaaaaa")
    watcher = ClipboardWatcher()
    
    # 監視スレッドを開始（非ブロッキング）
    import threading
    watcher_thread = threading.Thread(target=watcher.start, daemon=True)
    watcher_thread.start()
    
    print("Clipboard monitoring active. Checking config.json every 2 seconds...")
    
    # 2秒ごとにconfig.jsonをチェック
    while True:
        try:
            config = load_config()
            is_active = config.get("is_active", 0)
            
            if is_active == 0:
                print("Config set to inactive. Clipboard watcher process terminating...")
                watcher.stop()  # クリップボード監視を適切に停止
                set_inactive()  # config.jsonを確実に0に設定
                sys.exit(0)
            
            time.sleep(2)
        except KeyboardInterrupt:
            print("Clipboard watcher process interrupted by user")
            watcher.stop()
            set_inactive()  # 終了前にconfig.jsonを0に設定
            sys.exit(0)
        except Exception as e:
            print(f"Error in clipboard watcher process: {e}")
            time.sleep(2)

if __name__ == "__main__":
    main()
