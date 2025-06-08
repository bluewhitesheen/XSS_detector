import os
from openai import OpenAI
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()  # 載入 .env 中的 OPENAI_API_KEY

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

response = client.chat.completions.create(
    model="gpt-4o",  # 或 gpt-3.5-turbo
    messages=[
        {"role": "system", "content": "你是一位 Web 資安專家，擅長製作對抗性 XSS 攻擊樣本"},
        {"role": "user",
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
    }],
    temperature=0.5, frequency_penalty=0.2, presence_penalty=0.5
)

time = datetime.now().strftime("%m%d%H%M")

with open("res/llm_output/llm_output_" + time + ".txt", "w", encoding="utf-8") as file:
    file.write(response.choices[0].message.content)

print("Finished!")
