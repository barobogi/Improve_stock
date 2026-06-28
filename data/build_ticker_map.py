"""
build_ticker_map.py — 종목명 → 티커 매핑 생성
실행: python data/build_ticker_map.py
"""
import json, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ── 수동 매핑 (해외 종목 + 알려진 국내 종목) ───────────────────
MANUAL_MAP = {
    # 국내 주식
    "삼성전자":                             {"ticker": "005930.KS", "market": "KRX"},
    "KODEX 코스닥150레버리지":              {"ticker": "233740.KS", "market": "KRX"},
    "KODEX 미국나스닥100":                  {"ticker": "379800.KS", "market": "KRX"},
    "KODEX 미국S&P500":                     {"ticker": "379810.KS", "market": "KRX"},

    # 해외 주식
    "AST 스페이스모바일":                   {"ticker": "ASTS",   "market": "NASDAQ"},
    "셀레스티카":                           {"ticker": "CLS",    "market": "NYSE"},
    "아이렌":                               {"ticker": "IREN",   "market": "NASDAQ"},
    "엔비디아":                             {"ticker": "NVDA",   "market": "NASDAQ"},
    "파가야 테크놀로지스":                  {"ticker": "PGY",    "market": "NASDAQ"},
    "퀀텀스케이프":                         {"ticker": "QS",     "market": "NYSE"},
    "서프 에어 모빌리티":                   {"ticker": "SRFM",   "market": "NASDAQ"},
    "앰프리어스 테크놀로지스":              {"ticker": "AMPX",   "market": "NASDAQ"},
    "BTQ 테크놀로지스":                     {"ticker": "BTTX",   "market": "NASDAQ"},
    "실스크":                               {"ticker": "SLRX",   "market": "NASDAQ"},  # TODO 확인
    "X-에너지":                             {"ticker": "X-ENGY", "market": "TODO"},    # 미상장 or 특수

    # 해외 레버리지 ETF (TRADR/TRDR 계열)
    "TRDR 2X ASTS ETF":                     {"ticker": "ASTU",   "market": "NASDAQ"},
    "TRADR 2X LNG ETF":                     {"ticker": "LNGG",   "market": "NYSE"},
    "TRDR CLS DLY ETF":                     {"ticker": "CLSX",   "market": "NASDAQ"},
    "TRDR 2X CRDO ETF":                     {"ticker": "CRDX",   "market": "NASDAQ"},
    "TT DF 2XIREN ETF":                     {"ticker": "IREX",   "market": "NASDAQ"},  # TODO 확인
    "TRD2XLG APLD ETF":                     {"ticker": "APLDX",  "market": "NASDAQ"},  # TODO 확인
    "DFC DLY RKLB ETF":                     {"ticker": "RKLBX",  "market": "NASDAQ"},  # TODO 확인
    "Leverage Shares 2X Long CBRS DLY ETF": {"ticker": "CBRSX",  "market": "TODO"},    # TODO 확인
    "RNDHL MEMRY ETF":                      {"ticker": "MEMY",   "market": "TODO"},    # TODO 확인
    "RNDHLL INVTN ETF":                     {"ticker": "NVDX",   "market": "TODO"},    # TODO 확인

    # 해외 일반 ETF
    "Schwab 미국 배당주 ETF":               {"ticker": "SCHD",   "market": "NYSE"},

    # 수익증권/현금 (분석 제외)
    "삼성미국S&P500인덱스증권자투자H(주)-Ce": {"ticker": None, "market": "SKIP"},
    "삼성신종종류형MMF제4호-CP":              {"ticker": None, "market": "SKIP"},
    "현금성자산(삼성증권)":                   {"ticker": None, "market": "SKIP"},
    "삼성증권 디폴트옵션 안정자산형":         {"ticker": None, "market": "SKIP"},
}

def lookup_krx_code(name: str) -> str | None:
    """pykrx로 종목명 → KRX 코드 조회"""
    try:
        from pykrx import stock
        tickers = stock.get_market_ticker_list(market="ALL")
        for t in tickers:
            if stock.get_market_ticker_name(t) == name:
                return f"{t}.KS"
    except Exception as e:
        print(f"  pykrx 오류 ({name}): {e}")
    return None

def build_map():
    with open("data/sample_portfolio.json", encoding="utf-8") as f:
        d = json.load(f)
    stocks = d.get("stocks", [])

    # 고유 종목 추출
    unique = {}
    for s in stocks:
        name = s["name"]
        if name not in unique:
            unique[name] = s["type"]

    result = {}
    todo_list = []

    for name, stype in unique.items():
        if name in MANUAL_MAP:
            info = MANUAL_MAP[name].copy()
            info["type"] = stype
            result[name] = info
        elif stype == "주식":
            # 국내 ETF → pykrx 자동 조회
            print(f"  pykrx 조회 중: {name}")
            code = lookup_krx_code(name)
            if code:
                result[name] = {"ticker": code, "market": "KRX", "type": stype}
                print(f"    → {code}")
            else:
                result[name] = {"ticker": "TODO", "market": "KRX", "type": stype}
                todo_list.append(name)
                print(f"    → 미발견 (TODO)")
        else:
            result[name] = {"ticker": "TODO", "market": "TODO", "type": stype}
            todo_list.append(name)

    # 저장
    out = "data/ticker_map.json"
    with open(out, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"\n✅ 저장: {out}")
    print(f"총 {len(result)}개 / TODO: {len(todo_list)}개")
    if todo_list:
        print("\n⚠️  확인 필요 종목:")
        for n in todo_list:
            print(f"  - {n}")

    return result

if __name__ == "__main__":
    build_map()
