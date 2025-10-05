import re
import json, os
from whitelist_gui import load_whitelist
from warning_gui import show_warning_window
from detectors import check_malicious_command, check_malicious_url, check_with_llm


#仕様書(5)に相当する処理
#今の実装はすべての警告にllmの説明を付けてる
#常にllmを呼ぶのが嫌な場合，check_with_llm(text)は片方のみ悪性のコメント下で呼ぶ    #Todo
def detailed_analysis(text: str):
    command_findings = check_malicious_command(text)

    print("bbbbbbbbbbbbbb")
    url_findings = check_malicious_url(text)


    print("cccccccccccccccc")
    
    #LLM
    USE_LLM = True

    base_dir = os.path.dirname(os.path.abspath(__file__))
    config_file = os.path.join(base_dir, "llm_api_key.json")

    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
            api_key = config['llm_api_key']
            print(f"{api_key}")
        SET_GROQ_API = True
    except Exception as e:
        print("eee:{e}")
        SET_GROQ_API = False

    # ホワイトリスト読み込み
    wl = load_whitelist()
    text_block = (text not in wl["texts"])
    print(f"text_block{text_block}")
    url_findings = [u for u in url_findings if u[0] not in wl["urls"]]
    print(f"url:{url_findings}")

    if not text_block and not url_findings:
        print("ホワイトリスト登録済みの内容のみです。警告なし。")
        return
    
    elif not text_block:
        print("ホワイトリスト登録済みのテキストです。警告なし。")
        return

    elif not command_findings and not url_findings:
        print("ホワイトリスト登録済みのURLです。警告なし。")
        return

    if SET_GROQ_API and USE_LLM:
        print(f"boolco:{bool(command_findings)}")
        print(f"boolco:{bool(url_findings)}")

        details = []

        # 両方悪性 → LLM処理は行わない
        if command_findings and url_findings:

            for pattern, reason in command_findings:
                details.append(f"[コマンド検出]  {pattern}\n理由: {reason}\n")
            for url, reason in url_findings:
                details.append(f"[URL検出]  {url}\n理由: {reason}\n")

            message = "コピーされた内容は危険です！\n\n"
            message += f"[内容]  {text}\n\n"
            message += "\n".join(details)

            # options には text と url を渡す
            options = [("text", text)] + [("url", u[0]) for u in url_findings]
            show_warning_window("セキュリティ警告", message, options)
            return

        # 片方悪性の場合のみ LLM チェック
        elif (command_findings or url_findings):
            llm_malicious, llm_explanation, llm_detailed_analysis = check_with_llm(text, api_key)
            print(f"Malicious: {llm_malicious}")
            print(f"Explanation: {llm_explanation}")
            print(f"Detailed Analysis: {llm_detailed_analysis}")

            llm_malicious_jp = "危険" if llm_malicious else "安全"

            # 片方悪性 かつ LLM 悪性 → コマンド/URL検出は出さず LLM のみ
            if llm_malicious:
                message = "コピーされた内容は危険です！\n\n"
                message += f"[内容]  {text}\n\n"
                if url_findings:
                    for url, reason in url_findings:
                        details.append(f"[URL検出]  {url}")
                    message += "\n".join(details)
                message += f"\n\n[LLM補足説明]  {llm_malicious_jp}\n理由: {llm_explanation}"

                options = [("text", text)] + [("url", u[0]) for u in url_findings]
                show_warning_window("セキュリティ警告", message, options, llm_detailed_analysis)
                return


            # 片方悪性かつLLM良性
            elif not llm_malicious:
                pass
                return        

        else: #仕様書(5)の(ウ)，両方良性    #Todo
            #未定義の処理
            pass
            return #なかったので追加

#仕様書(2)に相当する処理
def analyze_text(text: str):
    text_lower = text.lower()

    # URL検出（複数含まれる可能性あり）
    url_pattern = r"https?://[^\s]+"  # http:// または https:// に続く文字列を検出
    urls = re.findall(url_pattern, text_lower)

    # PowerShell 検出 
    contains_powershell = "powershell" in text_lower

    # URLかPowerShellがある場合，詳細な解析を実行
    if urls or contains_powershell:
        detailed_analysis(text)

    else:
        pass
