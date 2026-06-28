"""
kis_api.py — 한국투자증권 API 데이터 레이어
==============================================
KIS API 승인 전: mock 모드로 동작 (기존 시뮬레이션)
KIS API 승인 후: real 모드로 교체 (아래 설정만 변경)

설정 방법:
  1. kis_config.py 생성 (gitignore에 포함됨):
     APP_KEY    = "PSxxxxxx..."
     APP_SECRET = "xxxxxxxxx..."
     ACCOUNT_NO = "50123456-01"
     MODE       = "real"  # or "mock"
"""

from __future__ import annotations
import random
from typing import Optional


# ── 설정 로드 ──────────────────────────────────────────────────

def _load_config() -> dict:
    try:
        import kis_config
        return {
            "app_key":    getattr(kis_config, "APP_KEY", ""),
            "app_secret": getattr(kis_config, "APP_SECRET", ""),
            "account_no": getattr(kis_config, "ACCOUNT_NO", ""),
            "mode":       getattr(kis_config, "MODE", "mock"),
        }
    except ImportError:
        return {"mode": "mock"}


# ── 시장 데이터 ───────────────────────────────────────────────

class StockData:
    """개별 종목 시장 데이터"""
    def __init__(self, stock_name: str, current_price: float,
                 volume_ratio: float, ma5_position: str,
                 inst_net_buy: float, momentum: float):
        self.stock_name    = stock_name
        self.current_price = current_price
        self.volume_ratio  = volume_ratio   # 평균 대비 거래량 배율 (1.5 = 평균의 1.5배)
        self.ma5_position  = ma5_position   # "above" | "below" | "cross"
        self.inst_net_buy  = inst_net_buy   # 기관 순매수 비율 (-1 ~ +1)
        self.momentum      = momentum       # 모멘텀 점수 (-1 ~ +1)


class KISDataProvider:
    """
    KIS API 데이터 프로바이더
    MODE=mock → 시드 기반 결정론적 가상 데이터
    MODE=real → KIS REST API 실데이터
    """

    def __init__(self):
        cfg = _load_config()
        self.mode = cfg.get("mode", "mock")
        self._token: Optional[str] = None

        if self.mode == "real":
            self._app_key    = cfg["app_key"]
            self._app_secret = cfg["app_secret"]
            self._account_no = cfg["account_no"]

    # ── public API ────────────────────────────────────────────

    def get_stock_data(self, stock_name: str, current_price: float) -> StockData:
        if self.mode == "real":
            return self._fetch_real(stock_name, current_price)
        return self._mock(stock_name, current_price)

    def get_portfolio(self) -> list[dict]:
        """보유 종목 목록 조회 (실계좌)"""
        if self.mode == "real":
            return self._fetch_portfolio_real()
        return []

    def is_mock(self) -> bool:
        return self.mode == "mock"

    # ── mock 구현 ─────────────────────────────────────────────

    def _mock(self, stock_name: str, current_price: float) -> StockData:
        rng = random.Random(hash(stock_name) % 1000)
        return StockData(
            stock_name    = stock_name,
            current_price = current_price,
            volume_ratio  = round(0.5 + rng.random() * 2.5, 2),
            ma5_position  = rng.choice(["above", "above", "below", "cross"]),
            inst_net_buy  = round(-0.5 + rng.random() * 1.2, 2),
            momentum      = round(-0.3 + rng.random() * 1.3, 2),
        )

    # ── real 구현 (KIS API 승인 후 채울 것) ───────────────────

    def _get_token(self) -> str:
        """OAuth 토큰 발급 (1일 유효)"""
        if self._token:
            return self._token
        import requests
        resp = requests.post(
            "https://openapi.koreainvestment.com:9443/oauth2/tokenP",
            json={
                "grant_type": "client_credentials",
                "appkey":     self._app_key,
                "appsecret":  self._app_secret,
            },
            timeout=10
        )
        resp.raise_for_status()
        self._token = resp.json()["access_token"]
        return self._token

    def _fetch_real(self, stock_name: str, current_price: float) -> StockData:
        """
        실데이터 조회 — KIS 현재가 + 거래량 + 이평선 + 기관수급
        TODO: KIS API 승인 후 구현
        """
        raise NotImplementedError("KIS API 승인 후 구현 예정 — 현재는 mock 모드 사용")

    def _fetch_portfolio_real(self) -> list[dict]:
        """실계좌 보유 종목 조회"""
        raise NotImplementedError("KIS API 승인 후 구현 예정")
