import json
d = json.load(open("d:/AI/0627_setup_finance_cline/data/sample_portfolio.json","r",encoding="utf-8"))
print(f"Valid JSON: {d['total_items']} stocks, {len(d['accounts'])} accounts")
print(f"First 3 stocks: {[s['name'] for s in d['stocks'][:3]]}")
print(f"Accounts: {[a['name'] for a in d['accounts']]}")
