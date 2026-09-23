# daily_run.py — ImproveStock v1.1 일일 자동 분석 파이프라인
# 실행: python D:\AI\Improve_stock\daily_run.py
# 스케줄: master_watch.py daily_scheduler 15:35 자동 실행

import sys
import json
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

from core.combined_scorer import run, _send_telegram, W_VCP, W_FOREIGN, W_NARRATIVE
from core.signal_types import SignalGrade


def main():
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    print(f"[ImproveStock v1.1] 일일 분석 시작 — {now}")

    results = run(vcp_scores=None, notify=False, top_n=10)

    if not results:
        _send_telegram(f"📊 <b>ImproveStock v1.1</b> [{now}]\n데이터 수집 실패 — 재시도 필요")
        return

    # 등급별 분류
    buy_candidates = [r for r in results if r.grade.buyable]
    watch_candidates = [r for r in results if r.grade == SignalGrade.B]
    top10 = results[:10]

    # 텔레그램 메시지 구성
    lines = [f"📊 <b>ImproveStock v1.1 일일 분석</b>"]
    lines.append(f"⏰ {now}")
    lines.append(f"📈 분석 종목: {len(results)}개\n")

    if buy_candidates:
        lines.append("🔥 <b>매수 후보 (A/S 등급)</b>")
        for r in buy_candidates[:5]:
            lines.append(f"  {str(r.grade)} {r.stock_name} | {r.score:.0f}점\n  └ {r.reason}")
    else:
        lines.append("⏸ 오늘 A/S 등급 매수 후보 없음")

    if watch_candidates:
        lines.append(f"\n👀 <b>관심 종목 (B 등급)</b>")
        for r in watch_candidates[:3]:
            lines.append(f"  {r.stock_name} | {r.score:.0f}점 | {r.reason}")

    lines.append(f"\n📊 상위 3종목:")
    for i, r in enumerate(top10[:3], 1):
        lines.append(f"  {i}. {r.stock_name} [{r.grade.value}] {r.score:.0f}점")

    lines.append(f"\n⚖️ 가중치: 외국인 {W_FOREIGN*100:.0f}% / 뉴스 {W_NARRATIVE*100:.0f}% (VCP 미적용)")

    _send_telegram("\n".join(lines))
    print(f"[ImproveStock v1.1] 텔레그램 발송 완료 — 매수후보 {len(buy_candidates)}개, 관심 {len(watch_candidates)}개")

    # 결과 JSON 저장
    out_path = Path(__file__).parent / "output" / f"daily_{datetime.now().strftime('%Y%m%d')}.json"
    out_path.parent.mkdir(exist_ok=True)
    out_path.write_text(
        json.dumps([r.to_dict() for r in results], ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    print(f"[ImproveStock v1.1] 결과 저장 → {out_path}")


if __name__ == "__main__":
    main()
