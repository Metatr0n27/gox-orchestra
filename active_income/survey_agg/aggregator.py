#!/usr/bin/env python3
"""Aggregates paid survey/test opportunities from multiple platforms."""
import json,requests
from bs4 import BeautifulSoup
from pathlib import Path

OUTFILE = Path.home()/"HERMES/active_income/survey_agg/opps.json"

PLATFORMS = {
    "usertesting": {"url":"https://www.usertesting.com/be-a-user-tester","rate":"$10/20min"},
    "respondent": {"url":"https://www.respondent.io/participants","rate":"$50-150/study"},
    "userinterviews": {"url":"https://www.userinterviews.com/how-it-works","rate":"$75/hr avg"},
    "swagbucks": {"url":"https://www.swagbucks.com/p/register","rate":"$5-15/hr"},
    "mturk": {"url":"https://www.mturk.com/worker","rate":"$8-12/hr"},
}

def scrape_meta(name, cfg):
    try:
        r = requests.get(cfg["url"], timeout=10, headers={"User-Agent":"Mozilla/5.0"})
        soup = BeautifulSoup(r.text, "html.parser")
        title = soup.find("title").text.strip() if soup.find("title") else name
        return {"platform":name,"url":cfg["url"],"rate":cfg["rate"],"page_title":title}
    except:
        return {"platform":name,"url":cfg["url"],"rate":cfg["rate"],"error":"timeout"}

def aggregate():
    results = []
    for name, cfg in PLATFORMS.items():
        results.append(scrape_meta(name, cfg))
    OUTFILE.write_text(json.dumps(results, indent=2))
    print(f"[SURVEYS] Aggregated {len(results)} platforms")
    for r in results:
        print(f"  - {r['platform']}: {r['rate']}")

if __name__ == "__main__":
    aggregate()
