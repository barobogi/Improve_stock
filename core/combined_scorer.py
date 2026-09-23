# combined_scorer.py — VCP + 외국인매수 + 내러티브 3중 필터 합산 + 텔레그램 알림
import json
import urllib.request
from dataclasses import dataclass, field
from typing import Optional
from pathlib import Path

from core.signal_types import SignalGrade, ActionType, SignalResult
from core.narrative_scanner import NarrativeScore, scan as narrative_scan
from core.foreign_filter import ForeignScore, scan as foreign_scan

TELEGRAM_TOKEN   = "8850996295:AAHXKedqZflR71jhDTR0MKutjxBdHWfxNAo"
TELEGRAM_CHAT_ID = "465471725"

# 가중치 (v1.1 초기값 — 추후 장세별 동적 조정 예정)
W_VCP       = 0.5
W_FOREIGN   = 0.2
W_NARRATIVE = 0.3


def _send_telegram(msg: str):
    try:
        payload = json.dumps({
            "chat_id": TELEGRAM_CHAT_ID,
            "text": msg,
            "parse_mode": "HTML",
        }).encode()
        req = urllib.request.Request(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        urllib.request.urlopen(req, timeout=10)
    except Exception as e:
        print(f"[CombinedScorer] 텔레그램 실패: {e}")


def _grade_from_score(score: float) -> tuple[SignalGrade, ActionType]:
    if score >= 80:
        return SignalGrade.S, ActionType.BUY
    elif score >= 60:
        return SignalGrade.A, ActionType.BUY
    elif score >= 40:
        return SignalGrade.B, ActionType.WATCH
    elif score >= 20:
        return SignalGrade.C, ActionType.HOLD
    else:
        return SignalGrade.D, ActionType.SKIP


def run(
    vcp_scores: Optional[dict[str, float]] = None,
    notify: bool = True,
    top_n: int = 10,
) -> list[SignalResult]:
    """
    3중 필터 합산 실행

    Args:
        vcp_scores: {종목명: vcp점수(0~100)} — 없으면 VCP 가중치 제외
        notify: True면 상위 종목 텔레그램 알림
        top_n: 알림/반환할 상위 종목 수

    Returns:
        SignalResult 리스트 (점수 내림차순)
    """
    print("[CombinedScorer] 3중 필터 분석 시작")

    # 1. 내러티브 스캔
    narrative_results: list[NarrativeScore] = narrative_scan()
    narrative_map = {ns.stock_name: ns for ns in narrative_results}

    # 2. 외국인 매수 스캔
    foreign_results: list[ForeignScore] = foreign_scan()
    foreign_map = {fs.stock_name: fs for fs in foreign_results}

    # 3. 전체 종목 집합
    all_stocks = set(narrative_map) | set(foreign_map)
    if vcp_scores:
        all_stocks |= set(vcp_scores)

    # 4. 합산
    results = []
    for stock in all_stocks:
        ns = narrative_map.get(stock)
        fs = foreign_map.get(stock)
        vcp_s = (vcp_scores or {}).get(stock, 0.0)

        n_score = ns.score if ns else 0.0
        f_score = fs.score if fs else 0.0

        if vcp_scores:
            combined = vcp_s * W_VCP + f_score * W_FOREIGN + n_score * W_NARRATIVE
        else:
            # VCP 없으면 나머지 비율 재분배
            w_f = W_FOREIGN / (W_FOREIGN + W_NARRATIVE)
            w_n = W_NARRATIVE / (W_FOREIGN + W_NARRATIVE)
            combined = f_score * w_f + n_score * w_n

        grade, action = _grade_from_score(combined)

        themes = ns.themes if ns else []
        headline = ns.top_headline if ns else ""
        reason_parts = []
        if n_score > 0:
            reason_parts.append(f"뉴스테마({', '.join(themes[:2])})")
        if f_score > 0:
            reason_parts.append(f"외국인매수({f_score:.0f}점)")
        if vcp_s > 0:
            reason_parts.append(f"VCP({vcp_s:.0f}점)")

        sr = SignalResult(
            stock_name=stock,
            grade=grade,
            action=action,
            score=round(combined, 1),
            reason=" | ".join(reason_parts) if reason_parts else "신호 없음",
            confidence=round(combined / 100, 2),
            details={
                "vcp_score": vcp_s,
                "foreign_score": f_score,
                "narrative_score": n_score,
                "themes": themes,
                "top_headline": headline,
            },
        )
        results.append(sr)

    results.sort(key=lambda x: -x.score)
    top = [r for r in results if r.grade.buyable][:top_n]

    print(f"[CombinedScorer] 완료 — 전체 {len(results)}개, 매수후보 {len(top)}개")

    # 5. 텔레그램 알림
    if notify and top:
        lines = ["<b>📊 Improve_stock v1.1 매수 후보</b>"]
        for i, r in enumerate(top[:5], 1):
            lines.append(
                f"\n{i}. <b>{r.stock_name}</b> [{r.grade.value}등급] {r.score:.0f}점\n"
                f"   {r.reason}"
            )
        lines.append(f"\n가중치: VCP {W_VCP*100:.0f}% / 외국인 {W_FOREIGN*100:.0f}% / 뉴스 {W_NARRATIVE*100:.0f}%")
        _send_telegram("\n".join(lines))
        print("[CombinedScorer] 텔레그램 알림 발송 완료")

    return results


if __name__ == "__main__":
    results = run(notify=True)
    print("\n=== TOP 10 매수 후보 ===")
    for r in results[:10]:
        print(f"  {r.stock_name:15s} | {str(r.grade):6s} | {r.score:5.1f}점 | {r.reason}")
