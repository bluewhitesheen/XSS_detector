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
        {"role": "user", "content": (
            "我正在測試一個基於 CNN+LSTM 的 XSS 檢測系統，我想產生能繞過這個系統的 XSS 對抗樣本。"
            "目前成功的 payload 有：\n"
            "<svg/onload=setTimeout('ale'+'rt(1)',100)></svg>\n"
            "<iframe src=\"javascript: setTimeout('ale'+'rt(1)', 100)\"></iframe>\n"
            "<details open ontoggle=\"setTimeout(unescape('%61%6c%65%72%74(1)'), 100)\"></details>\n"
            "請幫我再產生 20 個語法正確、與上方概念不同的 payloads"
            "使用非 script 標籤觸發、使用 setTimeout 或類似手法組合 alert(1)，避免被靜態分詞器解析。"
            "每個 payload 請用一行表示，只需要輸出 payload，不要編號，不要額外說明"
        )}
    ],
    temperature=1.0,
)

time = datetime.now().strftime("%m%d%H%M")
output = open("res/llm_output/llm_output_" + time + ".txt", "a")
output.write(response.choices[0].message.content)

print("Finished!")
