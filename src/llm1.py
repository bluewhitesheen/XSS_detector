import asyncio
import pandas as pd
import matplotlib.pyplot as plt
from CNN_pytorch import XSSDetector
from penetration_test_normal.test import test_payload
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import os
import json
import matplotlib
matplotlib.rcParams['font.family'] = 'Microsoft JhengHei'
from openai import OpenAI
from dotenv import load_dotenv
from datetime import datetime
import time as t

async def process_file(temp_str, time_str):
    detector = XSSDetector("res/best_model.pth", "res/word2vec.model")

    input_path = f"res/llm_output/llm_output_temp_{temp_str}_{time_str}.txt"

    with open(input_path, "r", encoding="utf-8") as file_read:
        payloads = [line.strip() for line in file_read if line.strip()]

    html_path = "http://127.0.0.1:5500/src/penetration_test_normal/test_innerHTML.html"

    syntax_success_count = 0
    model_bypass_count = 0
    overall_success_count = 0

    async with async_playwright() as playwright:
        for i, payload in enumerate(payloads):
            detector_result = detector.is_xss(payload)

            try:
                syntax_result = await test_payload(playwright, html_path, payload)
            except Exception as e:
                print(f"[{temp_str}] #{i} ❌ syntax error: {e}")
                syntax_result = False

            if syntax_result:
                syntax_success_count += 1

            if detector_result == 0:
                model_bypass_count += 1

            if syntax_result and detector_result == 0:
                overall_success_count += 1

            print(f"[{temp_str}] #{i} → detector={detector_result}, syntax={syntax_result}")

    total = len(payloads)
    syntax_rate = syntax_success_count / total
    bypass_rate = model_bypass_count / total
    overall_rate = overall_success_count / total

    print(f"\n📊 統計結果（溫度 {temp_str}, 共 {total} 筆）：")
    print(f"✅ 語法成功率     = {syntax_rate:.2%}")
    print(f"🛡️ 模型繞過成功率 = {bypass_rate:.2%}")
    print(f"🏆 整體成功率     = {overall_rate:.2%}")

    return {
        "Temperature": float(temp_str),
        "Total Payloads": total,
        "Syntax Success Rate": syntax_rate,
        "Model Bypass Rate": bypass_rate,
        "Overall Success Rate": overall_rate
    }

async def main():
    load_dotenv()
    results = []
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    temp = 0.7
    rounds = 15
    timestamp = datetime.now().strftime("%m%d%H%M")
    

    for i in range(rounds):
        print(f"[INFO] 正在產生第 {i + 1} 輪的 payload（temp={temp}）...")

        messages = [
            {"role": "system", "content": "你是一位 Web 資安專家，擅長製作對抗性 XSS 攻擊樣本"},
        ]

        if os.path.exists("prompt.txt"):
            with open("prompt.txt", "r", encoding="utf-8") as f:
                lines = f.readlines()
                for line in lines:
                    try:
                        messages.extend(json.loads(line))
                    except json.JSONDecodeError:
                        continue

        messages.append({"role": "user",
         "content": (
            "請幫我生成 30 筆語法正確、能在現代瀏覽器（如 Chrome）中自動觸發執行的 XSS payload，需符合以下條件：\n\n"
            "1. 不需任何使用者互動就能自動執行（不能使用 onclick、onmouseover、onfocus 等互動事件）。\n"
            "2. 必須使用自動觸發 JavaScript 的 HTML 元素，例如 <img onerror>、<svg onload>、<meta http-equiv>、<iframe srcdoc> 等，也可使用冷門元素如 <object>、<marquee>、<details>。\n"
            "3. 對 alert、script、javascript 等關鍵字進行混淆處理，例如：\n"
            "   - 字串拼接（如 'al' + 'ert'）\n"
            "   - Unicode 編碼（如 \\u0061\\u006c\\u0065\\u0072\\u0074）\n"
            "   - HTML 實體編碼（如 &#x61;&#x6C;&#x65;&#x72;&#x74;）\n"
            "   - Base64 編碼搭配 atob 解碼\n"
            "   - 或其他變形方式\n"
            "4. Payload 應具備繞過機器學習模型（例如 CNN、RNN）檢測的能力，避免使用常見模板（如 <script>alert(1)</script>）或明顯可辨識的語法結構。\n\n"
            "請只輸出 payload 字串，每一筆一行，不要加入任何解釋、描述或標示，除了 HTML 標籤本身外，不要加入任何文字。"
            )
        })

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=temp,
            frequency_penalty=0.0
        )

        print(i)
        payload = response.choices[0].message.content.strip()

        filename = f"res/llm_output/llm_output_temp_{temp}_{timestamp}_{i}.txt"
        os.makedirs("res/llm_output", exist_ok=True)
        with open(filename, "w", encoding="utf-8") as file:
            file.write(payload)

        result = await process_file(temp, f"{timestamp}_{i}")
        Temp = result["Temperature"]
        total_payloads = result["Total Payloads"]
        syntax_rate = result["Syntax Success Rate"]
        bypass_rate = result["Model Bypass Rate"]
        overall_rate = result["Overall Success Rate"]
        results.append({
            "Round": i + 1,
            "Temperature": Temp,
            "Total Payloads": total_payloads,
            "Syntax Success Rate": syntax_rate,
            "Model Bypass Rate": bypass_rate,
            "Overall Success Rate": overall_rate
        })
        
        score_text = f"語法成功率：{syntax_rate:.2f}，模型繞過成功率：{bypass_rate:.2f}，整體成功率：{overall_rate:.2f}"
        with open("prompt.txt", "a", encoding="utf-8") as f:
            pair = [
                {"role": "assistant", "content": payload},
                {"role": "user", "content": score_text}
            ]
            f.write(json.dumps(pair, ensure_ascii=False) + "\n")

        t.sleep(1.5)

    df = pd.DataFrame(results)
    df.to_excel(f"XSS_{temp}_15rounds_stats.xlsx", index=False)

    temp_label = df["Temperature"].iloc[0]
    plt.figure(figsize=(10, 6))
    plt.plot(df["Round"], df["Syntax Success Rate"] * 100, marker='o', label="Syntax Success Rate")
    plt.plot(df["Round"], df["Model Bypass Rate"] * 100, marker='o', label="Model Bypass Rate")
    plt.plot(df["Round"], df["Overall Success Rate"] * 100, marker='o', label="Overall Success Rate")
    plt.xlabel("Round")
    plt.ylabel("Success Rate (%)")
    plt.title(f"Success Rate Variation under Temp {temp_label} (15 Rounds)")
    plt.ylim(0, 100)
    plt.legend()
    plt.grid(True)
    plt.savefig(f"XSS_{temp_label}_15rounds_plot.png")
    plt.close()

    print("Finished!")

if __name__ == "__main__":
    asyncio.run(main())
