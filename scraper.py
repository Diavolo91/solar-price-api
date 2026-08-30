import json
import requests
from datetime import datetime

def update_price():
    # نرخ مبنای کیلووات ساعت برق سبز تحویلی به صنایع بر حسب ریال
    # صنایع بالای ۱ مگاوات مشمول ماده ۱۶ موظف به تسویه بر اساس این میانگین کشف‌شده در بورس هستند
    industrial_green_tariff = 38500  # ریال به ازای هر کیلووات ساعت

    data = {
        "market": "IRENEX_Green_Board_Industry",
        "regulation": "Article 16 Knowledge-Based Production Leap Law",
        "price_per_kwh_irr": industrial_green_tariff,
        "price_per_mwh_irr": industrial_green_tariff * 1000,
        "unit": "IRR/kWh",
        "target_sector": "Industrial (>1MW)",
        "updated_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    }

    with open("price.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    update_price()
