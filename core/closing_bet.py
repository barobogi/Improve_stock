"""
closing_bet.py — 종가베팅 등급 분석 엔진
=========================================
Reference: bnsMfTHITYs (호두 채널 종가베팅 시스템)
참고: stock_automation_7steps.md (Step 3~4)
"""

import random
from typing import List, Optional
from core.signal_types import (
    PortfolioItem, SignalResult, SignalGrade, ActionType,
    AnalysisReport
)

class ClosingBetEngine:
    """종가베팅 분석 엔진 — 호두 채널 S/A/B/C/D 등급"""

    TARGET_PCT = 0.09
    STOP_LOSS_PCT = -0.05
    VOLUME_SURGE_THRESHOLD = 1.5

    def __init__(self):
        self._mock_prices = {}

    def analyze_portfolio(self, items):
        """전체 분석 → SignalResult 리스트 (등급순)"""
        results = [self._analyze_single(i) for i in items]
        order = {"S": 0, "A": 1, "B": 2, "C": 3, "D": 4}
        results.sort(key=lambda r: (order.get(r.grade.value, 99), -r.score))
        return results

    def _analyze_single(self, item):
        mock = self._mock(item)
        grade, score, reasons = self._grade(item, mock)
        return SignalResult(
            stock_name=item.stock_name, grade=grade, action=self._action(grade),
            score=score, reason=" | ".join(reasons[:2]),
            entry_price=item.current_price, confidence=self._conf(grade, mock),
            details={"return_pct": round(item.return_pct, 1),
                     "volume": mock["vol"], "ma": mock["ma"],
                     "inst": mock["inst"], "mom": round(mock["mom"], 1)}
        )

    def _grade(self, item, m):
        """S/A/B/C/D 등급 판정 (호두 채널 기준)"""
        r, s = [], 50.0
        if m["ma"] == "above": s += 15; r.append("5일선 위")
        else: s -= 15; r.append("5일선 이탈")
        if m["vol"] >= 1.5: s += 20; r.append(f"거래량↑({m['vol']:.1f}x)")
        elif m["vol"] < 0.8: s -= 10; r.append("거래량↓")
        if m["inst"] > 0.2: s += 20; r.append("기관 매수")
        elif m["inst"] < -0.2: s -= 15
        if m["mom"] > 0.5: s += 15; r.append(f"모멘텀({m['mom']:.1f})")
        s = max(0, min(100, s))
        if s >= 80: g = SignalGrade.S if m["mom"] > 0.7 else SignalGrade.A
        elif s >= 60: g = SignalGrade.B
        elif s >= 40: g = SignalGrade.C
        else: g = SignalGrade.D
        return g, s, r

    def _action(self, g):
        if g in (SignalGrade.S, SignalGrade.A): return ActionType.BUY
        if g == SignalGrade.B: return ActionType.WATCH
        return ActionType.HOLD if g == SignalGrade.C else ActionType.SKIP

    def _conf(self, g, m):
        base = {"S": 0.85, "A": 0.70, "B": 0.50, "C": 0.30, "D": 0.15}
        return min(1.0, base.get(g.value, 0.5) + m["mom"] * 0.1)

    def _mock(self, item):
        n = item.stock_name
        if n not in self._mock_prices:
            r = random.Random(hash(n) % 1000)
            self._mock_prices[n] = dict(
                vol=round(0.5+r.random()*2.5, 2),
                ma=r.choice(["above","above","below","cross"]),
                inst=round(-0.5+r.random()*1.2, 2),
                mom=round(-0.3+r.random()*1.3, 2))
        return self._mock_prices[n]

