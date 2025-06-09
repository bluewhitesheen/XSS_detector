import asyncio
from CNN_pytorch import XSSDetector
from penetration_test_normal.test import test_payload
from playwright.async_api import async_playwright


async def main():
    detector = XSSDetector("res/best_model_evo1.pth", "res/word2vec.model")
    file_read = open("res/llm_output/llm_output_06090036.txt", "r")
    success_payloads = open("res/success/success_payloads_06090037.txt", "a+")
    success_payloads.seek(0)
    success_payloads_set = set(success_payloads.read().splitlines())
    payloads = file_read.readlines()

    async with async_playwright() as playwright:
        html_path = "http://127.0.0.1:5500/src/penetration_test_normal/test_innerHTML.html" 

        for i, payload in enumerate(payloads):
            payload = payload.strip()
            detector_result = detector.is_xss(payload)
            syntax_result = await test_payload(playwright, html_path, payload)  # 使用 await 調用異步函數
            

            print(i, detector_result, syntax_result)
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