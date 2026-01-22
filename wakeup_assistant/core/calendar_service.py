import json
import os
from datetime import datetime

CALENDAR_FILE = r"C:\Users\user\Desktop\wakeup\wakeup_assistant\calendar.json"

def get_todays_schedule(limit=3):
    """
    讀取 calendar.json 並回傳適合播報的行程摘要 (支援每週固定行程)。
    """
    if not os.path.exists(CALENDAR_FILE):
        return "今天沒有特別的行程記錄。"

    try:
        with open(CALENDAR_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        today = datetime.now()
        current_time = today.strftime("%H:%M")
        today_date_str = today.strftime("%Y-%m-%d")
        week_day_name = today.strftime("%A") # e.g. "Monday"

        todays_events = []

        # 1. 載入每週固定行程 (Weekly)
        if "weekly" in data:
            weekly_events = data["weekly"].get(week_day_name, [])
            for event in weekly_events:
                # 只有時間和標題，直接加入
                todays_events.append(event)

        # 2. 載入特定日期行程 (Specific)
        if "specific" in data:
            for event in data["specific"]:
                if event.get("date") == today_date_str:
                    todays_events.append(event)

        # 3. 排序 (依時間)
        todays_events.sort(key=lambda x: x["time"])

        # 4. 過濾已結束的行程
        upcoming_events = [e for e in todays_events if e.get("time") > current_time]
        
        # --- 產生回覆文字 ---

        # Case A: 完全無行程
        if not todays_events:
            return "今天原本就沒有安排任何行程，輕鬆的一天！"

        # Case B: 有行程但都結束了
        if not upcoming_events:
            return "今天原本安排的行程都已經結束了，可以好好休息。"

        # Case C: 還有行程
        count = len(upcoming_events)
        targets = upcoming_events[:limit]
        
        day_name_zh = {
            "Monday": "週一", "Tuesday": "週二", "Wednesday": "週三",
            "Thursday": "週四", "Friday": "週五", "Saturday": "週六", "Sunday": "週日"
        }.get(week_day_name, "")
        
        speech_parts = [f"今天是{day_name_zh}，接下來還有 {count} 個行程。"]
        
        for event in targets:
            # 1. 取得原本的時間字串 (例如 "22:00")
            raw_time = event["time"]
            
            # 2. 切割字串並轉成整數 (22:00 -> hour=22, minute=0)
            hour, minute = map(int, raw_time.split(":"))

            # 3. 判斷時段 (上午/下午)
            period = "上午"
            if hour >= 12:
                period = "下午"

            # 4. 數學轉換：把 24 小時制轉成 12 小時制
            if hour > 12:
                hour -= 12      # 13點~23點 -> 減12變成 1點~11點
            elif hour == 0:
                hour = 12       # 00點 (半夜) -> 改叫 12點

            # 5. 組裝字串 ( f-string 語法 )
            # {minute:02d} 的意思是：如果分鐘只有一位數(例如5)，前面自動補0變成 "05"
            time_str = f"{period} {hour}點{minute:02d}分"
            
            summary = event["summary"]
            speech_parts.append(f"{time_str} {summary}。")
            
        return "".join(speech_parts)

    except Exception as e:
        print(f"  [Calendar Error] {e}")
        return "讀取行程表失敗，請檢查格式。"
