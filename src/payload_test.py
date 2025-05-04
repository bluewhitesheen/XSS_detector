import asyncio
from CNN_pytorch import XSSDetector
from penetration_test_normal.test import test_payload
from playwright.async_api import async_playwright
from tqdm import tqdm


async def main():
    detector = XSSDetector("res/best_model.pth", "res/word2vec.model")
    file_read = open("res/llm_output/llm_output_05032142.txt", "r")
    success_payloads = open("res/success_payloads.txt", "a+")
    success_payloads.seek(0)
    success_payloads_set = set(success_payloads.read().splitlines())
    payloads = file_read.readlines()

    async with async_playwright() as playwright:
        html_path = "http://127.0.0.1:5500/src/penetration_test_normal/test_innerHTML.html" 
        success_payloads.write("\n")

        for payload in tqdm(payloads):
            payload = payload.strip()
            detector_result = detector.is_xss(payload)
            syntax_result = await test_payload(playwright, html_path, payload)  # 使用 await 調用異步函數
            
            if detector_result == 0 and syntax_result:
                if payload not in success_payloads_set:
                    success_payloads.write(payload + "\n")
                    print(f"Payload: {payload} successfully added to success_payloads.txt")
                else:
                    print(f"Payload: {payload} already exists in success_payloads.txt")

        success_payloads.close()
        file_read.close() 

# 使用 asyncio 執行異步主函數
if __name__ == "__main__":
    asyncio.run(main())