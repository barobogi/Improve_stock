import yfinance as yf

test_tickers = {
    "삼성전자": "005930.KS",
    "KODEX 코스닥150레버리지": "233740.KS",
    "KODEX 미국나스닥100": "379800.KS",
    "엔비디아": "NVDA",
    "SCHD": "SCHD",
    "ASTS": "ASTS",
    "QS": "QS",
}

print("=== yfinance 실데이터 테스트 ===")
for name, ticker in test_tickers.items():
    try:
        hist = yf.Ticker(ticker).history(period="5d")
        if hist.empty:
            print(f"[❌] {name} ({ticker}) — 데이터 없음")
        else:
            close = hist["Close"].iloc[-1]
            vol   = hist["Volume"].iloc[-1]
            ma5   = hist["Close"].mean()
            pos   = "위" if close > ma5 else "아래"
            print(f"[✅] {name} ({ticker}) — 종가:{close:.2f} | 5일MA:{ma5:.2f}({pos}) | 거래량:{int(vol):,}")
    except Exception as e:
        print(f"[❌] {name} ({ticker}) — {e}")
