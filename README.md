# XSS detector

* 目前都統一使用 conda 來 build env
* pip install -r requirements.txt 完成之後要裝 playwright 的 broswer driver

* 弄一些 XSS 不同的 payload 類型來當作多樣性，並對這些多樣性做語法測試
* 用 CVE_test_1: 2020-11022 來當真實環境背書

## prompting record

1. 初始版本
:::
    "role": "user", "content": (
    "我正在測試一個基於 CNN+LSTM 的 XSS 檢測系統，我想產生能繞過這個系統，並且能夠在 Chrome 能夠跳窗的 XSS 對抗樣本。"
    "目前成功的 payload 有：\n"
    "<svg/onload=setTimeout('ale'+'rt(1)',100)></svg>\n"
    "<iframe src=\"javascript: setTimeout('ale'+'rt(1)', 100)\"></iframe>\n"
    "<details open ontoggle=\"setTimeout(unescape('%61%6c%65%72%74(1)'), 100)\"></details>\n"
    "請幫我再產生 50 個語法正確、與上方概念不同的 payloads"
    "使用非 script 標籤觸發、使用 setTimeout 或類似手法組合 alert(1)，避免被靜態分詞器解析。"
    "每個 payload 請用一行表示，只需要輸出 payload，不要編號，不要額外說明")
:::

2. 從 5/11 AM 2:00 開始使用
:::
    "role": "user","content": (
    "請幫我生成 30 筆語法正確的 XSS payload，需符合以下條件：\n\n"
    "1. 不需要使用者互動就能自動執行（不能使用 onclick、onmouseover、onfocus 等互動事件）。\n"
    "2. 必須能自動觸發 JavaScript，例如使用 <img onerror>、<svg onload>、<meta refresh>、<iframe srcdoc> 等元素。\n"
    "3. 請對關鍵詞如 alert、script、javascript 進行混淆處理，例如字串拼接、Unicode 編碼、HTML 實體編碼、Base64 等。\n"
    "4. Payload 應具備繞過機器學習模型（例如 CNN）檢測的能力，盡量避免明顯可辨識的語法結構。\n\n"
    "請只輸出 payload 字串，每一筆一行，不要加入任何解釋，除 HTML 標籤外，不要任何說明。")
:::

    