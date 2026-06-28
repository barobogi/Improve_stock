#!/usr/bin/env python
"""generate_sample_data.py — 대시보드 포트폴리오 샘플 데이터 생성"""
import json, os

DATA_DIR = os.path.dirname(os.path.abspath(__file__))

accounts = [
    {"id":1,"name":"일반계좌1","num":"70714","type":"general","desc":"미국주식+한국주식"},
    {"id":2,"name":"일반계좌2","num":"70871","type":"general","desc":"미국주식+한국주식"},
    {"id":3,"name":"ISA","num":"71297","type":"isa","desc":"ISA 계좌"},
    {"id":4,"name":"IRP","num":"70714","type":"irp","desc":"IRP (퇴직연금)"},
    {"id":5,"name":"연금저축1","num":"71462","type":"pension","desc":"연금저축"},
    {"id":6,"name":"연금저축2","num":"71615","type":"pension","desc":"연금저축"},
    {"id":7,"name":"연금저축3","num":"70868","type":"pension","desc":"연금저축"},
    {"id":8,"name":"일반계좌3","num":"71417","type":"general","desc":"해외주식"},
    {"id":9,"name":"일반계좌4","num":"71661","type":"general","desc":"일반계좌"},
]

def _stock(aid, name, qty, price, eval_amt, stype, buy_amt):
    return {"accountId":aid,"name":name,"qty":qty,"curPrice":price,
            "evalAmount":eval_amt,"type":stype,"buyAmount":buy_amt}

# -- 종목 데이터 (대시보드 2026-06-19 12:50 기준) --
stocks = [] 

# -- 일반계좌1 (accountId=1) --
stocks.append(_stock(1,"SOL 팔란티어미국채커버드콜혼합",5,9945,49725,"주식",56975))
stocks.append(_stock(1,"SOL 팔란티어커버드콜OTM채권혼합",159,8410,1337190,"주식",1437837))
stocks.append(_stock(1,"삼성전자",118,362500,42775000,"주식",16842022))
stocks.append(_stock(1,"ACE 미국AI테크핵심산업액티브",26,10200,265200,"주식",224276))
stocks.append(_stock(1,"SOL 200타겟위클리커버드콜",82,16485,1351770,"주식",963336))
stocks.append(_stock(1,"KODEX 미국우주항공",158,11965,1890470,"주식",1877988))
stocks.append(_stock(1,"TIGER 현대차그룹플러스",36,64545,2323620,"주식",2234124))
stocks.append(_stock(1,"KODEX 코스닥150레버리지",322,12430,4002460,"주식",3414810))
stocks.append(_stock(1,"KODEX 테슬라커버드콜채권혼합액티브",29,8530,247370,"주식",249574))
stocks.append(_stock(1,"KODEX 200타겟위클리커버드콜",842,28270,23803340,"주식",16301120))
stocks.append(_stock(1,"앰프리어스 테크놀로지스",81,16170,1981420,"해외증권",1913369))
stocks.append(_stock(1,"TRD2XLG APLD ETF",1,32430,49060,"해외증권",40209))
stocks.append(_stock(1,"TRADR 2X LNG ETF",10,33950,513595,"해외증권",757101))
stocks.append(_stock(1,"AST 스페이스모바일",20,80660,2440448,"해외증권",1927270))
stocks.append(_stock(1,"TRDR 2X ASTS ETF",24,24265,880994,"해외증권",1040318))
stocks.append(_stock(1,"BTQ 테크놀로지스",12,5675,103021,"해외증권",50710))
stocks.append(_stock(1,"Leverage Shares 2X Long CBRS DLY ETF",400,729,4411324,"해외증권",3869643))
stocks.append(_stock(1,"셀레스티카",5,372550,2817968,"해외증권",1299495))
stocks.append(_stock(1,"TRDR CLS DLY ETF",270,1998,8160950,"해외증권",9020115))
stocks.append(_stock(1,"RNDHL MEMRY ETF",10,7671,1160468,"해외증권",812762))
stocks.append(_stock(1,"아이렌",32,59960,2902639,"해외증권",2302487))
stocks.append(_stock(1,"실스크",1,3120,4719,"해외증권",5073))
stocks.append(_stock(1,"엔비디아",1,210690,195786,"해외증권",173908))
stocks.append(_stock(1,"파가야 테크놀로지스",2,15620,47259,"해외증권",33253))
stocks.append(_stock(1,"RNDHLL INVTN ETF",19,31510,905698,"해외증권",895976))
stocks.append(_stock(1,"퀀텀스케이프",6,8040,72977,"해외증권",87737))
stocks.append(_stock(1,"DFC DLY RKLB ETF",30,52450,2380390,"해외증권",2198880))
stocks.append(_stock(1,"Schwab 미국 배당주 ETF",2,31860,96395,"해외증권",73297))
stocks.append(_stock(1,"서프 에어 모빌리티",20,1170,35399,"해외증권",46077))
stocks.append(_stock(1,"X-에너지",1,21560,32615,"해외증권",45674))
# -- 일반계좌2 (accountId=2) --
stocks.append(_stock(2,"삼성전자",30,362500,10875000,"주식",1641000))
stocks.append(_stock(2,"삼성미국S&P500인덱스증권자투자H(주)-Ce",26443,3078,81396,"수익증권",69677))
stocks.append(_stock(2,"AST 스페이스모바일",62,80660,7565391,"해외증권",5120151))
stocks.append(_stock(2,"TRDR 2X ASTS ETF",200,24265,7341618,"해외증권",7613913))
stocks.append(_stock(2,"셀레스티카",20,372550,11271872,"해외증권",4450910))
stocks.append(_stock(2,"TRDR 2X CRDO ETF",39,99410,5865110,"해외증권",962096))
stocks.append(_stock(2,"TT DF 2XIREN ETF",81,29850,3657723,"해외증권",1931312))
stocks.append(_stock(2,"아이렌",100,59960,9070748,"해외증권",5285207))
# -- ISA (accountId=3) --
stocks.append(_stock(3,"SOL 팔란티어커버드콜OTM채권혼합",2008,8410,16887280,"주식",20086024))
stocks.append(_stock(3,"삼성전자",15,362500,5437500,"주식",967500))
stocks.append(_stock(3,"PLUS 자사주매입고배당주",31,12800,396800,"주식",341961))
stocks.append(_stock(3,"ACE 미국AI테크핵심산업액티브",909,10200,9271800,"주식",7576515))
stocks.append(_stock(3,"SOL 200타겟위클리커버드콜",1995,16485,32887575,"주식",27808305))
stocks.append(_stock(3,"KODEX 미국우주항공",238,11965,2847670,"주식",2683884))
stocks.append(_stock(3,"TIGER 현대차그룹플러스",15,64545,968175,"주식",861000))
stocks.append(_stock(3,"KODEX 미국나스닥100",4,30425,121700,"주식",91388))
stocks.append(_stock(3,"TIGER 미국테크TOP10타겟커버드콜",304,15995,4862480,"주식",3885728))
stocks.append(_stock(3,"KODEX 테슬라커버드콜채권혼합액티브",1401,8530,11950530,"주식",13249257))
stocks.append(_stock(3,"RISE 200위클리커버드콜",1485,16040,23819400,"주식",14374800))
stocks.append(_stock(3,"ACE 미국빅테크7+데일리타겟커버드콜(합성)",329,12195,4012155,"주식",4119080))
stocks.append(_stock(3,"TIGER 미국S&P500타겟데일리커버드콜",354,13000,4602000,"주식",3640182))
stocks.append(_stock(3,"KODEX 200타겟위클리커버드콜",590,28270,16679300,"주식",10741540))
# -- 연금저축1 (accountId=5) --
stocks.append(_stock(5,"SOL 팔란티어미국채커버드콜혼합",90,9945,895050,"주식",1044090))
stocks.append(_stock(5,"SOL 팔란티어커버드콜OTM채권혼합",1622,8410,13641020,"주식",16174584))
stocks.append(_stock(5,"ACE 미국AI테크핵심산업액티브",453,10200,4620600,"주식",0))
stocks.append(_stock(5,"SOL 200타겟위클리커버드콜",108,16485,1780380,"주식",1331748))
stocks.append(_stock(5,"KODEX 미국우주항공",45,11965,538425,"주식",461430))
stocks.append(_stock(5,"TIGER 현대차그룹플러스",253,64545,16329885,"주식",15415590))
stocks.append(_stock(5,"KODEX 테슬라커버드콜채권혼합액티브",490,8530,4179700,"주식",4602080))
stocks.append(_stock(5,"RISE 200위클리커버드콜",639,16040,10249560,"주식",6492420))
stocks.append(_stock(5,"TIGER 미국S&P500타겟데일리커버드콜",623,13000,8099000,"주식",6271542))
stocks.append(_stock(5,"KODEX 미국나스닥100데일리커버드콜OTM",37,10935,404595,"주식",380286))
stocks.append(_stock(5,"ACE 미국빅테크7+데일리타겟커버드콜(합성)",517,12195,6304815,"주식",5990200))
stocks.append(_stock(5,"KODEX 200타겟위클리커버드콜",450,28270,12721500,"주식",8189550))
stocks.append(_stock(5,"KODEX 금융고배당TOP10타겟위클리커버드콜",310,11960,3707600,"주식",3707600))
# -- 연금저축2 (accountId=6) --
stocks.append(_stock(6,"SOL 팔란티어커버드콜OTM채권혼합",185,8410,1555850,"주식",1867190))
stocks.append(_stock(6,"ACE 미국AI테크핵심산업액티브",237,10200,2417400,"주식",2370000))
stocks.append(_stock(6,"KODEX 테슬라커버드콜채권혼합액티브",706,8530,6022180,"주식",6417540))
stocks.append(_stock(6,"RISE 200위클리커버드콜",673,16040,10794920,"주식",6960060))
stocks.append(_stock(6,"TIGER 미국테크TOP10타겟커버드콜",219,15995,3502905,"주식",3119524))
stocks.append(_stock(6,"TIGER 미국S&P500타겟데일리커버드콜",354,13000,4602000,"주식",3919716))
stocks.append(_stock(6,"KODEX 미국나스닥100데일리커버드콜OTM",208,10935,2274480,"주식",2111408))
stocks.append(_stock(6,"ACE 미국빅테크7+데일리타겟커버드콜(합성)",491,12195,5987745,"주식",6216480))
stocks.append(_stock(6,"KODEX 200타겟위클리커버드콜",309,28270,8735430,"주식",6365670))
stocks.append(_stock(6,"KODEX 금융고배당TOP10타겟위클리커버드콜",251,11960,3001960,"주식",3162600))
stocks.append(_stock(6,"SOL 200타겟위클리커버드콜",361,16485,5951085,"주식",4664038))

# -- 연금저축3 (accountId=7) --
stocks.append(_stock(7,"KODEX 테슬라커버드콜채권혼합액티브",509,8530,4341770,"주식",4606400))
stocks.append(_stock(7,"RISE 200위클리커버드콜",135,16040,2165400,"주식",1409400))
stocks.append(_stock(7,"TIGER 미국테크TOP10타겟커버드콜",239,15995,3822805,"주식",3276674))
stocks.append(_stock(7,"KODEX 미국나스닥100데일리커버드콜OTM",208,10935,2274480,"주식",2111408))
stocks.append(_stock(7,"KODEX 200타겟위클리커버드콜",135,28270,3816450,"주식",2251935))
stocks.append(_stock(7,"TIGER 미국S&P500타겟데일리커버드콜",239,13000,3107000,"주식",2515714))
stocks.append(_stock(7,"KODEX 금융고배당TOP10타겟위클리커버드콜",768,11960,9185280,"주식",9502464))
stocks.append(_stock(7,"삼성신종종류형MMF제4호-CP",336069,1010,339728,"수익증권",339597))
# -- IRP (accountId=4) --
stocks.append(_stock(4,"TIGER 현대차그룹플러스",11,64545,709995,"주식",638150))
stocks.append(_stock(4,"KODEX 미국S&P500",9,25830,232470,"주식",131715))
stocks.append(_stock(4,"KODEX 미국배당커버드콜액티브",227,13545,3074715,"주식",2555145))
stocks.append(_stock(4,"RISE 글로벌자산배분액티브",24,15140,363360,"주식",345915))
stocks.append(_stock(4,"TIGER 미국테크TOP10타겟커버드콜",235,15995,3758825,"주식",2771720))
stocks.append(_stock(4,"KODEX 테슬라커버드콜채권혼합액티브",895,8530,7634350,"주식",8190800))
stocks.append(_stock(4,"RISE 200위클리커버드콜",465,16040,7458600,"주식",3692810))
stocks.append(_stock(4,"ACE 미국빅테크7+데일리타겟커버드콜(합성)",304,12195,3707280,"주식",3845600))
stocks.append(_stock(4,"KODEX 200타겟위클리커버드콜",27,28270,763290,"주식",441270))
stocks.append(_stock(4,"KODEX 금융고배당TOP10타겟커버드콜",664,11960,7941440,"주식",8318115))
stocks.append(_stock(4,"SOL 팔란티어커버드콜OTM채권혼합",989,8410,8317490,"주식",9666960))
stocks.append(_stock(4,"SOL 팔란티어미국채커버드콜혼합",31,9945,308295,"주식",356345))
stocks.append(_stock(4,"SOL 200타겟위클리커버드콜",69,16485,1137465,"주식",939865))
stocks.append(_stock(4,"현금성자산(삼성증권)",185802,1,185802,"수익증권",185802))
stocks.append(_stock(4,"삼성증권 디폴트옵션 안정자산형",0,0,4388,"수익증권",0))

# -- 출력 --
data = {
    "memo": "대시보드 포트폴리오 샘플 (2026-06-19 12:50 기준)",
    "source": "barobogi.github.io/stock_dashboard — DEFAULT_STOCKS",
    "total_items": len(stocks),
    "accounts": accounts,
    "stocks": stocks,
    "exchange_rate": 1512.8,
    "baseline_date": "2026-06-19",
    "baseline_time": "12:50"
}
out_path = os.path.join(DATA_DIR, "sample_portfolio.json")
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print(f"✅ 생성 완료: {out_path}")
print(f"   계좌: {len(accounts)}개, 종목: {len(stocks)}개")

# -- 그 외 남은 종목들 (연금저축3, IRP) --


