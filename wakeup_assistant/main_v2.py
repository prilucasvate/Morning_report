import time
import colorama
from datetime import datetime

# 匯入模組
from core import audio_control, tts_engine, state_manager, voice_trigger, weather_service

# 匯入配置 (API keys)
try:
    from config import PICOVOICE_ACCESS_KEY, OPENWEATHER_API_KEY
except ImportError:
    print("[錯誤] 找不到 config.py！請複製 config.example.py 為 config.py 並填入 API Keys。")
    exit(1)

# ================= 設定區 v2 =================
# Picovoice (v1) - API keys 從 config.py 匯入
KEYWORD_PATHS = [r"C:\Users\user\Desktop\大學\wakeup\早安_zh_windows_v4_0_0.ppn"]
MODEL_PATH = r"C:\Users\user\Desktop\大學\wakeup\porcupine_params_zh.pv"

# OpenWeatherMap (v2) - API key 從 config.py 匯入

# 位置: 台北市 (預設)
LATITUDE = 23.034123
LONGITUDE = 120.308709
USER_NAME = "挖哩"
DELAY_SECONDS = 5
# ============================================

def run_morning_flow():
    """
    早晨播報流程 v2 (加入即時天氣)
    """
    print(colorama.Fore.GREEN + "  [Go] 喚醒成功！執行早晨流程..." + colorama.Style.RESET_ALL)

    # 1. 暫停 Spotify
    audio_control.toggle_media_playback()

    # 2. 延遲
    print(f"  [Wait] 等待 {DELAY_SECONDS} 秒 (請移動到廁所)...")
    time.sleep(DELAY_SECONDS)

    # 3. 準備播報內容 (同時抓取天氣)
    now_str = datetime.now().strftime("%H點%M分")
    
    # [Modify] 抓取真實天氣
    weather_summary = weather_service.get_weather_report(OPENWEATHER_API_KEY, LATITUDE, LONGITUDE)
    
    todo_summary = "上午 10 點有一個團隊會議。" # v3 才會改成真的
    
    script = f"早安，{USER_NAME}。現在時間是 {now_str}。{weather_summary} {todo_summary}"
    
    print(colorama.Fore.MAGENTA + "  [Speak] 開始播報..." + colorama.Style.RESET_ALL)
    tts_engine.speak(script, rate=200) # 使用 user 調整過的語速

    # 4. 恢復 Spotify
    print("  [Audio] 恢復音樂播放...")
    audio_control.toggle_media_playback()

    # 5. 紀錄狀態
    state_manager.mark_as_done()
    print(colorama.Fore.CYAN + "[Done] 流程結束。繼續監聽...\n" + colorama.Style.RESET_ALL)

def main():
    colorama.init()
    print(colorama.Fore.YELLOW + "=== 早晨語音助理 v2 (天氣整合版) ===" + colorama.Style.RESET_ALL)
    
    # 初始化 Porcupine
    try:
        # v1 既有邏輯：檢查模型路徑
        if KEYWORD_PATHS and MODEL_PATH:
            import os
            if not os.path.exists(MODEL_PATH):
                print(colorama.Fore.RED + f"[Error] 找不到中文模型檔案！({MODEL_PATH})" + colorama.Style.RESET_ALL)
                return

        listener = voice_trigger.WakeWordListener(
            access_key=PICOVOICE_ACCESS_KEY,
            keyword_paths=KEYWORD_PATHS,
            model_path=MODEL_PATH if KEYWORD_PATHS else None
        )
        print(f"正在監聽喚醒詞... (Lat:{LATITUDE}, Lon:{LONGITUDE})")
        
        while True:
            keyword_index = listener.listen_one_frame()
            if keyword_index >= 0:
                print(colorama.Fore.CYAN + "\n[WakeWord] 聽到喚醒詞了！" + colorama.Style.RESET_ALL)
                
                # 條件檢查
                if not state_manager.is_within_time_window():
                    print(colorama.Fore.YELLOW + "  [Skip] 非早晨時間，忽略呼叫。" + colorama.Style.RESET_ALL)
                    continue
                
                if state_manager.has_run_today():
                    print(colorama.Fore.YELLOW + "  [Skip] 今天已經執行過了，忽略呼叫。" + colorama.Style.RESET_ALL)
                    continue
                
                # 執行流程
                run_morning_flow()
                
    except KeyboardInterrupt:
        print("\n使用者中斷。")
    except Exception as e:
        print(f"\n發生錯誤: {e}")
    finally:
        if 'listener' in locals():
            listener.close()

if __name__ == "__main__":
    main()
