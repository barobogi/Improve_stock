# foreign_filter.py — 외국인 순매수 강도 점수화 (pykrx 기반, API 키 불필요)
import json
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Optional

try:
    from pykrx import stock as krx
    PYKRX_AVAILABLE = True
except ImportError:
    PYKRX_AVAILABLE = False

try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False


# 종목명 -> yfinance 티커 매핑 (ticker_map.json 기반으로 확장)
# KRX: {코드}.KS / NASDAQ/NYSE: 티커 직접
TICKER_MAP = {
    # 한국 개별주
    "삼성전자": "005930.KS",
    # KRX ETF
    "KODEX 미국나스닥100":               "379800.KS",
    "KODEX 미국S&P500":                 "379810.KS",
    "KODEX 코스닥150레버리지":            "233740.KS",
    "KODEX 미국우주항공":                "0167Z0.KS",
    "KODEX 미국나스닥100데일리커버드콜OTM": "494300.KS",
    "KODEX 금융고배당TOP10타겟위클리커버드콜": "498410.KS",
    "KODEX 금융고배당TOP10타겟커버드콜":    "498410.KS",
    "KODEX 미국배당커버드콜액티브":         "441640.KS",
    "KODEX 테슬라커버드콜채권혼합액티브":    "475080.KS",
    "KODEX 200타겟위클리커버드콜":         "498400.KS",
    "TIGER 미국테크TOP10타겟커버드콜":     "474220.KS",
    "TIGER 현대차그룹플러스":             "138540.KS",
    "TIGER 미국S&P500타겟데일리커버드콜":  "482730.KS",
    "ACE 미국AI테크핵심산업액티브":        "0118Z0.KS",
    "ACE 미국빅테크7+데일리타겟커버드콜(합성)": "480020.KS",
    "SOL 팔란티어커버드콜OTM채권혼합":     "0040Y0.KS",
    "SOL 팔란티어미국채커버드콜혼합":      "0040X0.KS",
    "SOL 200타겟위클리커버드콜":          "0167B0.KS",
    "PLUS 자사주매입고배당주":            "0098N0.KS",
    "RISE 글로벌자산배분액티브":          "461490.KS",
    # 미국 개별주 / ETF
    "엔비디아":                   "NVDA",
    "AST 스페이스모바일":           "ASTS",
    "셀레스티카":                  "CLS",
    "아이렌":                     "IREN",
    "파가야 테크놀로지스":           "PGY",
    "퀀텀스케이프":                 "QS",
    "서프 에어 모빌리티":           "SRFM",
    "앰프리어스 테크놀로지스":        "AMPX",
    "BTQ 테크놀로지스":             "BTTX",
    "실스크":                     "LAES",
    "X-에너지":                   "XE",
    "Schwab 미국 배당주 ETF":      "SCHD",
    "TRDR 2X ASTS ETF":          "ASTX",
    "TRADR 2X LNG ETF":          "ONDL",
    "TRDR CLS DLY ETF":          "CSEX",
    "TRDR 2X CRDO ETF":          "CRDU",
    "TT DF 2XIREN ETF":          "IRE",
    "TRD2XLG APLD ETF":          "APLX",
    "DFC DLY RKLB ETF":          "RKLX",
    "Leverage Shares 2X Long CBRS DLY ETF": "CBRG",
    "RNDHL MEMRY ETF":           "DRAM",
    "RNDHLL INVTN ETF":          "QDTE",
}


@dataclass
class ForeignScore:
    """외국인 순매수 점수"""
    stock_name: str
    ticker: str = ""
    score: float = 0.0             # 0~100
    net_buy_5d: int = 0            # 5일 누적 순매수 (주)
    net_buy_today: int = 0         # 당일 순매수
    consecutive_buy: int = 0       # 연속 순매수 일수

    def to_dict(self) -> dict:
        return {
            "stock": self.stock_name,
            "ticker": self.ticker,
            "foreign_score": round(self.score, 1),
            "net_buy_5d": self.net_buy_5d,
            "net_buy_today": self.net_buy_today,
            "consecutive_buy": self.consecutive_buy,
        }


def _get_trading_dates(n: int = 5) -> tuple[str, str]:
    """최근 n 영업일 범위 (yyyymmdd 포맷)"""
    end = datetime.now()
    # 주말 건너뛰기 (간단 처리: 7일 전으로 잡고 KRX가 알아서 처리)
    start = end - timedelta(days=n + 4)
    return start.strftime("%Y%m%d"), end.strftime("%Y%m%d")


def _calc_score(net_5d: int, net_today: int, consecutive: int) -> float:
    """외국인 매수 강도 → 0~100 점수화"""
    score = 0.0
    # 5일 누적 순매수 (많을수록 높은 점수, 최대 50점)
    if net_5d > 0:
        score += min(50, net_5d / 10000)
    # 당일 순매수 (최대 30점)
    if net_today > 0:
        score += min(30, net_today / 5000)
    # 연속 매수일 (최대 20점)
    score += min(20, consecutive * 4)
    return round(min(100, score), 1)


def _scan_pykrx(stocks: list[str], start_date: str, end_date: str) -> list[ForeignScore]:
    """pykrx로 외국인 순매수 조회 (1순위)"""
    results = []
    try:
        df_all = krx.get_market_net_purchases_of_equities_by_ticker(
            start_date, end_date, "KOSPI"
        )
        if df_all is None or df_all.empty:
            return []

        # 역방향 매핑: 티커 → 종목명
        rev_map = {v: k for k, v in TICKER_MAP.items()}

        for ticker_code in df_all.index:
            stock_name = rev_map.get(ticker_code)
            if not stock_name or (stocks and stock_name not in stocks):
                continue
            for col in df_all.columns:
                if "외국인" in str(col):
                    net_5d = int(df_all.loc[ticker_code, col])
                    fs = ForeignScore(
                        stock_name=stock_name, ticker=ticker_code,
                        net_buy_5d=net_5d,
                    )
                    fs.score = _calc_score(net_5d, 0, 0)
                    results.append(fs)
                    break
    except Exception as e:
        print(f"[ForeignFilter] pykrx 실패: {e}")
    return results


def _scan_yfinance_proxy(stocks: list[str]) -> list[ForeignScore]:
    """yfinance 거래량 급등으로 외국인 매집 추정 (폴백)

    5일 평균 대비 거래량 비율이 높을수록 비정상 매집 가능성 높음
    """
    if not YFINANCE_AVAILABLE:
        return []

    results = []
    for stock_name in stocks:
        ticker_code = TICKER_MAP.get(stock_name)
        if not ticker_code:
            continue
        try:
            # 이미 .KS 포함(한국주식) 또는 미국 티커는 그대로, 아닌 경우만 .KS 추가
            yf_ticker = ticker_code if ('.KS' in ticker_code or '.' not in ticker_code and not ticker_code.isdigit()) else f"{ticker_code}.KS"
            # 순수 숫자 코드(한국주식)는 .KS 없이도 시도
            if ticker_code.replace('.KS','').isdigit():
                yf_ticker = ticker_code if '.KS' in ticker_code else f"{ticker_code}.KS"
            t = yf.Ticker(yf_ticker)
            hist = t.history(period="20d")
            if hist.empty or len(hist) < 6:
                continue

            vol_20d_avg = hist["Volume"].iloc[:-1].mean()
            vol_recent  = hist["Volume"].iloc[-5:].mean()
            vol_today   = hist["Volume"].iloc[-1]

            if vol_20d_avg == 0:
                continue

            # 거래량 비율 → 점수 (2배면 50점, 3배면 100점)
            ratio = vol_recent / vol_20d_avg
            score = min(100, (ratio - 1.0) * 50) if ratio > 1.0 else 0

            # 연속 거래량 증가일 계산
            vols = hist["Volume"].tolist()
            consecutive = 0
            for i in range(len(vols) - 1, 0, -1):
                if vols[i] > vols[i - 1]:
                    consecutive += 1
                else:
                    break

            fs = ForeignScore(
                stock_name=stock_name, ticker=ticker_code,
                score=round(score, 1),
                net_buy_today=int(vol_today),
                consecutive_buy=consecutive,
            )
            results.append(fs)
        except Exception:
            continue

    return results


def scan(target_stocks: Optional[list[str]] = None) -> list[ForeignScore]:
    """
    외국인 순매수 데이터 수집 → 종목별 점수 산출

    pykrx 1순위, 실패 시 yfinance 거래량 프록시로 폴백.

    Args:
        target_stocks: 대상 종목 리스트 (None이면 TICKER_MAP 전체)

    Returns:
        ForeignScore 리스트 (점수 내림차순)
    """
    stocks = target_stocks or list(TICKER_MAP.keys())
    start_date, end_date = _get_trading_dates(5)

    results = []

    # 1순위: pykrx
    if PYKRX_AVAILABLE:
        print(f"[ForeignFilter] pykrx 조회 중... ({start_date}~{end_date})")
        results = _scan_pykrx(stocks, start_date, end_date)

    # 폴백: yfinance 거래량 프록시
    if not results and YFINANCE_AVAILABLE:
        print("[ForeignFilter] pykrx 데이터 없음 -> yfinance 거래량 프록시 사용")
        results = _scan_yfinance_proxy(stocks)

    if not results:
        print("[ForeignFilter] 데이터 없음 — 외국인 필터 스킵")
        return []

    results.sort(key=lambda x: -x.score)
    print(f"[ForeignFilter] 완료 — {len(results)}개 종목 점수 산출")
    return results


if __name__ == "__main__":
    scores = scan()
    print("\n=== 외국인 순매수 TOP 10 ===")
    for fs in scores[:10]:
        print(f"  {fs.stock_name:15s} | 점수: {fs.score:5.1f} | 5일누적: {fs.net_buy_5d:>8,} | 연속매수: {fs.consecutive_buy}일")
