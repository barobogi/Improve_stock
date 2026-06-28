"""
closing_bet.py — 종가베팅 등급 분석 엔진
=========================================
Reference: bnsMfTHITYs (호두 채널 종가베팅 시스템)
참고: stock_automation_7steps.md (Step 3~4)
"""

from typing import List, Optional
from core.signal_types import (
    PortfolioItem, SignalResult, SignalGrade, ActionType,
    AnalysisReport
)
from core.kis_api import KISDataProvider


class ClosingBetEngine:
    """종가베팅 분석 엔진 — 호두 채널 S/A/B/C/D 등급"""

    TARGET_PCT = 0.09
    STOP_LOSS_PCT = -0.05
    VOLUME_SURGE_THRESHOLD = 1.5

    def __init__(self, data_provider: Optional[KISDataProvider] = None):
        self._provider = data_provider or KISDataProvider()

    def analyze_portfolio(self, items):
        """전체 분석 → SignalResult 리스트 (등급순)"""
        results = [self._analyze_single(i) for i in items]
        order = {"S": 0, "A": 1, "B": 2, "C": 3, "D": 4}
        results.sort(key=lambda r: (order.get(r.grade.value, 99), -r.score))
        return results

    def generate_report(self, items) -> AnalysisReport:
        """전체 분석 리포트 생성"""
        signals = self.analyze_portfolio(items)
        buyable = [s for s in signals if s.grade.buyable]
        dist = {}
        for s in signals:
            dist[s.grade.value] = dist.get(s.grade.value, 0) + 1
        total_eval = sum(i.eval_amount for i in items)
        total_buy  = sum(i.buy_amount  for i in items)
        report = AnalysisReport(signals=signals)
        report.summary = {"total": len(signals), "buyable": len(buyable), "distribution": dist}
        report.portfolio_stats = {
            "total_eval": total_eval,
            "total_buy":  total_buy,
            "total_pnl":  total_eval - total_buy,
        }
        return report

    def is_mock(self) -> bool:
        return self._provider.is_mock()

    def _analyze_single(self, item):
        data = self._provider.get_stock_data(item.stock_name, item.current_price)
        m = {
            "vol":  data.volume_ratio,
            "ma":   data.ma5_position,
            "inst": data.inst_net_buy,
            "mom":  data.momentum,
        }
        grade, score, reasons = self._grade(item, m)
        return SignalResult(
            stock_name=item.stock_name, grade=grade, action=self._action(grade),
            score=score, reason=" | ".join(reasons[:2]),
            entry_price=item.current_price, confidence=self._conf(grade, m),
            details={"return_pct": round(item.return_pct, 1),
                     "volume": m["vol"], "ma": m["ma"],
                     "inst": m["inst"], "mom": round(m["mom"], 1)}
        )

    def _grade(self, item, m):
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
