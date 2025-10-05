import re
from groq import Groq
import os
import json
import requests
from typing import Optional, Dict #高尾追加
from patterns_sorted import patterns
from url_response_translate import THREAT_MAP, STATUS_MAP #追加高尾

#仕様書(4)に相当する処理，正規表現によるテキストのチェック
def check_malicious_command(text: str) -> list[tuple[str, str]]:

    findings = []
    for pattern, reason in patterns:
        """
        if re.search(pattern, text, flags=re.IGNORECASE):
            return [(pattern, reason)]
        """
        match = re.search(pattern, text, flags=re.IGNORECASE)   #試せてない
        if match:
            matched_text = match.group(0)  # 実際にマッチした文字列
            return [(matched_text, reason)]

    return findings


#仕様書(4)に相当する処理，APIによるurlのチェック
def query_urlhaus(url: str) -> Optional[Dict]:
    """
    URLhaus API に問い合わせて結果を返す。
    正常時は dict を返し、失敗時は None を返す。
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    config_file = os.path.join(base_dir, "url_api_key.json")

    print(f"aaa:{config_file}")

    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
            api_key = config['url_api_key']
            print(f"url:{api_key}")
            print("dddddddddddddd")

        SET_GROQ_API = True
    except Exception as e:
        print(f"{e}")
        print("eeeeeeeeeeeeeee")
        SET_GROQ_API = False
    api_url = "https://urlhaus-api.abuse.ch/v1/url/"
    headers = {
        "Auth-Key": api_key
    }
    payload = {"url": url}  # JSON形式
    try:
        resp = requests.post(
    "https://urlhaus-api.abuse.ch/v1/url/",
    headers=headers,
    data=payload,  # ここが重要
    timeout=10
)
        print(f"[DEBUG] HTTP status code: {resp.status_code}")
        print(f"[DEBUG] Response text: '{resp.text}'")  # 空かどうか確認
        if not resp.text.strip():
            print("[DEBUG] Response is empty! 形式が間違っている可能性があります。")
            return None
            
        if resp.status_code == 200:
            return resp.json()
        else:
            print(f"[DEBUG] URLhaus API HTTP error: {resp.status_code}")
            return None
    except requests.RequestException as e:
        print(f"[DEBUG] URLhaus API request exception: {e}")
        return None


def check_malicious_url(text: str) -> list[tuple[str, str]]:
    """
    テキスト中の URL を抽出して、URLhaus に問い合わせて
    危険なものを検出し、その理由を返す。
    戻り値： (URL, 説明) のリスト
    """
    url_pattern = r"https?://[^\s]+"  
    urls = re.findall(url_pattern, text)
    print(f"urls{urls}")

    findings: list[tuple[str, str]] = []
    for url in urls:
        result = query_urlhaus(url)

        # API呼び出し自体の成否を確認（デバッグ用）
        if result:
            print(f"[DEBUG] URLhaus API called successfully for: {url}")
            print(f"[DEBUG] Response: {result}")
        else:
            print(f"[DEBUG] URLhaus API call failed or empty for: {url}")
            continue

        status = result.get("query_status")

        if status == "ok":
            # 脅威タイプを取得（なければ空文字）
            threat = result.get("threat", "")
            url_status = result.get("url_status", "")
            
            #追加高尾日本語化
            desc_threat = THREAT_MAP.get(threat, f"未知の脅威({threat})")
            desc_status = STATUS_MAP.get(url_status, f"未知の状態({url_status})")

            #追加高尾
            desc = f"悪性のURLとして登録済みです。\n脅威タイプ：{desc_threat}\n通信先の状態：{desc_status}"
            findings.append((url, desc))

        elif status == "no_results":
            # 良性URLの可能性（問い合わせは成功）
            #findings.append((url, "URLhaus 問い合わせ済み: 登録なし"))
            continue

    return findings


#仕様書(6)に相当する処理
def check_with_llm(text: str, api_key: str) -> tuple[bool, str, str]:
    # config.jsonからapi_keyを読み込み

    client = Groq(api_key=api_key)
    system_prompt = {
        "role": "system",
        "content": """あなたはサイバーセキュリティの専門家です。与えられたテキストを分析し、悪意のあるコマンドやURLが含まれているかを判断してください。

判断の際は以下の点を考慮してください：
- PowerShell、Bash、CMD等の危険なコマンド
- 難読化された文字列やエンコード
- 外部からのスクリプトダウンロード（curl、wget、Invoke-WebRequest等）
- 実行権限の変更や迂回
- システムファイルの操作
- 不審なURL

回答は以下の形式で出力してください：
'True: [理由]' または 'False: [理由]'

理由は必ず以下の形式で出力してください：
簡潔な説明: (50文字程度，日本語)
詳細な説明: (200文字以上500文字以下，日本語)

理由は具体的で分かりやすく記述してください。"""
    }
    user_input = f"""以下のテキストを分析してください：

{text}

このテキストが悪意のあるコマンドやURLを含むかどうかを判断し、その理由を説明してください。"""
    user_prompt = {
    "role": "user", "content": user_input
    }
    print(user_input)

    # Initialize the chat history
    chat_history = [system_prompt, user_prompt]

    response = client.chat.completions.create(model="groq/compound",
                                            messages=chat_history,
                                            max_tokens=300,
                                            temperature=0.0)

    results_content = response.choices[0].message.content.strip()
    
    # results_contentからTrueかFalseを抽出し、説明部分をexplainに格納
    if results_content.strip().lower().startswith('true'):
        isMalicious = True
        # "True:"以降の部分を説明として抽出
        explain = results_content.strip()[5:].strip()  # "True:"を除去
    elif results_content.strip().lower().startswith('false'):
        isMalicious = False
        # "False:"以降の部分を説明として抽出
        explain = results_content.strip()[6:].strip()  # "False:"を除去
    else:
        # デフォルトでFalseとする（予期しない形式の場合）
        isMalicious = False
        explain = results_content  # 全体を説明として使用

    match_explain = re.search(r"簡潔な説明\s*[:：]\s*(.+?)(?:\s*詳細な説明\s*[:：]|$)", results_content, re.S)
    match_detail  = re.search(r"詳細な説明\s*[:：]\s*(.+)", results_content, re.S)

    if match_explain:
        explain = match_explain.group(1).strip()
        print(f"mat_e:{explain}")
    if match_detail:
        detailed_analysis = match_detail.group(1).strip()
    else:
        # detailed_analysis が取れなかった場合は explain をコピー
        detailed_analysis = explain

    return isMalicious, explain, detailed_analysis
