import asyncio
from CNN_pytorch import XSSDetector
from penetration_test_normal.test import test_payload
from playwright.async_api import async_playwright

async def main():
    detector = XSSDetector("res/best_model.pth", "res/word2vec.model")
    file_read = open("res/llm_output.txt", "r")
    success_payloads = open("res/success_payloads.txt", "a")
    payloads = file_read.readlines()

    async with async_playwright() as playwright:
        html_path = "http://127.0.0.1:5500/src/penetration_test_normal/test_innerHTML.html" 

        for payload in payloads:
            payload = payload.strip()
            detector_result = detector.is_xss(payload)
            syntax_result = await test_payload(playwright, html_path, payload)  # 使用 await 調用異步函數
            
            if detector_result == 0 and syntax_result:
                print(f"Payload: {payload} SUCCESS")
                success_payloads.write(payload + "\n")

        success_payloads.close()
        file_read.close() 

# 使用 asyncio 執行異步主函數
if __name__ == "__main__":
    asyncio.run(main())