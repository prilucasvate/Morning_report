import time
import colorama
from datetime import datetime

# 匯入所有模組
from core import audio_control, tts_engine, state_manager, vosk_trigger, weather_service, calendar_service

# 匯入配置 (API keys)
try:
    from config import CWA_API_KEY, OPENAI_API_KEY
except ImportError:
    print("[錯誤] 找不到 config.py！")
    print("請複製 config.example.py 為 config.py 並填入你的 API Keys。")
    exit(1)

# ================= 設定區 v3 =================
# 1. 語音喚醒設定 (Vosk Grammar)
VOSK_MODEL_PATH = r"C:\Users\user\Desktop\wakeup\vosk-model-small-cn-0.22"
TRIGGER_WORD = "早安"

# 2. 氣象設定 (Taiwan CWA)
# CWA_API_KEY 從 config.py 匯入
LOCATION_CITY = "臺南市" # 請填入你的縣市 (臺北市, 新北市, 臺中市, 高雄市 等)

# 3. 語音設定 (TTS)
TTS_PROVIDER = "EDGE"  # 選項: "EDGE" (免費) / "OPENAI" (付費, 高音質)
# OPENAI_API_KEY 從 config.py 匯入

# 4. 使用者與流程設定
USER_NAME = "挖 哩"
DELAY_SECONDS = 0
# ============================================

def run_morning_flow():
    """
    早晨播報流程 v3 (完整版)
    """
    print(colorama.Fore.GREEN + "  [Go] 喚醒成功！執行早晨流程..." + colorama.Style.RESET_ALL)

    # 1. 暫停 Spotify
    audio_control.toggle_media_playback()

    # 2. 延遲
    print(f"  [Wait] 等待 {DELAY_SECONDS} 秒 (請移動到廁所)...")
    time.sleep(DELAY_SECONDS)

    # 3. 準備播報內容
    now = datetime.now()
    hour = now.hour
    minute = now.minute

    # 判斷時段
    if 0 <= hour < 6:
        period = "凌晨"
    elif 6 <= hour < 11:
        period = "上午"
    elif 11 <= hour < 13:
        period = "中午"
    elif 13 <= hour < 18:
        period = "下午"
    else:
        period = "晚上"

    # 轉換 12 小時制
    display_hour = hour if hour <= 12 else hour - 12
    if display_hour == 0: display_hour = 12
    
    now_str = f"{period} {display_hour}點{minute}分"
    
    # [Weather]
    # weather_summary = weather_service.get_weather_report(OPENWEATHER_API_KEY, LATITUDE, LONGITUDE)
    weather_summary = weather_service.get_cwa_weather_report(CWA_API_KEY, LOCATION_CITY)
    
    # [Calendar]
    calendar_summary = calendar_service.get_todays_schedule(limit=3)
    
    # 組合
    script = (
        f"早安，{USER_NAME}。現在時間是 {now_str}。"
        f"{weather_summary} "
        f"{calendar_summary}"
        f"祝你今天順利！"
    )
    
    print(colorama.Fore.MAGENTA + "  [Speak] 開始播報..." + colorama.Style.RESET_ALL)
    print(colorama.Fore.LIGHTBLACK_EX + f"  (內容: {script})" + colorama.Style.RESET_ALL)
    
    # 語速稍微加快一點點 (200)
    tts_engine.speak(script, rate=132, provider=TTS_PROVIDER, openai_key=OPENAI_API_KEY)

    # 4. 恢復 Spotify
    print("  [Audio] 恢復音樂播放...")
    audio_control.toggle_media_playback()

    # 5. 紀錄狀態
    # state_manager.mark_as_done()
    print(colorama.Fore.CYAN + "[Done] 流程結束。繼續監聽...\n" + colorama.Style.RESET_ALL)

def main():
    colorama.init()
    print(colorama.Fore.YELLOW + "=== 早晨語音助理 v3 (最終完整版) ===" + colorama.Style.RESET_ALL)
    print(f"位置: {LOCATION_CITY}")


    # 初始化 Vosk Listener
    try:
        print(f"正在監聽喚醒詞 (Vosk Grammar Mode): {TRIGGER_WORD}")
        
        listener = vosk_trigger.VoskGrammarListener(
            model_path=VOSK_MODEL_PATH,
            trigger_word=TRIGGER_WORD
        )
        
        while True:
            # Vosk 的 listen_chunk 會回傳 True/False
            is_triggered = listener.listen_chunk()
            
            if is_triggered:
                print(colorama.Fore.CYAN + f"\n[WakeWord] 聽到 '{TRIGGER_WORD}' 了！" + colorama.Style.RESET_ALL)
                
                # 條件檢查
                if not state_manager.is_within_time_window():
                    print(colorama.Fore.YELLOW + "  [Skip] 非早晨時間，忽略呼叫。" + colorama.Style.RESET_ALL)
                    continue
                
                if state_manager.has_run_today():
                    print(colorama.Fore.YELLOW + "  [Skip] 今天已經執行過了，忽略呼叫。" + colorama.Style.RESET_ALL)
                    continue
                
                # 執行流程
                run_morning_flow()
                
                # 執行完後稍微清空 buffer，避免連續觸發 (Vosk buffer)
                listener.recognizer.Reset()
                
    except KeyboardInterrupt:
        print("\n使用者中斷。")
    except Exception as e:
        print(f"\n發生錯誤: {e}")
    finally:
        if 'listener' in locals():
            listener.close()

if __name__ == "__main__":
    main()
