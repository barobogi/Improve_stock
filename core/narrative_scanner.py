# narrative_scanner.py — 뉴스 RSS → Claude 테마 분석 → 종목 내러티브 점수 산출
import json
import glob
import subprocess
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional

# Claude CLI 경로
_claude_candidates = glob.glob(
    r"C:\Users\*\.vscode\extensions\anthropic.claude-code-*\resources\native-binary\claude.exe"
)
CLAUDE_EXE = sorted(_claude_candidates)[-1] if _claude_candidates else "claude"

# 뉴스 RSS 소스 (API 키 불필요)
NEWS_RSS_SOURCES = [
    {
        "name": "한국경제",
        "url": "https://www.hankyung.com/feed/all-news",
        "category": "경제",
    },
    {
        "name": "매일경제",
        "url": "https://www.mk.co.kr/rss/40300001/",
        "category": "주식",
    },
    {
        "name": "CNBC Markets",
        "url": "https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=10000664",
        "category": "미국주식",
    },
    {
        "name": "Reuters Business",
        "url": "https://feeds.reuters.com/reuters/businessNews",
        "category": "글로벌경제",
    },
]

# 섹터 → 종목 매핑 (sector_mapping.json 없을 때 기본값)
DEFAULT_SECTOR_MAP = {
    "반도체": ["삼성전자", "SK하이닉스", "한미반도체", "DB하이텍"],
    "2차전지": ["LG에너지솔루션", "삼성SDI", "POSCO홀딩스", "에코프로비엠"],
    "AI": ["네이버", "카카오", "KT", "SK텔레콤"],
    "에너지": ["HD현대에너지솔루션", "두산에너빌리티", "한화솔루션"],
    "바이오": ["셀트리온", "삼성바이오로직스", "유한양행"],
    "금융": ["KB금융", "신한지주", "하나금융지주", "삼성화재"],
    "자동차": ["현대차", "기아", "현대모비스", "HL만도"],
}

SECTOR_MAP_PATH = Path(__file__).parent.parent / "data" / "sector_mapping.json"


@dataclass
class NarrativeScore:
    """종목별 내러티브 모멘텀 점수"""
    stock_name: str
    score: float = 0.0            # 0~100
    themes: list = field(default_factory=list)   # 연관 테마
    news_count: int = 0
    top_headline: str = ""

    def to_dict(self) -> dict:
        return {
            "stock": self.stock_name,
            "narrative_score": round(self.score, 1),
            "themes": self.themes,
            "news_count": self.news_count,
            "top_headline": self.top_headline,
        }


def _fetch_rss(url: str, timeout: int = 10) -> list[dict]:
    """RSS 피드에서 오늘 뉴스 제목 수집"""
    try:
        req = urllib.request.Request(
            url, headers={"User-Agent": "Mozilla/5.0 (compatible; ImproveStock/1.1)"}
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            xml_data = resp.read()
        root = ET.fromstring(xml_data)
        items = []
        for item in root.iter("item"):
            title = item.findtext("title", "").strip()
            pub   = item.findtext("pubDate", "").strip()
            if title:
                items.append({"title": title, "pubDate": pub})
        return items[:20]  # 최신 20개
    except Exception as e:
        print(f"[NarrativeScanner] RSS 수집 실패 ({url}): {e}")
        return []


def _extract_themes_via_claude(headlines: list[str]) -> list[dict]:
    """Claude CLI로 뉴스 헤드라인 → 테마 + 점수 추출"""
    prompt = f"""다음 주식/경제 뉴스 헤드라인을 분석하여 테마와 점수를 JSON으로 반환해주세요.

헤드라인 목록:
{chr(10).join(f"- {h}" for h in headlines[:15])}

반드시 아래 JSON 형식만 출력 (코드블록 없이 순수 JSON):
{{
  "themes": [
    {{"name": "테마명", "score": 점수(1~10), "keywords": ["키워드1", "키워드2"], "headline": "대표 헤드라인"}}
  ]
}}

테마명은 반드시 다음 중에서 선택: AI, 반도체, 데이터센터, 우주항공, 방산, 에너지, 2차전지, 전기차, 자동차, 금융, 배당, 나스닥, S&P500, 코스닥, 통신, 기타
점수는 뉴스 강도와 글로벌 시장 영향력 기준 (10=매우 강함, 1=미약)
상위 5개 테마만 포함"""

    try:
        result = subprocess.run(
            [CLAUDE_EXE, "--output-format", "json", "--print"],
            input=prompt.encode("utf-8"),
            capture_output=True,
            timeout=60,
        )
        if result.returncode != 0:
            print(f"[NarrativeScanner] Claude 오류: {result.stderr.decode('utf-8', errors='replace')[:100]}")
            return []

        outer = json.loads(result.stdout.decode("utf-8"))
        text = outer.get("result") or ""
        if not text:
            content = outer.get("content", [])
            text = content[0].get("text", "") if content else ""

        text = text.strip()
        if "```" in text:
            for part in text.split("```"):
                part = part.strip().lstrip("json").strip()
                try:
                    return json.loads(part).get("themes", [])
                except Exception:
                    continue
        return json.loads(text).get("themes", [])

    except Exception as e:
        print(f"[NarrativeScanner] Claude 분석 실패: {e}")
        return []


def _load_sector_map() -> dict:
    """섹터-종목 매핑 테이블 로드"""
    if SECTOR_MAP_PATH.exists():
        try:
            return json.loads(SECTOR_MAP_PATH.read_text(encoding="utf-8"))
        except Exception:
            pass
    return DEFAULT_SECTOR_MAP


def scan(target_stocks: Optional[list[str]] = None) -> list[NarrativeScore]:
    """
    메인 함수: RSS 수집 → Claude 테마 분석 → 종목 점수 산출

    Args:
        target_stocks: 점수 산출 대상 종목 리스트 (None이면 섹터 맵 전체)

    Returns:
        NarrativeScore 리스트 (점수 내림차순)
    """
    print(f"[NarrativeScanner] 뉴스 수집 시작 {datetime.now().strftime('%H:%M')}")

    # 1. RSS 뉴스 수집
    all_headlines = []
    for source in NEWS_RSS_SOURCES:
        items = _fetch_rss(source["url"])
        headlines = [it["title"] for it in items]
        all_headlines.extend(headlines)
        print(f"  [{source['name']}] {len(headlines)}개 수집")

    if not all_headlines:
        print("[NarrativeScanner] 뉴스 수집 실패 — 종료")
        return []

    # 2. Claude → 테마 추출
    print(f"[NarrativeScanner] Claude 테마 분석 중... ({len(all_headlines)}개 헤드라인)")
    themes = _extract_themes_via_claude(all_headlines)
    if not themes:
        print("[NarrativeScanner] 테마 추출 실패")
        return []

    print(f"[NarrativeScanner] 테마 {len(themes)}개 추출:")
    for t in themes:
        print(f"  - {t.get('name')} (점수: {t.get('score')}): {t.get('headline', '')[:50]}")

    # 3. 섹터 매핑 → 종목 점수 배분
    sector_map = _load_sector_map()
    stock_scores: dict[str, NarrativeScore] = {}

    for theme in themes:
        theme_name  = theme.get("name", "")
        theme_score = float(theme.get("score", 0)) * 10  # 1~10 → 10~100
        headline    = theme.get("headline", "")

        stocks_in_sector = sector_map.get(theme_name, [])
        if not stocks_in_sector:
            continue

        for stock in stocks_in_sector:
            if target_stocks and stock not in target_stocks:
                continue
            if stock not in stock_scores:
                stock_scores[stock] = NarrativeScore(stock_name=stock)
            ns = stock_scores[stock]
            ns.score = min(100, ns.score + theme_score * 0.5)
            if theme_name not in ns.themes:
                ns.themes.append(theme_name)
            ns.news_count += 1
            if not ns.top_headline:
                ns.top_headline = headline

    results = sorted(stock_scores.values(), key=lambda x: -x.score)
    print(f"[NarrativeScanner] 완료 — {len(results)}개 종목 점수 산출")
    return results


if __name__ == "__main__":
    # 단독 실행 테스트
    scores = scan()
    print("\n=== 내러티브 모멘텀 TOP 10 ===")
    for ns in scores[:10]:
        print(f"  {ns.stock_name:15s} | 점수: {ns.score:5.1f} | 테마: {', '.join(ns.themes)}")
