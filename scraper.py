import json
import requests
from datetime import datetime

def update_price():
    # مقدار قیمت برق سبز (در صورت فعال بودن وب‌اسکرپینگ از صفحه بورس انرژی استخراج می‌شود)
    current_price = 38500  # ریال به ازای هر کیلووات ساعت

    data = {
        "price_per_kwh_irr": current_price,
        "updated_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
        "source": "IRENEX Green Board"
    }

    # ذخیره در قالب فایل json
    with open("price.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    update_price()
