"""
yfinance_provider.py — yfinance 기반 실데이터 프로바이더
KIS API 승인 전까지 yfinance로 실데이터 연동.

ticker_map.json에 종목 추가 → 자동 반영 (코드 수정 불필요)
"""
import json
import os

import yfinance as yf

from core.kis_api import StockData

TICKER_MAP_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "ticker_map.json")


def _load_ticker_map() -> dict:
    with open(TICKER_MAP_PATH, encoding="utf-8") as f:
        return json.load(f)


class YFinanceProvider:
    """
    yfinance 기반 실데이터 프로바이더.
    - ticker_map.json 에서 티커 자동 조회
    - 종가 / 거래량비율 / 5일MA / 모멘텀 자동 계산
    - 기관수급(inst_net_buy)은 yfinance 미제공 → 0.0 고정 (KIS 승인 후 교체)
    """

    def __init__(self):
        self._ticker_map = _load_ticker_map()

    def reload(self):
        """ticker_map.json 재로드 (새 종목 추가 즉시 반영)"""
        self._ticker_map = _load_ticker_map()

    def get_stock_data(self, stock_name: str, current_price: float) -> StockData:
        ticker = self._resolve_ticker(stock_name)
        if not ticker:
            return self._neutral(stock_name, current_price)

        try:
            hist = yf.Ticker(ticker).history(period="20d")
            if hist.empty or len(hist) < 2:
                return self._neutral(stock_name, current_price)

            close      = float(hist["Close"].iloc[-1])
            vol_today  = float(hist["Volume"].iloc[-1])
            vol_avg    = float(hist["Volume"].iloc[:-1].mean()) or 1.0
            vol_ratio  = round(vol_today / vol_avg, 2)

            window = min(5, len(hist))
            ma5    = float(hist["Close"].iloc[-window:].mean())
            if close > ma5 * 1.002:
                ma5_pos = "above"
            elif close < ma5 * 0.998:
                ma5_pos = "below"
            else:
                ma5_pos = "cross"

            # 모멘텀: 최근 10일 수익률을 -1~+1로 정규화
            lookback = min(10, len(hist))
            raw_mom  = (close - float(hist["Close"].iloc[-lookback])) / float(hist["Close"].iloc[-lookback])
            momentum = max(-1.0, min(1.0, round(raw_mom * 5, 2)))

            return StockData(
                stock_name    = stock_name,
                current_price = close,
                volume_ratio  = vol_ratio,
                ma5_position  = ma5_pos,
                inst_net_buy  = 0.0,
                momentum      = momentum,
            )
        except Exception:
            return self._neutral(stock_name, current_price)

    def get_all_stocks(self) -> list[dict]:
        """
        ticker_map.json 에서 분석 가능한 종목 전체 반환.
        SKIP 종목, TODO 티커 자동 제외.
        반환: [{"name": ..., "ticker": ..., "type": ...}, ...]
        """
        self.reload()
        result = []
        for name, info in self._ticker_map.items():
            if info.get("market") == "SKIP":
                continue
            ticker = info.get("ticker")
            if not ticker or ticker == "TODO":
                continue
            result.append({
                "name":   name,
                "ticker": ticker,
                "type":   info.get("type", "주식"),
                "market": info.get("market", ""),
            })
        return result

    def is_mock(self) -> bool:
        return False

    def _resolve_ticker(self, stock_name: str):
        info   = self._ticker_map.get(stock_name, {})
        ticker = info.get("ticker")
        if not ticker or ticker == "TODO":
            return None
        return ticker

    def _neutral(self, stock_name: str, current_price: float) -> StockData:
        """티커 없거나 조회 실패 시 중립값 반환"""
        return StockData(
            stock_name    = stock_name,
            current_price = current_price,
            volume_ratio  = 1.0,
            ma5_position  = "below",
            inst_net_buy  = 0.0,
            momentum      = 0.0,
        )
