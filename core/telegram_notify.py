"""
telegram_notify.py — 텔레그램 시그널 알림
==========================================
분석 결과(SignalResult 리스트)를 텔레그램 메시지로 전송.

설정:
  kis_config.py에 추가:
    TELEGRAM_BOT_TOKEN = "123456:ABCxxx..."
    TELEGRAM_CHAT_ID   = "465471725"

또는 환경변수:
    TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
"""

from __future__ import annotations
import os
from datetime import datetime
from typing import Optional


def _load_telegram_config() -> tuple[Optional[str], Optional[str]]:
    token   = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    try:
        import kis_config
        token   = token   or getattr(kis_config, "TELEGRAM_BOT_TOKEN", None)
        chat_id = chat_id or getattr(kis_config, "TELEGRAM_CHAT_ID", None)
    except ImportError:
        pass
    return token, chat_id


def send_signal_report(signals: list, vcp_signals: list, is_mock: bool = True) -> bool:
    """
    분석 결과를 텔레그램으로 전송.
    Returns True if sent, False if config missing (dry-run).
    """
    token, chat_id = _load_telegram_config()

    msg = _build_message(signals, vcp_signals, is_mock)
    print(msg)  # 항상 콘솔 출력

    if not token or not chat_id:
        print("\n[텔레그램 미설정] kis_config.py에 TELEGRAM_BOT_TOKEN + TELEGRAM_CHAT_ID 추가 필요")
        return False

    import requests
    resp = requests.post(
        f"https://api.telegram.org/bot{token}/sendMessage",
        json={"chat_id": chat_id, "text": msg, "parse_mode": "HTML"},
        timeout=10
    )
    resp.raise_for_status()
    return True


def _build_message(signals: list, vcp_signals: list, is_mock: bool) -> str:
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    mode_tag = "🔶 [시뮬레이션]" if is_mock else "🟢 [실데이터]"

    buyable = [s for s in signals if s.grade.buyable]
    breakout = [v for v in vcp_signals if v.breakout_imminent]

    lines = [
        f"<b>📊 Improve_stock 종가베팅 시그널</b>",
        f"{mode_tag} {now}",
        "",
    ]

    if buyable:
        lines.append(f"<b>🔥 매수 검토 ({len(buyable)}개)</b>")
        for s in buyable[:5]:
            grade_icon = {"S": "🔥S", "A": "✅A"}.get(s.grade.value, s.grade.value)
            lines.append(f"  {grade_icon} <b>{s.stock_name}</b> {s.score:.0f}점 | {s.reason}")
    else:
        lines.append("오늘 매수 대상 없음")

    if breakout:
        lines.append(f"\n<b>📈 VCP 돌파임박 ({len(breakout)}개)</b>")
        for v in breakout[:3]:
            lines.append(f"  🔥 {v.stock_name}: {v.description}")

    lines.append(f"\n전체 분석: {len(signals)}종목 | S/A: {len(buyable)}개")

    return "\n".join(lines)
