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
        {"role": "user","content": (
        "請幫我生成 30 筆語法正確的 XSS payload，需符合以下條件：\n\n"
        "1. 不需要使用者互動就能自動執行（不能使用 onclick、onmouseover、onfocus 等互動事件）。\n"
        "2. 必須能在自動觸發 JavaScript，例如使用 <img onerror>、<svg onload>、<meta refresh>、<iframe srcdoc> 等元素。\n"
        "3. 請對關鍵詞如 alert、script、javascript 進行混淆處理，例如字串拼接、Unicode 編碼、HTML 實體編碼、Base64 等。\n"
        "4. Payload 應具備繞過機器學習模型（例如 CNN）檢測的能力，盡量避免明顯可辨識的語法結構。\n\n"
        "請只輸出 payload 字串，每一筆一行，不要加入任何解釋，除 HTML 標籤外，不要任何說明。")
    }],
    temperature=0.5, frequency_penalty=0.0
)

time = datetime.now().strftime("%m%d%H%M")

with open("res/llm_output/llm_output_" + time + ".txt", "w", encoding="utf-8") as file:
    file.write(response.choices[0].message.content)

print("Finished!")
