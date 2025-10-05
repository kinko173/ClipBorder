Set WshShell = CreateObject("WScript.Shell")
' run.batと同じディレクトリのpython_envとanti_clickfix.pyを実行
WshShell.CurrentDirectory = CreateObject("Scripting.FileSystemObject").GetParentFolderName(WScript.ScriptFullName)
' 0 = ウィンドウを非表示, True = 実行完了を待つ
WshShell.Run "python_env\python.exe anti_clickfix.py", 0, False
