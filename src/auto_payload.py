import asyncio
from CNN_pytorch import XSSDetector
from penetration_test_normal.test import test_payload
from playwright.async_api import async_playwright
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_payloads():
    content = (
                "我正在測試一個基於 CNN+LSTM 的 XSS 檢測系統，我想產生能繞過這個系統的 XSS 對抗樣本。"
                "請幫我再產生 10 個類似概念的對抗性 payload，"
                "使用非 script 標籤觸發、使用 setTimeout 或類似手法組合 alert(1)，避免被靜態分詞器解析。"
                "每個 payload 請用一行表示，只需要輸出 payload，不要編號，不要額外說明，"
                "目前成功的 payload 有：\n"
            )
    success_payloads = open("res/success_payloads.txt", "r")

    print(content + success_payloads.read())

    response = client.chat.completions.create(
        model="gpt-4o",  # 或 gpt-3.5-turbo
        messages=[
            {"role": "system", "content": "你是一位 Web 資安專家，擅長製作對抗性 XSS 攻擊樣本"},
            {"role": "user", "content": content + success_payloads.read()}
        ],
        temperature=0.9
    )

    output = open("res/llm_output.txt", "a")
    output.write(response.choices[0].message.content)
    print("Generated payloads successfully!")
    output.close()

async def main():
    detector = XSSDetector("res/best_model.pth", "res/word2vec.model")
    file_read = open("res/llm_output.txt", "r")
    success_payloads = open("res/success_payloads.txt", "a+")
    success_payloads_set = set(success_payloads.read().splitlines())
    payloads = file_read.readlines()

    async with async_playwright() as playwright:
        html_path = "http://127.0.0.1:5500/src/penetration_test_normal/test_innerHTML.html" 

        for payload in payloads:
            payload = payload.strip()
            detector_result = detector.is_xss(payload)
            syntax_result = await test_payload(playwright, html_path, payload)  # 使用 await 調用異步函數
            
            if detector_result == 0 and syntax_result:
                print(f"Payload: {payload} SUCCESS")
                if payload not in success_payloads_set:
                    success_payloads.write(payload + "\n")
                    print(f"Payload: {payload} added to success_payloads.txt")

        success_payloads.close()
        file_read.close() 

# 使用 asyncio 執行異步主函數
if __name__ == "__main__":
    for i in range(3):
        generate_payloads()
        asyncio.run(main())