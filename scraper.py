import json
import re
from datetime import datetime
from playwright.sync_api import sync_playwright

def fetch_live_green_price():
    extracted_price = None
    fetch_status = "fallback"

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            # باز کردن صفحه و منتظر ماندن تا جاوااسکریپت‌ها و جدول‌ها لود شوند
            page.goto("https://irenex.ir/TradeStatistics/Physical", timeout=60000, wait_until="networkidle")
            page.wait_for_timeout(5000)

            content = page.content()
            browser.close()

            # جستجوی تابلوی برق سبز در متن رندر شده
            if "سبز" in content or "برق" in content:
                # استخراج اعداد ۵ یا ۶ رقمی مربوط به نرخ ریالی
                matches = re.findall(r'(\d{2,3}[,\.]\d{3})', content)
                for m in matches:
                    clean = int(m.replace(",", "").replace(".", ""))
                    if 30000 <= clean <= 250000:
                        extracted_price = clean
                        fetch_status = "live_irenex"
                        break
    except Exception as e:
        print(f"Browser automation failed: {e}")

    if not extracted_price:
        extracted_price = 110000  # نرخ پیش‌فرض پشتیبان
        fetch_status = "fallback"

    return extracted_price, fetch_status

def update_price():
    live_price, fetch_status = fetch_live_green_price()
    setup_cost_per_kw = 250000000

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
