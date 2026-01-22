import requests
import colorama
import json

def get_cwa_weather_report(api_key, city_name):
    """
    呼叫台灣中央氣象署 (CWA) Open Data API 取得天氣預報 (F-C0032-001)。
    :param api_key: CWA API Key (授權碼)
    :param city_name: 縣市名稱 (e.g. "臺南市", "臺北市")
    """
    if not api_key or "YOUR" in api_key:
        print(colorama.Fore.YELLOW + "  [Weather] 未設定 CWA API Key，使用預設資訊。" + colorama.Style.RESET_ALL)
        return "提醒您，請先去申請氣象局的授權碼，才能取得最準確的天氣喔。"

    # CWA 一般天氣預報 (36小時) API
    url = f"https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-C0032-001?Authorization={api_key}&locationName={city_name}"
    
    # fix: 忽略 SSL 憑證錯誤 (解決 SSLCertVerificationError)
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    try:
        print(f"  [Weather] 正在抓取氣象局資料 ({city_name})...")
        response = requests.get(url, timeout=5, verify=False)
        response.raise_for_status()
        data = response.json()

        if not data["success"]:
            return "氣象局 API 回傳錯誤。"

        # 解析資料 (結構有點深)
        # records -> location[0] -> weatherElement -> [WX, PoP, MinT, CI, MaxT]
        location = data["records"]["location"][0]
        elements = {e["elementName"]: e["time"][0]["parameter"]["parameterName"] for e in location["weatherElement"]}
        
        # 取得第一個時段 (最近的 12 小時)
        wx = elements.get("Wx", "未知")       # 天氣現象 (e.g. 多雲短暫雨)
        pop = elements.get("PoP", "0")        # 降雨機率 (%)
        min_t = elements.get("MinT", "20")    # 最低溫
        max_t = elements.get("MaxT", "25")    # 最高溫
        ci = elements.get("CI", "")           # 舒適度 (e.g. 舒適)

        # 組合建議
        advice = ""
        try:
            pop_val = int(pop)
            if pop_val >= 70:
                advice += "降雨機率很高，出門一定要帶傘。"
            elif pop_val >= 30:
                advice += "可能會下雨，建議帶著傘備用。"
            else:
                advice += "不用擔心下雨。"
        except:
            pass

        report = f"今天{city_name}{wx}。氣溫在 {min_t} 到 {max_t} 度之間，感覺{ci}。{advice}"
        return report

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            print(colorama.Fore.YELLOW + "  [Weather] CWA API Key 無效。" + colorama.Style.RESET_ALL)
            return "氣象局授權碼無效，請確認是否複製正確。"
        print(colorama.Fore.RED + f"  [Weather Error] HTTP 錯誤: {e}" + colorama.Style.RESET_ALL)
        return "抱歉，無法取得氣象局資訊。"
        
    except Exception as e:
        print(colorama.Fore.RED + f"  [Weather Error] 未知錯誤: {e}" + colorama.Style.RESET_ALL)
        return "抱歉，讀取天氣資料失敗。"

# 保留舊的 OWM 函式 (雖然後面不會用到，但留著當備份)
def get_weather_report(api_key, lat, lon, language="zh_tw"):
    return "請改用 CWA 函式。"
