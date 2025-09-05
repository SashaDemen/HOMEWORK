import os, requests, datetime

API_KEY = os.environ.get("OPENWEATHER_API_KEY")

def _recommendation(main: str) -> str:
    m = (main or "").lower()
    if "thunder" in m:
        return "Візьми 'М'ясну' — енергії вистачить на грози!"
    if "rain" in m or "drizzle" in m:
        return "Соковита 'Пепероні' зігріє в дощ ☔"
    if "snow" in m:
        return "Хочеться теплого — '4 Сири' ідеально ❄️"
    if "clear" in m:
        return "Сонячно? Класична 'Маргарита' саме те ☀️"
    if "cloud" in m:
        return "Хмарно? Спробуй 'Гавайську' з ананасом ☁️"
    return "Будь-яка піца — гарна ідея 😊"

def get_weather(city: str, date_str: str):
    if not API_KEY:
        return {"error":"Set OPENWEATHER_API_KEY env var", "recommendation":"Візьми будь-яку піцу :)", "source":"none"}

    try:
        target_date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
    except Exception:
        target_date = datetime.date.today()

    today = datetime.date.today()
    try:
        if target_date <= today:
            # use current weather (close enough for demo)
            url = "https://api.openweathermap.org/data/2.5/weather"
            r = requests.get(url, params={"q": city, "appid": API_KEY, "units":"metric"}, timeout=8)
            data = r.json()
            main = (data.get("weather") or [{}])[0].get("main","")
            temp = (data.get("main") or {}).get("temp")
            return {
                "city": data.get("name") or city,
                "date": target_date.isoformat(),
                "temp": temp,
                "main": main,
                "source": "current",
                "recommendation": _recommendation(main),
            }
        else:
            # forecast 5-day/3h
            url = "https://api.openweathermap.org/data/2.5/forecast"
            r = requests.get(url, params={"q": city, "appid": API_KEY, "units":"metric"}, timeout=8)
            data = r.json()
            best = None
            target_dt = datetime.datetime.combine(target_date, datetime.time(12,0))
            for item in data.get("list", []):
                dt = datetime.datetime.fromtimestamp(item.get("dt",0))
                if best is None or abs(dt - target_dt) < abs(best["dt"] - target_dt):
                    best = {"dt": dt, "item": item}
            if not best:
                return {"error":"No forecast found", "source":"forecast"}
            itm = best["item"]
            main = (itm.get("weather") or [{}])[0].get("main","")
            temp = (itm.get("main") or {}).get("temp")
            city_name = (data.get("city") or {}).get("name") or city
            return {
                "city": city_name,
                "date": target_date.isoformat(),
                "temp": temp,
                "main": main,
                "source": "forecast",
                "recommendation": _recommendation(main),
            }
    except Exception as e:
        return {"error": str(e), "recommendation":"Замов 'Маргариту' — не прогадаєш", "source":"error"}
