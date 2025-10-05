import tkinter as tk
from tkinter import messagebox
from config_manager import get_is_active, set_is_active

class ConfigController:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("ClipBorder")
        self.root.geometry("300x150")
        
        # 現在の状態表示
        self.status_label = tk.Label(self.root, text="", font=("Arial", 12))
        self.status_label.pack(pady=10)
        
        # ボタンフレーム
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=10)
        
        # 開始ボタン
        self.start_btn = tk.Button(button_frame, text="開始", command=self.start_monitoring, 
                                   bg="green", fg="white", width=10)
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        # 停止ボタン
        self.stop_btn = tk.Button(button_frame, text="停止", command=self.stop_monitoring,
                                  bg="red", fg="white", width=10)
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        # 更新ボタン
        self.refresh_btn = tk.Button(self.root, text="状態更新", command=self.update_status)
        self.refresh_btn.pack(pady=5)
        
        # 初期状態更新
        self.update_status()
        
    def update_status(self):
        """現在の状態を更新"""
        is_active = get_is_active()
        if is_active == 1:
            self.status_label.config(text="状態: 監視中", fg="green")
        else:
            self.status_label.config(text="状態: 停止中", fg="red")
    
    def start_monitoring(self):
        """監視を開始"""
        if set_is_active(1):
            messagebox.showinfo("成功", "クリップボード監視を開始しました")
            self.update_status()
        else:
            messagebox.showerror("エラー", "設定の保存に失敗しました")
    
    def stop_monitoring(self):
        """監視を停止"""
        if set_is_active(0):
            messagebox.showinfo("成功", "クリップボード監視を停止しました")
            self.update_status()
        else:
            messagebox.showerror("エラー", "設定の保存に失敗しました")
    
    def run(self):
        """GUIを開始"""
        self.root.mainloop()

if __name__ == "__main__":
    controller = ConfigController()
    controller.run()
