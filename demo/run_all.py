"""
run_all.py — 통합 데모 실행기
==============================
"바로보기 대시보드 ↔ 호두 인사이트" 연결 시뮬레이션

실행: python demo/run_all.py
결과: output/ 폴더에 JSON 리포트 + 콘솔 출력
"""
import os, sys, json
from datetime import datetime

# 경로 설정
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from integration.dashboard_adapter import DashboardAdapter
from core.closing_bet import ClosingBetEngine
from core.vcp_scanner import VCPScanner
from core.signal_types import SignalGrade


def print_header(title):
    w = 60
    print(f"\n{'='*w}")
    print(f"  {title}")
    print(f"{'='*w}")


def main():
    OUTPUT_DIR = os.path.join(ROOT, "output")
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # ─────────────────────────────────────────────
    # Step 1: 대시보드 포트폴리오 로드
    # ─────────────────────────────────────────────
    print_header("📥 Step 1: 대시보드 포트폴리오 로드")
    adapter = DashboardAdapter(os.path.join(ROOT, "data", "sample_portfolio.json"))
    items = adapter.load_portfolio()
    accounts = adapter.get_accounts()
    print(f"  계좌: {len(accounts)}개")
    print(f"  종목: {len(items)}개")
    print(f"  총 평가금액: ₩{sum(i.eval_amount for i in items):,}")
    print(f"  총 매수금액: ₩{sum(i.buy_amount for i in items):,}")

    # ─────────────────────────────────────────────
    # Step 2: 종가베팅 분석
    # ─────────────────────────────────────────────
    print_header("🔥 Step 2: 종가베팅 등급 분석 (호두 채널 기준)")
    engine = ClosingBetEngine()
    cb_report = engine.generate_report(items)
    print(f"  분석 시각: {cb_report.generated_at}")
    print(f"  총 분석: {cb_report.summary['total']}개")
    print(f"  매수대상(S/A): {cb_report.summary['buyable']}개")
    print(f"  등급분포: {cb_report.summary['distribution']}")

    # 상위 시그널 출력
    buyable = [s for s in cb_report.signals if s.grade in (SignalGrade.S, SignalGrade.A)]
    if buyable:
        print(f"\n  📌 매수 검토 대상 TOP:")
        for s in buyable[:5]:
            print(f"    {s.grade} {s.stock_name:25s} 점수:{s.score:.0f} | {s.reason}")

    # ─────────────────────────────────────────────
    # Step 3: VCP 스캔
    # ─────────────────────────────────────────────
    print_header("📊 Step 3: VCP 패턴 스캔")
    scanner = VCPScanner()
    vcps = scanner.scan(items)
    breakout = [v for v in vcps if v.breakout_imminent]
    print(f"  VCP 감지: {len(vcps)}개")
    print(f"  🔥 돌파임박: {len(breakout)}개")
    for v in breakout[:3]:
        print(f"    🔥 {v.stock_name:25s} {v.description}")

    # 리포트에 VCP 추가
    cb_report.vcp_signals = vcps
    cb_report.summary["vcp_detected"] = len(vcps)
    cb_report.summary["vcp_breakout"] = len(breakout)

    # ─────────────────────────────────────────────
    # Step 4: 대시보드 연결 JSON 생성
    # ─────────────────────────────────────────────
    print_header("🔗 Step 4: 대시보드 연동 JSON 생성")
    dashboard_json = adapter.to_dashboard_format(cb_report)
    output_path = os.path.join(OUTPUT_DIR,
        f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(dashboard_json, f, ensure_ascii=False, indent=2)
    print(f"  ✅ 저장됨: {output_path}")
    print(f"  📎 대시보드 연동: 이 파일을 대시보드에서 fetch()로 읽으면 됨")

    # ─────────────────────────────────────────────
    # Step 5: 실행 요약
    # ─────────────────────────────────────────────
    print_header("📋 최종 요약")
    actions = dashboard_json["closing_bet"]["signals"]
    buys = [s for s in actions if s["action"] == "BUY"]
    print(f"  ✅ BUY  (매수검토): {len(buys)}개")
    print(f"  👀 WATCH (관망): {len([s for s in actions if s['action']=='WATCH'])}개")
    print(f"  🏠 HOLD (보유): {len([s for s in actions if s['action']=='HOLD'])}개")
    print(f"  ❌ SKIP (제외): {len([s for s in actions if s['action']=='SKIP'])}개")
    print(f"  🔥 VCP 돌파임박: {len(breakout)}개")
    print(f"\n  📁 전체 결과: {output_path}")
    print(f"  🚀 내일 만복이에게 전달 준비 완료!")


if __name__ == "__main__":
    main()
