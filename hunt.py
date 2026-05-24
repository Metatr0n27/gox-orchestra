#!/usr/bin/env python3
import requests
import json
import os
import re
from datetime import datetime

DATA_FILE = os.path.expanduser("~/HERMES/data/results.json")
LOG_FILE = os.path.expanduser("~/HERMES/logs/runlog.txt")
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

SOURCES = [
    ("beermoney", "https://old.reddit.com/r/beermoney/new.json?limit=15"),
    ("slavelabour", "https://old.reddit.com/r/slavelabour/new.json?limit=15"),
    ("signupsforpay", "https://old.reddit.com/r/signupsforpay/new.json?limit=15"),
    ("passive_income", "https://old.reddit.com/r/passive_income/new.json?limit=10"),
    ("flipping", "https://old.reddit.com/r/flipping/new.json?limit=10"),
    ("workonline", "https://old.reddit.com/r/workonline/new.json?limit=10"),
]

DEAL_SITES = [
    ("slickdeals_popular", "https://slickdeals.net/popular.php"),
    ("dealsea_new", "https://www.dealsea.com/new-deals"),
]

KEYWORDS = ["$", "paypal", "venmo", "cash", "btc", "bitcoin", "paid", "hiring", "looking for", "offer", "% off"]

def extract_amount(text):
    matches = re.findall(r'\$(\d+(?:,\d{3})*(?:\.\d{2})?)', text)
    if matches:
        nums = [float(m.replace(",", "")) for m in matches]
        return max(nums)
    return None

def fetch_subreddit(name, url):
    items = []
    try:
        r = requests.get(url, headers=HEADERS, timeout=12)
        posts = r.json().get("data", {}).get("children", [])
        for p in posts:
            d = p.get("data", {})
            title = d.get("title", "")
            selftext = d.get("selftext", "")
            combined = title + " " + selftext
            
            keyword_match = sum(1 for kw in KEYWORDS if kw.lower() in combined.lower())
            amount = extract_amount(combined)
            
            if keyword_match >= 1 or amount:
                items.append({
                    "source": name,
                    "type": "reddit_post",
                    "title": title[:100],
                    "link": "https://redd.it/" + d.get("id", ""),
                    "amount": amount,
                    "keyword_score": keyword_match,
                    "priority": (amount or 0) + (keyword_match * 5),
                    "time": datetime.now().strftime("%H:%M")
                })
        print(f"[{name}] {len(items)} relevant posts")
    except Exception as e:
        print(f"[{name}] error: {str(e)[:25]}")
    return items

def fetch_deals(name, url):
    items = []
    try:
        r = requests.get(url, headers=HEADERS, timeout=12)
        soup = __import__("bs4").BeautifulSoup(r.text, "html.parser")
        texts = soup.get_text(separator=" ")[:3000]
        
        deals = re.findall(r'(\$[\d,.]+)[^\$]*?(?:was\s*)?(\$[\d,.]+)?', texts)
        amounts = re.findall(r'\$(\d+(?:\.\d{2})?)', texts)
        pct_off = re.findall(r'(\d{1,3})%\s*[oO][fF][fF]', texts)
        
        if amounts:
            savings = sum(float(a) for a in amounts[:10]) * 0.3
            items.append({
                "source": name,
                "type": "price_error_watch",
                "sample_prices": amounts[:5],
                "percent_off_samples": pct_off[:3],
                "est_flip_potential": round(savings, 2),
                "priority": savings,
                "time": datetime.now().strftime("%H:%M")
            })
            print(f"[{name}] {len(amounts)} prices tracked")
    except Exception as e:
        print(f"[{name}] error: {str(e)[:25]}")
    return items

def run():
    all_items = []
    
    print("\n=== HERMES HUNT STARTING ===\n")
    
    for src_name, src_url in SOURCES:
        all_items.extend(fetch_subreddit(src_name, src_url))
    
    for deal_name, deal_url in DEAL_SITES:
        all_items.extend(fetch_deals(deal_name, deal_url))
    
    all_items.sort(key=lambda x: x.get("priority", 0), reverse=True)
    
    with open(DATA_FILE, "w") as f:
        json.dump(all_items[:50], f, indent=2)
    
    summary = {
        "last_run": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "total_opportunities": len(all_items),
        "top_priority": all_items[0]["title"][:60] if all_items else "none"
    }
    
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(summary) + "\n")
    
    print(f"\n=== RESULTS ===")
    print(f"Stored: {len(all_items)} opportunities")
    print(f"Top hit: {summary['top_priority']}")
    print(f"File: {DATA_FILE}")

if __name__ == "__main__":
    run()
