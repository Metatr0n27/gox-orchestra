#!/usr/bin/env python3
"""Monitors price spreads between exchanges for arb opportunities."""
import json,requests
from pathlib import Path

OUTFILE = Path.home()/"HERMES/active_income/crypto_watch/spreads.json"

EXCHANGES = {
    "coinbase": "https://api.coinbase.com/v2/prices/BTC-USD/spot",
    "kraken": "https://api.kraken.com/0/public/Ticker?pair=XBTUSD",
    "binance": "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT",
}

def fetch_price(exchange, url):
    try:
        r = requests.get(url, timeout=10)
        d = r.json()
        if exchange == "coinbase":
            return float(d["data"]["amount"])
        elif exchange == "kraken":
            return float(d["result"]["XXBTZUSD"]["c"][0])
        elif exchange == "binance":
            return float(d["price"])
    except:
        return None

def find_arbs():
    prices = {}
    for ex, url in EXCHANGES.items():
        prices[ex] = fetch_price(ex, url)
    
    valid = {k:v for k,v in prices.items() if v}
    if len(valid) < 2:
        print("[CRYPTO] Insufficient data")
        return
    
    sorted_prices = sorted(valid.items(), key=lambda x: x[1])
    lowest = sorted_prices[0]
    highest = sorted_prices[-1]
    
    spread_pct = ((highest[1] - lowest[1]) / lowest[1]) * 100
    
    result = {
        "buy_exchange": lowest[0],
        "buy_price": lowest[1],
        "sell_exchange": highest[0],
        "sell_price": highest[1],
        "spread_percent": round(spread_pct, 3),
        "timestamp": __import__("datetime").datetime.now().isoformat()
    }
    
    OUTFILE.write_text(json.dumps(result, indent=2))
    
    if spread_pct > 0.5:
        print(f"[CRYPTO] ARBITRAGE ALERT: {spread_pct:.2f}% spread!")
        print(f"  Buy @{lowest[0]}: ${lowest[1]:,.2f}")
        print(f"  Sell @{highest[0]}: ${highest[1]:,.2f}")
    else:
        print(f"[CRYPTO] Spread: {spread_pct:.3f}% (below threshold)")

if __name__ == "__main__":
    find_arbs()
