import asyncio
from playwright.async_api import async_playwright

# 要測試的 payload 列表
innerHTML_payloads = [
    "<img src=x onerror=alert('XSS')>",
    "<svg/onload=alert('XSS')>",
    "<iframe src='javascript:alert(`XSS`)'></iframe>",
    "<input autofocus onfocus=alert('XSS')>",
    "<details open ontoggle=alert('XSS')>"
]

# 可選：你可以使用 Live Server 路徑
html_path_base = "http://127.0.0.1:5500/penetration_test_normal/"
html_paths = [html_path_base + "test_innerHTML.html", html_path_base + "test_href.html", html_path_base + "test_onerror.html"]

async def test_payload(playwright, html_path: str, payload: str) -> bool:
    browser = await playwright.chromium.launch(headless=True)
    context = await browser.new_context()

    context.alert_triggered = False

    async def on_dialog(dialog):
        context.alert_triggered = True
        print(f"Alert triggered: {dialog.message}")
        await dialog.dismiss()

    page = await context.new_page()
    page.on("dialog", on_dialog)

    # 使用 window.name 傳遞 payload
    await page.goto(html_path)
    await page.evaluate(f'window.name = `{payload}`')
    await page.reload()
    await asyncio.sleep(1)

    await browser.close()
    return context.alert_triggered

async def main():
    async with async_playwright() as playwright:
        print("=== 開始測試 XSS Payloads ===")
        for html_path in html_paths:
            print(f"Testing: {html_path}")
            for i, payload in enumerate(innerHTML_payloads):
                try:
                    result = await test_payload(playwright, html_path, payload)
                    if result:
                        print(f"[{i}] Triggered | {payload}")
                    else:
                        print(f"[{i}] Not Triggered | {payload}")
                except Exception as e:
                    print(f"[{i}] Error! | Payload: {payload}")
            print(f"=== 完成測試: {html_path} ===\n\n")

if __name__ == "__main__":
    asyncio.run(main())
