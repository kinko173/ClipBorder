import re #追加渕
import ctypes
import win32api
import win32con
import win32clipboard
import win32gui
from analysis import analyze_text

#追加 _wnd_proc内の処理のため，win32conにはないので自分で定義する必要がある
WM_CLIPBOARDUPDATE = 0x031D

class ClipboardWatcher:
    def __init__(self):
        self.hwnd = None
        self.next_viewer = None

        self.running = False

    def start(self):
        if self.running:
            return
        
        self.running = True

        wc = win32gui.WNDCLASS()
        wc.lpfnWndProc = self._wnd_proc
        wc.lpszClassName = "ClipboardWatcher"
        wc.hInstance = win32api.GetModuleHandle(None)
        class_atom = win32gui.RegisterClass(wc)

        #追加   #user32.dll にある Windows API使用のため
        user32 = ctypes.windll.user32

        self.hwnd = win32gui.CreateWindow(
            class_atom,
            "ClipboardWatcherWindow",
            0,
            0, 0, 0, 0,
            0, 0, wc.hInstance, None
        )

        #SetClipboardViewer(self.hwnd)から変更  #Windows 10 以前向けらしい
        self.next_viewer = user32.AddClipboardFormatListener(self.hwnd)
        win32gui.PumpMessages()

    def stop(self):
        """クリップボード監視を停止"""
        if self.hwnd and self.running:
            self.running = False
            user32 = ctypes.windll.user32
            user32.RemoveClipboardFormatListener(self.hwnd)
            win32gui.DestroyWindow(self.hwnd)
            win32gui.PostQuitMessage(0)
    

    def _wnd_proc(self, hwnd, msg, wparam, lparam):
        #win32con.WM_DRAWCLIPBOARDから変更
        if msg == WM_CLIPBOARDUPDATE:

            #debug
            print("Clipboard updated!")

            try:
                win32clipboard.OpenClipboard()
                if win32clipboard.IsClipboardFormatAvailable(win32con.CF_UNICODETEXT):
                    data = win32clipboard.GetClipboardData(win32con.CF_UNICODETEXT)
                    if data:
                        #変更 渕
                        print(f"data:{data}")
                        
                        # 日本語または改行が含まれていれば終了
                        if re.search(r'[\u3040-\u30FF\u4E00-\u9FFF]|[\r\n]', data):
                            print("日本語または改行を検出。処理を終了します。")
                            return 0

                        analyze_text(data)
            except Exception as e:
                print("Clipboard error:", e)
            finally:
                try:
                    win32clipboard.CloseClipboard()
                except Exception:
                    pass
            return 0    #追加
            

        elif msg == win32con.WM_DESTROY:
            #win32gui.ChangeClipboardChain(hwnd, self.next_viewer)  #削除
            win32gui.PostQuitMessage(0)
            return 0

        return win32gui.DefWindowProc(hwnd, msg, wparam, lparam)