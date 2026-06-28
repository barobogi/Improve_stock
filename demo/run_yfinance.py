"""
run_yfinance.py — yfinance 실데이터 기반 종가베팅 분석
========================================================
실행: python demo/run_yfinance.py

- ticker_map.json 에서 종목 자동 로드
- yfinance 실데이터로 등급 산출 (S/A/B/C/D)
- 텔레그램 전송 + output/latest.json 저장
- 새 종목 추가: ticker_map.json 에 추가만 하면 자동 반영
"""
import os
import sys
import json
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from core.yfinance_provider import YFinanceProvider
from core.closing_bet import ClosingBetEngine
from core.signal_types import PortfolioItem, SignalGrade
from core.telegram_notify import send_signal_report


def build_portfolio(provider: YFinanceProvider) -> list[PortfolioItem]:
    """ticker_map.json → PortfolioItem 리스트 (yfinance 현재가 적용)"""
    stocks = provider.get_all_stocks()
    items  = []
    failed = []

    print(f"  분석 대상: {len(stocks)}개 종목 로드 중...")

    for s in stocks:
        data = provider.get_stock_data(s["name"], 0)
        if data.current_price == 0:
            failed.append(s["name"])
            continue
        price = data.current_price
        items.append(PortfolioItem(
            account_id   = 1,
            account_name = "yfinance 자동",
            stock_name   = s["name"],
            quantity     = 1,
            current_price= price,
            eval_amount  = price,
            buy_amount   = price,
            stock_type   = s["type"],
        ))

    if failed:
        print(f"  [주의] 조회 실패 {len(failed)}개: {', '.join(failed[:5])}")
    print(f"  실데이터 로드 완료: {len(items)}개")
    return items


def print_header(title: str):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


def main():
    OUTPUT_DIR = os.path.join(ROOT, "output")
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # ── Step 1: yfinance 종목 로드 ──────────────────────────
    print_header("Step 1: ticker_map.json → yfinance 실데이터 로드")
    provider = YFinanceProvider()
    items    = build_portfolio(provider)

    if not items:
        print("  [오류] 분석 가능한 종목이 없습니다. ticker_map.json 확인 필요.")
        return

    # ── Step 2: 종가베팅 등급 분석 ─────────────────────────
    print_header("Step 2: 종가베팅 등급 분석 (호두 채널 기준)")
    engine    = ClosingBetEngine(data_provider=provider)
    cb_report = engine.generate_report(items)

    print(f"  데이터 모드: [yfinance 실데이터]")
    print(f"  분석 시각: {cb_report.generated_at}")
    print(f"  총 분석: {cb_report.summary['total']}개")
    print(f"  매수대상(S/A): {cb_report.summary['buyable']}개")
    print(f"  등급분포: {cb_report.summary['distribution']}")

    buyable = [s for s in cb_report.signals if s.grade in (SignalGrade.S, SignalGrade.A)]
    if buyable:
        print(f"\n  매수 검토 대상 TOP:")
        for s in buyable[:5]:
            print(f"    [{s.grade.value}] {s.stock_name:30s} 점수:{s.score:.0f} | {s.reason}")

    # ── Step 3: 전체 등급 출력 ─────────────────────────────
    print_header("Step 3: 전체 종목 등급")
    for s in cb_report.signals:
        vol  = s.details.get("volume", 0)
        ma   = s.details.get("ma", "?")
        mom  = s.details.get("mom", 0)
        print(f"  [{s.grade.value}] {s.stock_name:30s} 거래량:{vol:.1f}x | MA:{ma} | 모멘텀:{mom:.2f}")

    # ── Step 4: 텔레그램 전송 ──────────────────────────────
    print_header("Step 4: 텔레그램 전송")
    sent = send_signal_report(cb_report.signals, [], is_mock=False)
    if sent:
        print("  텔레그램 전송 완료!")
    else:
        print("  텔레그램 미설정 또는 전송 실패")

    # ── Step 5: JSON 저장 ───────────────────────────────────
    output = {
        "generated_at": cb_report.generated_at,
        "mode": "yfinance",
        "total": cb_report.summary["total"],
        "buyable": cb_report.summary["buyable"],
        "distribution": cb_report.summary["distribution"],
        "signals": [s.to_dict() for s in cb_report.signals],
    }
    ts          = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = os.path.join(OUTPUT_DIR, f"yf_report_{ts}.json")
    latest_path = os.path.join(OUTPUT_DIR, "latest_yf.json")

    for path in (report_path, latest_path):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(output, f, ensure_ascii=False, indent=2)

    print_header("완료")
    print(f"  저장: {report_path}")
    print(f"  최신: {latest_path}")


if __name__ == "__main__":
    main()
