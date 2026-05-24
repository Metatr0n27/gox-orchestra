#!/usr/bin/env python3
"""
AUTO-HARVEST MODULE
Visits top opportunities and extracts actionable intel
"""

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
import json
import os
import time
from datetime import datetime

RESULTS_FILE = os.path.expanduser("~/HERMES/data/actionable.json")
SCREENSHOT_DIR = os.path.expanduser("~/HERMES/screenshots")

OPPORTUNITIES = [
    {
        "name": "kast_promo",
        "url": "https://redd.it/1tke08o",
        "action": "Extract signup link and requirements",
        "potential": 415
    },
    {
        "name": "onepay_promo", 
        "url": "https://redd.it/1tl1hzl",
        "action": "Check if still active, grab referral link",
        "potential": 150
    },
    {
        "name": "kraken_promo",
        "url": "https://redd.it/1tjr00j",
        "action": "Verify KYC requirements vs payout",
        "potential": 350
    }
]

def setup_driver():
    opts = Options()
    opts.add_argument("--headless")
    opts.add_argument("--width=1920")
    opts.add_argument("--height=1080")
    opts.binary_location = "/usr/bin/firefox-esr"
    
    service = Service(log_path=os.devnull)
    driver = webdriver.Firefox(options=opts, service=service)
    driver.set_page_load_timeout(30)
    return driver

def harvest_reddit_post(driver, post_id, name):
    """Visit reddit post and extract external links"""
    url = f"https://old.reddit.com/comments/{post_id}"
    try:
        driver.get(url)
        time.sleep(2)
        
        # Grab all outbound links
        links = []
        anchors = driver.find_elements("tag name", "a")
        for a in anchors:
            href = a.get_attribute("href")
            if href and "reddit.com" not in href and "redd.it" not in href:
                if any(x in href.lower() for x in ["signup", "register", "invite", "referral", "promocode"]):
                    links.append(href)
        
        # Save screenshot
        ss_path = f"{SCREENSHOT_DIR}/{name}_{datetime.now().strftime('%H%M%S')}.png"
        os.makedirs(SCREENSHOT_DIR, exist_ok=True)
        driver.save_screenshot(ss_path)
        
        return {"success": True, "links": links[:5], "screenshot": ss_path}
    except Exception as e:
        return {"success": False, "error": str(e)[:50]}

def run_harvest():
    print("\n" + "="*45)
    print("AUTO-HARVEST INITIATED")
    print("="*45 + "\n")
    
    driver = setup_driver()
    results = []
    
    for opp in OPPORTUNITIES:
        print(f"Hunting: {opp['name']} (${opp['potential']})")
        
        # Extract post ID from redd.it link
        post_id = opp['url'].split("/")[-1]
        
        data = harvest_reddit_post(driver, post_id, opp['name'])
        
        result = {
            "name": opp['name'],
            "potential_usd": opp['potential'],
            "harvested": datetime.now().strftime("%H:%M:%S"),
            "outcome": data
        }
        results.append(result)
        
        if data['success']:
            print(f"  ✓ Links captured: {len(data.get('links', []))}")
        else:
            print(f"  ✗ Issue: {data.get('error', 'unknown')}")
        
        time.sleep(1)
    
    driver.quit()
    
    with open(RESULTS_FILE, "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n{'='*45}")
    print(f"Harvest complete. Data saved to:\n{RESULTS_FILE}")
    print(f"Screenshots in: {SCREENSHOT_DIR}/")
    print("="*45)
    
    return results

if __name__ == "__main__":
    run_harvest()
