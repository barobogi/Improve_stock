"""
signal_types.py — 공통 데이터 타입 정의
=========================================
호두 채널 등급 시스템 + 대시보드 포트폴리오 구조를 연결하는
표준 데이터 모델.

Reference: bnsMfTHITYs (종가베팅 등급 시스템)
Reference: stock_automation_7steps.md (7단계 분할 개발법)
"""

from dataclasses import dataclass, field, asdict
from typing import Optional
from enum import Enum
from datetime import datetime


# ──────────────────────────────────────────────
# 등급 시스템 (호두 채널 기준)
# ──────────────────────────────────────────────

class SignalGrade(Enum):
    """종목 등급 — S/A/B/C/D (호두 채널 등급 시스템)"""
    S = "S"   # 초강력 매수 — 모든 조건 충족 + 추가 모멘텀
    A = "A"   # 강력 매수 — 거래량 급등 + 5일선 위 + 기관 순매수
    B = "B"   # 관심 — 일부 조건 충족, 추가 확인 필요
    C = "C"   # 관망 — 5일선 이탈, 조건 미달
    D = "D"   # 제외 — 하락 추세, 거래량 부족

    def __str__(self):
        icons = {SignalGrade.S: "🔥 S", SignalGrade.A: "✅ A",
                 SignalGrade.B: "👀 B", SignalGrade.C: "⏸ C", SignalGrade.D: "❌ D"}
        return icons[self]

    @property
    def buyable(self) -> bool:
        """매수 대상 등급인가? (S, A만 매수)"""
        return self in (SignalGrade.S, SignalGrade.A)


class ActionType(Enum):
    """권장 액션"""
    BUY = "BUY"
    HOLD = "HOLD"
    SELL = "SELL"
    WATCH = "WATCH"
    SKIP = "SKIP"


# ──────────────────────────────────────────────
# 포트폴리오 아이템 (대시보드 ↔ 엔진 공통)
# ──────────────────────────────────────────────

@dataclass
class PortfolioItem:
    """개별 보유 종목 정보"""
    account_id: int
    account_name: str
    stock_name: str
    quantity: int
    current_price: float
    eval_amount: float
    buy_amount: float
    stock_type: str  # '주식', '해외증권', '수익증권'

    @property
    def return_pct(self) -> float:
        """수익률 (%)"""
        if self.buy_amount == 0:
            return 0.0
        return ((self.eval_amount - self.buy_amount) / self.buy_amount) * 100

    @property
    def profit_loss(self) -> float:
        """손익 금액"""
        return self.eval_amount - self.buy_amount


@dataclass
class AccountInfo:
    """계좌 정보"""
    account_id: int
    name: str
    number: str
    account_type: str  # general, isa, irp, pension
    description: str


# ──────────────────────────────────────────────
# 분석 결과
# ──────────────────────────────────────────────

@dataclass
class SignalResult:
    """개별 종목 분석 결과"""
    stock_name: str
    grade: SignalGrade
    action: ActionType
    score: float           # 0~100 점수
    reason: str            # 등급 산출 이유
    target_price: Optional[float] = None    # 목표가 (+9%)
    stop_loss: Optional[float] = None       # 손절가 (-5%)
    entry_price: Optional[float] = None     # 진입가
    confidence: float = 0.0                 # 신뢰도 0~1
    details: dict = field(default_factory=dict)  # 상세 분석 데이터

    def to_dict(self) -> dict:
        """대시보드 호환 dict 변환"""
        return {
            "stock": self.stock_name,
            "grade": self.grade.value,
            "action": self.action.value,
            "score": round(self.score, 1),
            "reason": self.reason,
            "target_price": self.target_price,
            "stop_loss": self.stop_loss,
            "entry_price": self.entry_price,
            "confidence": round(self.confidence, 2),
            "details": self.details,
            "grade_icon": str(self.grade),
        }


@dataclass
class AnalysisReport:
    """통합 분석 리포트"""
    generated_at: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    signals: list = field(default_factory=list)
    vcp_signals: list = field(default_factory=list)
    summary: dict = field(default_factory=dict)
    portfolio_stats: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "generated_at": self.generated_at,
            "total_signals": len(self.signals),
            "buyable_count": len([s for s in self.signals if s.grade.buyable]),
            "signals": [s.to_dict() for s in self.signals],
            "vcp_signals": [s.to_dict() if isinstance(s, SignalResult) else s for s in self.vcp_signals],
            "summary": self.summary,
            "portfolio_stats": self.portfolio_stats,
        }


# ──────────────────────────────────────────────
# VCP 패턴 데이터
# ──────────────────────────────────────────────

@dataclass
class VCPattern:
    """VCP (Volatility Contraction Pattern) 감지 결과"""
    stock_name: str
    detected: bool
    contraction_count: int          # 수렴 횟수
    contraction_pct: float          # 현재 변동성 축소율 (%)
    volume_trend: str               # 'declining', 'stable', 'increasing'
    breakout_imminent: bool         # 돌파 임박?
    days_to_breakout: Optional[int] = None  # 예상 돌파까지 남은 일수
    apex_price_range: tuple = None  # (하단, 상단) 수렴 끝단 가격대
    score: float = 0.0
    description: str = ""

    def to_dict(self) -> dict:
        return {
            "stock": self.stock_name,
            "detected": self.detected,
            "contraction_count": self.contraction_count,
            "contraction_pct": self.contraction_pct,
            "volume_trend": self.volume_trend,
            "breakout_imminent": self.breakout_imminent,
            "score": round(self.score, 1),
            "description": self.description,
        }
