#!/usr/bin/env python3
"""Generates affiliate landing pages for passive commission collection."""
from pathlib import Path

BASE = Path.home()/"HERMES/active_income/affiliate_grid/pages"
BASE.mkdir(parents=True, exist_ok=True)

TEMPLATES = {
    "tools": {
        "title": "Essential Tools for Gig Workers",
        "programs": [
            {"name":"DoorDash Signup","link":"https://drd.sh/","bonus":"$200+"},
            {"name":"Uber Eats Invite","link":"https://ubereats.com/drive","bonus":"Varies"},
            {"name":"Instacart Referral","link":"https://shoppers.instacart.com","bonus":"$750"},
        ]
    },
    "finance": {
        "title": "Banking Apps That Pay You",
        "programs": [
            {"name":"CashApp Download","link":"https://cash.app","bonus":"$5-15"},
            {"name":"Venmo Promo","link":"https://venmo.com","bonus":"$10"},
            {"name":"Chime Referral","link":"https://chime.com","bonus":"$100"},
        ]
    }
}

HTML_TEMPLATE = '''<!DOCTYPE html>
<html><head><title>{title}</title>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<style>body{{font-family:sans-serif;max-width:600px;margin:40px auto;padding:20px}}
h1{{color:#00aa55}}.offer{{border:1px solid #ddd;border-radius:8px;padding:16px;margin:12px 0}}
.offer h3{{margin:0 0 8px}}.badge{{background:#00aa55;color:#fff;padding:4px 8px;border-radius:4px;font-size:12px}}
a.button{{display:inline-block;background:#00aa55;color:#fff;padding:12px 24px;border-radius:6px;text-decoration:none;margin-top:8px}}</style>
</head><body>
<h1>{title}</h1>
<p>Earn sign-up bonuses instantly:</p>
{offers}
<footer style="margin-top:40px;color:#666;font-size:12px">Affiliate disclosure: We may earn commissions.</footer>
</body></html>'''

def gen_page(slug, data):
    offers_html = ""
    for prog in data["programs"]:
        offers_html += f'''<div class="offer"><h3>{prog['name']}</h3>
<span class="badge">{prog['bonus']} bonus</span><br>
<a class="button" href="{prog['link']}">Claim Bonus</a></div>\n'''
    
    html = HTML_TEMPLATE.format(title=data["title"], offers=offers_html)
    (BASE/f"{slug}.html").write_text(html)
    print(f"[AFFILIATE] Created {slug}.html")

def main():
    for slug, data in TEMPLATES.items():
        gen_page(slug, data)
    print(f"[AFFILIATE] {len(TEMPLATES)} pages ready at {BASE}")

if __name__ == "__main__":
    main()
