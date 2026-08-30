import json
import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime

def fetch_live_green_price():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
    }

    url = "https://www.irenex.ir/TradeStatistics/Physical"
    extracted_price = None

    try:
        response = requests.get(url, headers=headers, timeout=20)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            
            for row in soup.find_all("tr"):
                row_text = row.get_text()
                if "برق سبز" in row_text or "سبز" in row_text:
                    cells = row.find_all(["td", "th"])
                    for cell in reversed(cells):
                        clean_val = re.sub(r"[^\d]", "", cell.get_text().strip())
                        if clean_val and int(clean_val) > 10000:
                            extracted_price = int(clean_val)
                            break
                if extracted_price:
                    break
    except Exception as e:
        print(f"Direct scrape failed: {e}")

    # تعیین وضعیت اتصال و اعمال نرخ پشتیبان در صورت عدم دریافت داده زنده
    if extracted_price:
        print(f"SUCCESS: Successfully fetched live price from IRENEX: {extracted_price}")
        fetch_status = "live_irenex"
    else:
        print("WARNING: Could not parse IRENEX page. Falling back to default price.")
        extracted_price = 120000  # نرخ پیش‌فرض پشتیبان (ریال)
        fetch_status = "fallback"

    return extracted_price, fetch_status

def update_price():
    live_price, fetch_status = fetch_live_green_price()

    # هزینه احداث هر کیلووات نیروگاه خورشیدی بر حسب ریال (قابل ویرایش دستی)
    setup_cost_per_kw = 250000000  # معادل ۲۵ میلیون تومان

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
