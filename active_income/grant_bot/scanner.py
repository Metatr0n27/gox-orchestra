#!/usr/bin/env python3
"""Auto-discovers and queues grant applications."""
import json,requests,re,asyncio
from datetime import datetime
from pathlib import Path

CACHE = Path.home()/"HERMES/active_income/grant_bot/cache.json"
QUEUE = Path.home()/"HERMES/active_income/grant_bot/to_apply.json"

SOURCES = [
    "https://helloalice.com/grants/",
    "https://www.ifundwomen.com/projects",
    "https://www.kickstarter.com/creator-funds",
]

GRANT_PATTERNS = [
    r'\$[\d,]+\s*(?:grant|fund|award)',
    r'application\s*(?:open|due|deadline)[:\s]*([\w\d,\s]+)',
    r'(?:small business|startup|entrepreneur)[\s\w]*(?:grant|fund)'
]

def scan_source(url):
    try:
        r = requests.get(url, timeout=15, headers={"User-Agent":"Mozilla/5.0"})
        matches = []
        for pat in GRANT_PATTERNS:
            matches.extend(re.findall(pat, r.text, re.I))
        return list(set(matches))[:10]
    except Exception as e:
        return [f"ERROR: {e}"]

def main():
    findings = {}
    for src in SOURCES:
        findings[src] = scan_source(src)
    
    CACHE.write_text(json.dumps(findings, indent=2))
    
    opportunities = []
    for src, matches in findings.items():
        for m in matches:
            if isinstance(m,str) and "$" in m:
                amt = re.search(r'\$([\d,]+)', m)
                if amt:
                    val = int(amt.group(1).replace(",",""))
                    if val >= 1000:
                        opportunities.append({"source":src,"snippet":m,"value":val})
    
    opportunities.sort(key=lambda x: -x["value"])
    QUEUE.write_text(json.dumps(opportunities[:20], indent=2))
    
    print(f"[GRANTS] Found {len(opportunities)} qualifying opportunities")
    print(f"[GRANTS] Top prize: ${opportunities[0]['value']:,}" if opportunities else "")

if __name__ == "__main__":
    main()
