import json
import re
import requests
import urllib3
from datetime import datetime

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def fetch_live_green_price():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "X-Requested-With": "XMLHttpRequest",
        "Referer": "https://irenex.ir/TradeStatistics/Physical"
    }

    extracted_price = None

    # اندپوینت‌های متداول ایجکس بورس انرژی برای واکشی جدول آمار معاملات فیزیکی
    endpoints = [
        "https://irenex.ir/TradeStatistics/PhysicalData",
        "https://irenex.ir/TradeStatistics/GetPhysicalTrades",
        "https://irenex.ir/api/trade/physical"
    ]

    for ep in endpoints:
        try:
            res = requests.get(ep, headers=headers, timeout=15, verify=False)
            if res.status_code == 200 and "application/json" in res.headers.get("Content-Type", ""):
                data = res.json()
                data_str = json.dumps(data, ensure_ascii=False)
                if "سبز" in data_str or "برق" in data_str:
                    # استخراج اولین قیمت منطقی مربوط به برق سبز (عددهای ریالی بالای ۱۰۰۰۰)
                    matches = re.findall(r'"(?:Price|LastPrice|AveragePrice|Rate)":\s*(\d+)', data_str)
                    for m in matches:
                        if int(m) > 10000:
                            extracted_price = int(m)
                            break
            if extracted_price:
                break
        except Exception:
            continue

    if extracted_price:
        print(f"SUCCESS: Fetched live market price: {extracted_price}")
        fetch_status = "live_irenex"
    else:
        print("NOTICE: Live board not available (market closed or JS-only). Using standard industrial rate.")
        extracted_price = 110000  # نرخ مبنای مصوب ماده ۱۶ برق صنایع (۱۱۰,۰۰۰ ریال)
        fetch_status = "fallback"

    return extracted_price, fetch_status

def update_price():
    live_price, fetch_status = fetch_live_green_price()

    # هزینه احداث هر کیلووات نیروگاه خورشیدی (قابل ویرایش دستی بدون آپدیت اپلیکیشن)
    setup_cost_per_kw = 250000000  # ۲۵ میلیون تومان بر حسب ریال

    data = {
        "market": "IRENEX_Green_Board_Industry",
        "regulation": "Article 16 Knowledge-Based Production Leap Law",
        "price_per_kwh_irr": live_price,
        "price_per_mwh_irr": live_price * 1000,
        "setup_cost_per_kw_irr": setup_cost_per_kw,
        "unit": "IRR",
        "target_sector": "Industrial (>1MW)",
        "source_status": fetch_status,
        "updated_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    }

    with open("price.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    update_price()
