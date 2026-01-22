import json
import os
from datetime import datetime
import colorama

STATE_FILE = "state.json"

# 設定時間窗 (24小時制)
START_HOUR = 0
START_MINUTE = 0
END_HOUR = 23
END_MINUTE = 59

def get_today_date_str():
    return datetime.now().strftime("%Y-%m-%d")

def is_within_time_window():
    """
    檢查現在時間是否在設定的早晨時間窗內
    """
    now = datetime.now()
    start_time = now.replace(hour=START_HOUR, minute=START_MINUTE, second=0, microsecond=0)
    end_time = now.replace(hour=END_HOUR, minute=END_MINUTE, second=0, microsecond=0)
    
    return start_time <= now <= end_time

def has_run_today():
    """
    檢查 state.json，看今天的日期是否已經被記錄過
    """
    if not os.path.exists(STATE_FILE):
        return False
    
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            last_run = data.get("last_run_date")
            return last_run == get_today_date_str()
    except (json.JSONDecodeError, IOError):
        return False

def mark_as_done():
    """
    將今天日期寫入 state.json
    """
    data = {
        "last_run_date": get_today_date_str(),
        "last_run_time": datetime.now().strftime("%H:%M:%S")
    }
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(colorama.Fore.GREEN + f"  [State] 已紀錄今日執行狀態 ({data['last_run_date']})" + colorama.Style.RESET_ALL)
