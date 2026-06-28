"""
dashboard_adapter.py — 대시보드 데이터 ↔ 분석 엔진 연결 어댑터
==============================================================
목적: barobogi.github.io 대시보드의 포트폴리오 JSON을 읽어서
      분석 엔진이 사용하는 PortfolioItem으로 변환 + 결과를 대시보드 형식으로 출력
"""
import json, os
from typing import List, Optional
from core.signal_types import PortfolioItem, AccountInfo, AnalysisReport


class DashboardAdapter:
    """
    대시보드 ↔ 분석 엔진 연결 어댑터

    입력: 대시보드 JSON 포맷 (sample_portfolio.json)
    출력: PortfolioItem[] → ClosingBetEngine/VCPScanner
    결과: 대시보드 호환 JSON (output/report_*.json)
    """

    def __init__(self, data_path: Optional[str] = None):
        self.data_path = data_path or os.path.join(
            os.path.dirname(__file__), "..", "data", "sample_portfolio.json"
        )

    def load_portfolio(self) -> List[PortfolioItem]:
        """대시보드 JSON → PortfolioItem 리스트 변환"""
        with open(self.data_path, "r", encoding="utf-8") as f:
            raw = json.load(f)

        items = []
        accounts = {a["id"]: a["name"] for a in raw.get("accounts", [])}

        for s in raw.get("stocks", []):
            item = PortfolioItem(
                account_id=s["accountId"],
                account_name=accounts.get(s["accountId"], f"계좌{s['accountId']}"),
                stock_name=s["name"],
                quantity=s["qty"],
                current_price=float(s["curPrice"]),
                eval_amount=float(s["evalAmount"]),
                buy_amount=float(s["buyAmount"]),
                stock_type=s["type"],
            )
            items.append(item)

        self._raw_data = raw
        return items

    def get_accounts(self) -> List[AccountInfo]:
        """계좌 정보 로드"""
        with open(self.data_path, "r", encoding="utf-8") as f:
            raw = json.load(f)
        return [AccountInfo(a["id"], a["name"], a["num"], a["type"], a["desc"])
                for a in raw.get("accounts", [])]

    def to_dashboard_format(self, report: AnalysisReport) -> dict:
        """분석 리포트 → 대시보드 호환 JSON 변환"""
        return {
            "generated_at": report.generated_at,
            "dashboard_version": "v1.0",
            "intended_for": "barobogi.github.io — 시그널 위젯 연동",
            "portfolio_stats": {
                "total_portfolio": report.portfolio_stats.get("total_eval", 0),
                "total_invested": report.portfolio_stats.get("total_buy", 0),
                "total_pnl": report.portfolio_stats.get("total_pnl", 0),
            },
            "closing_bet": {
                "total_analyzed": report.summary.get("total", 0),
                "buyable_signals": report.summary.get("buyable", 0),
                "grade_distribution": report.summary.get("distribution", {}),
                "signals": [self._signal_to_widget(s) for s in report.signals],
            },
            "vcp_scanner": {
                "total_detected": len(report.vcp_signals),
                "patterns": [v.to_dict() if hasattr(v, 'to_dict') else v
                            for v in report.vcp_signals],
            },
            "integration_guide": (
                "이 JSON을 대시보드의 stock-dashboard.html에 "
                "fetch('/output/report_*.json')로 읽어서 "
                "'📊 AI 분석' 탭에 표시하세요."
            ),
        }

    def _signal_to_widget(self, signal) -> dict:
        """SignalResult → 대시보드 위젯 데이터"""
        return {
            "stock": signal.stock_name,
            "grade": signal.grade.value,
            "grade_display": str(signal.grade),
            "score": round(signal.score, 1),
            "action": signal.action.value,
            "reason": signal.reason,
            "consistency": round(signal.confidence, 2),
            "details": signal.details,
        }
