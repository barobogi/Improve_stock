"""
vcp_scanner.py — VCP (Volatility Contraction Pattern) 스캐너
=============================================================
Reference: AQ8MiLHaKPs (호두 채널 VCP 스캐너)
VCP: 가격 변동성이 단계적으로 수축 → 돌파 직전 패턴 감지
"""
import random, math
from typing import List
from core.signal_types import PortfolioItem, VCPattern


class VCPScanner:
    """VCP 패턴 감지 엔진"""

    def scan(self, items: List[PortfolioItem]) -> List[VCPattern]:
        """포트폴리오 전체 VCP 스캔"""
        results = []
        for item in items:
            vcp = self._check_pattern(item)
            if vcp.score > 0:
                results.append(vcp)
        results.sort(key=lambda v: -v.score)
        return results

    def _check_pattern(self, item: PortfolioItem) -> VCPattern:
        """개별 종목 VCP 패턴 체크 (모의 데이터 기반)"""
        rng = random.Random(hash(item.stock_name) % 1000)
        price = item.current_price

        # 수축 단계 (1~4)
        contraction_count = rng.randint(0, 4)

        # 변동성 축소율 (최대폭 대비 현재 변동성 %)
        contraction_pct = round(5 + rng.random() * 35, 1) if contraction_count > 0 else 0

        # 거래량 추세
        vol_trend = rng.choice(["declining", "stable", "stable", "declining"])

        # 돌파 임박?
        breakout = contraction_count >= 3 and contraction_pct < 15

        # 점수
        score = 0
        if contraction_count >= 3: score += 40
        elif contraction_count >= 2: score += 25
        elif contraction_count >= 1: score += 10

        if vol_trend == "declining": score += 20
        if breakout: score += 30
        if "커버드콜" not in item.stock_name: score += 10  # 개별주 우대

        score = min(100, max(0, score))

        # apex 가격대
        apex_low = round(price * 0.95, -1) if price else 0
        apex_high = round(price * 1.02, -1) if price else 0

        desc = ""
        if breakout: desc = f"🔥 VCP 포착! {contraction_count}차 수렴 완료 — 돌파 임박!"
        elif contraction_count >= 2: desc = f"👀 VCP 진행중 — {contraction_count}차 수렴 (축소율 {contraction_pct}%)"
        elif contraction_count == 1: desc = f"🔍 초기 VCP 감지 — 모니터링 필요"
        else: desc = "VCP 패턴 없음"

        return VCPattern(
            stock_name=item.stock_name,
            detected=breakout or contraction_count >= 2,
            contraction_count=contraction_count,
            contraction_pct=contraction_pct,
            volume_trend=vol_trend,
            breakout_imminent=breakout,
            apex_price_range=(apex_low, apex_high),
            score=score, description=desc
        )


if __name__ == "__main__":
    items = [PortfolioItem(1,"일반","삼성전자",118,362500,42775000,16842022,"주식"),
             PortfolioItem(2,"일반","팔란티어",102,128470,19823640,15675163,"해외증권"),
             PortfolioItem(2,"일반","셀레스티카",20,372550,11271872,4450910,"해외증권")]
    vcps = VCPScanner().scan(items)
    for v in vcps:
        print(f"  {'🔥' if v.breakout_imminent else '👀'} {v.stock_name:20s} 점수:{v.score:.0f} | {v.description}")
    print("OK")
