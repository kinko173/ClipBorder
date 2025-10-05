# warning_gui.py
import tkinter as tk
from tkinter import scrolledtext
from whitelist_gui import whitelist_window  # ホワイトリスト登録画面を呼び出すためにimport


# 詳細説明用の小ウィンドウ
def show_detail_window(detailed_text: str):
    detail_win = tk.Toplevel()
    detail_win.title("ClipBorder")
    detail_win.geometry("600x400")
    detail_win.configure(bg="#FDFEFE")
    detail_win.attributes("-topmost", True)  # 常に最前面に表示

    tk.Label(detail_win, text="🔎 詳細な説明", font=("Arial", 14, "bold"),
             fg="#154360", bg="#FDFEFE").pack(pady=10)

    txt = scrolledtext.ScrolledText(detail_win, width=70, height=18, font=("Arial", 11), bg="#F8F9F9")
    txt.pack(padx=20, pady=10, fill="both", expand=True)
    txt.insert("end", detailed_text)
    txt.configure(state="disabled")

    tk.Button(detail_win, text="閉じる", width=15, command=detail_win.destroy, bg="#D5DBDB").pack(pady=10)

# 警告画面
def show_warning_window(title: str, message: str, options, detailed_analysis: str = ""):
    root = tk.Tk()
    root.title("ClipBorder")
    root.geometry("600x400")
    root.resizable(False, False)
    root.configure(bg="#FDEDEC")  # 薄赤背景
    root.attributes("-topmost", True)  # 常に最前面に表示

    tk.Label(root, text="⚠️ " + title, font=("Arial", 16, "bold"),
             fg="#C0392B", bg="#FDEDEC").pack(pady=15)

    # スクロール可能テキスト
    txt = scrolledtext.ScrolledText(root, width=70, height=15, font=("Arial", 11), bg="#FCF3F3")
    txt.pack(padx=20, pady=10, fill="both", expand=True)
    txt.insert("end", message)
    txt.configure(state="disabled")

    # ボタン
    btn_frame = tk.Frame(root, bg="#FDEDEC")
    btn_frame.pack(pady=10)

    tk.Button(btn_frame, text="OK", width=15, command=root.destroy, bg="#F5B7B1").pack(side="left", padx=10)

    if detailed_analysis:  # 詳細説明があるときだけボタン表示
        tk.Button(btn_frame, text="詳細を表示", width=15,
                  command=lambda: show_detail_window(detailed_analysis), bg="#85C1E9").pack(side="left", padx=10)

    tk.Button(btn_frame, text="ホワイトリストに登録", width=20,
              command=lambda: whitelist_window(options), bg="#A9DFBF").pack(side="left", padx=10)

    root.mainloop()
