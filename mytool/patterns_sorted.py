# 並び替え済みパターンファイル
# 危険度: High -> Medium -> Low の順に並べています。
# 元の説明文はそのまま維持しています。

patterns = [
    # === HIGH ===
    (r"(?i)rm\s+-rf", "大量のファイル・フォルダを削除する命令が含まれています。"),
    (r"(?i)(curl|wget)\s+[^|\r\n]+?\s*\|\s*(sh|bash|powershell)", "外部のスクリプトを直接ダウンロードして実行しようとしています。"),
    (r"(?i)powershell\s+-enc", "中身が隠された（エンコードされた）命令が使われています。"),
    (r"(?i)\b(-e|-encoded(?:command)?|-eNcOdEdCoMMaNd)\b", "暗号化／エンコードされたコマンドが使われています。"),
    (r"(?i)-encodedcommand\b", "中身が隠されたコマンドが使われています（解読不可）。"),
    (r"(?i)invoke-expression", "外部から受け取った文字列を勝手に実行しようとしています。"),
    (r"(?i)downloadfile\(\s*['\"]", "外部からファイルをダウンロードしようとしています。"),
    (r"(?i)downloadstring", "外部から文字列データを取得しようとしています。"),
    (r"(?i)downloaddata", "外部からバイナリデータを取得しようとしています。"),
    (r"(?i)new-object\s+system\.net\.webclient", "ネットワークからデータを取得する準備が行われています。"),
    (r"(?i)Invoke-WebRequest", "外部のサイトからファイルやデータを取得しようとしています。"),
    (r"(?i)invoke-webrequest", "外部サイトからファイルやデータを取得しようとしています。"),
    (r"(?i)invoke-restmethod", "外部のサービスと通信しようとしています。"),
    (r"(?i)\b(?:invoke-|iwr\b|irm\b|iex\b|nEW-oBJeCt\s+System\.Net\.)", "外部取得や即時実行の短縮形が使われています。"),
    (r"(?i)\bdownload(file|string|data)\s*\(", "外部から取得する命令（.Download）が使われています。"),
    (r"(?i)AKIA[0-9A-Z]{16}", "AWSのアクセスキーらしき文字列が含まれています。"),
    (r"(?i):ASIA|ACCA[0-9A-Z]{16}", "一時的なAWS認証情報が含まれている可能性があります。"),
    (r"(?is)-----BEGIN (?:RSA|OPENSSH|ED25519|DSA) PRIVATE KEY-----", "秘密鍵（プライベートキー）が含まれています。"),
    (r"(?i)password\s*=\s*['\"][^'\"]{8,}['\"]", "パスワードのような文字列が含まれています。"),
    (r"(?i)(?:[A-Za-z0-9+/]{40,}={0,2})", "長いBase64文字列が検出されました（ペイロードの可能性）。"),
    (r"(?i)(?:0x[0-9A-Fa-f]{400,})", "非常に長い16進データが含まれています（可能性: バイナリ）。"),
    (r"(?i)\b(FromBase64String|Base64ToString)\s*\(", "Base64で暗号化された文字列が復号されています。"),
    (r'(?i)\bpython\s+-c\s+["\']import\s+base64', "暗号化されたデータを復号してその場で実行する可能性があります。"),

    # === MEDIUM ===
    (r"(?i)\bpowershell(\.exe)?\b", "PowerShell が呼ばれています。"),
    (r"(?i)\b(pwsh|posh)\b", "PowerShell 系の別名が使われています。"),
    (r"(?i)cmd\.exe", "コマンドプロンプトが呼ばれています。"),
    (r"(?i)mshta\.exe", "HTMLアプリケーション実行の痕跡があります。"),
    (r"(?i)wscript\.exe", "スクリプト実行ホストが呼ばれています。"),
    (r"(?i)cscript\.exe", "スクリプト実行ホスト（コマンド版）が呼ばれています。"),
    (r"(?i)regsvr32\.exe", "レジストリ登録ツールが悪用されている可能性があります。"),
    (r"(?i)certutil\.exe", "証明書ツールがファイル取得や変換に使われています。"),
    (r"(?i)rundll32\.exe", "DLLを使った実行が試みられています。"),
    (r"(?i)msiexec\.exe", "MSI 実行の痕跡があります。"),
    (r"(?i)bitsadmin\.exe", "BITS 管理ツールが使われています（ダウンロード等）。"),
    (r"(?i)ftp\.exe", "FTP を使った通信が行われています。"),
    (r"(?i)\bwmic\s+process\s+call\b", "WMIC を使ったプロセス操作が行われています。"),
    (r"(?i)\brun-dll32\.exe\b", "不正なライブラリが読み込まれる可能性があります。"),
    (r"(?i)\b(mshta|wscript|cscript|regsvr32|rundll32|msiexec|certutil|bitsadmin|schtasks)\.exe\b", "管理用実行ファイルが呼ばれています。"),
    (r"(?i)start-process\b", "別のプログラムを新しく起動しようとしています。"),
    (r"(?i)\bstart-process\s+['\"]?[^-\s].*\.ps1\b", "PowerShell スクリプトを新プロセスで実行しようとしています。"),
    (r"(?i)\b(Add-Type|System\.Reflection\.Assembly)\b", "コードを動的に組み込む命令が使われています。"),
    (r"(?i)system\.reflection\.assembly", ".NET の反射機能が使われています。"),
    (r"(?i)system\.text\.encoding", "特殊な文字コード処理が使われています。"),
    (r"(?i)invoke-item\b", "ファイルやプログラムを開こうとしています。"),
    (r"(?i)out-file\b", "ファイルへの書き出しが行われようとしています。"),
    (r"(?i)\b(Add-Type|System\.Reflection\.Assembly)\b", "プログラム内でコードを新たに作成・コンパイルしています。"),
    (r"(?i)\b(FromBase64String|Base64ToString)\s*\(", "Base64で暗号化された文字列が復号されています。"),

    # === LOW ===
    (r"(?i)set-clipboard\b", "クリップボードの内容を書き換えようとしています。"),
    (r"(?i)get-clipboard\b", "クリップボードの内容を読み取ろうとしています。"),
    (r"(?i)\b(Get|Set)-Clipboard\b", "クリップボードの読み書き操作が検出されました。"),
    (r"(?i)invoke-item\b", "ファイルやプログラムを開こうとしています。"),
    (r"(?i)out-file\b", "ファイルへの書き出しが行われようとしています。"),
    (r"(?i)sleep\s+\d{1,3}\s*;\s*exit", "自動実行テストの可能性がある命令です。"),
    (r"(?i)\bSendKeys\s*\(\s*\".*{ENTER}\"'", "キーボード入力を自動で送る操作が検出されました。"),
    (r"(?i)\bpython\s+-c\s+[\"']import\s+base64", "暗号化されたデータを復号してその場で実行する可能性があります。"),
    (r"(?i)\b(cmd|cmd\.exe|/c\s+start)\b", "コマンドプロンプトを起動しています。"),
    (r"(?i)\b(mshta|wscript|cscript|regsvr32|rundll32|msiexec|certutil|bitsadmin|schtasks)\.exe\b", "管理用実行ファイルが呼ばれています。"),
    (r"(?i)\bwmic\s+process\s+call\b", "WMIC を使ったプロセス操作が行われています。"),
    (r"(?i)\brun-dll32\.exe\b", "不正なライブラリが読み込まれる可能性があります。"),
    (r"(?i)ftp\.exe", "FTP を使った通信が行われています。"),
    (r"(?i)bitsadmin\.exe", "BITS 管理ツールが使われています（ダウンロード等）。"),
]

# 注意: 元のパターン群には重複や似た意味の正規表現が存在します。
# 必要であれば重複削除、各パターンに 'severity' フィールド追加、
# または JSON/CSV で出力するなどの追加加工も可能です。
