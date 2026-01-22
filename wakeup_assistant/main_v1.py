import time
import colorama
from datetime import datetime

# 匯入 v0 寫好的模組 + v1 新模組
from core import audio_control, tts_engine, state_manager, voice_trigger

# 匯入配置 (API keys)
try:
    from config import PICOVOICE_ACCESS_KEY
except ImportError:
    print("[錯誤] 找不到 config.py！請複製 config.example.py 為 config.py 並填入 API Keys。")
    exit(1)

# ================= 設定區 =================
# PICOVOICE_ACCESS_KEY 從 config.py 匯入 

# 如果你有訓練好的 .ppn 檔案 (例如 '早安.ppn')，請填入絕對路徑
KEYWORD_PATHS = [r"C:\Users\user\Desktop\大學\wakeup\早安_zh_windows_v4_0_0.ppn"]
# KEYWORD_PATHS = None  # None 代表使用預設喚醒詞 (Jarvis)

# [NEW] 中文模型檔案 (.pv) 路徑
# 由於使用中文喚醒詞，必須搭配中文模型檔案
MODEL_PATH = r"C:\Users\user\Desktop\大學\wakeup\porcupine_params_zh.pv"

USER_NAME = "主人"
DELAY_SECONDS = 15
# ========================================

def run_morning_flow():
    """
    執行早晨播報流程 (與 v0 相同，只是封裝起來)
    """
    print(colorama.Fore.GREEN + "  [Go] 喚醒成功！執行早晨流程..." + colorama.Style.RESET_ALL)

    # 1. 暫停 Spotify
    audio_control.toggle_media_playback()

    # 2. 延遲
    print(f"  [Wait] 等待 {DELAY_SECONDS} 秒 (請移動到廁所)...")
    time.sleep(DELAY_SECONDS)

    # 3. TTS 播報
    now_str = datetime.now().strftime("%H點%M分")
    weather_summary = "今天天氣多雲轉晴，氣溫舒適。"
    todo_summary = "記得今天要完成語音助理的開發。"
    script = f"早安，{USER_NAME}。現在時間是 {now_str}。{weather_summary} {todo_summary}"
    
    print(colorama.Fore.MAGENTA + "  [Speak] 開始播報..." + colorama.Style.RESET_ALL)
    tts_engine.speak(script)

    # 4. 恢復 Spotify
    print("  [Audio] 恢復音樂播放...")
    audio_control.toggle_media_playback()

    # 5. 紀錄狀態
    state_manager.mark_as_done()
    print(colorama.Fore.CYAN + "[Done] 流程結束。繼續監聽...\n" + colorama.Style.RESET_ALL)

def main():
    colorama.init()
    print(colorama.Fore.YELLOW + "=== 早晨語音助理 v1 (語音喚醒版) ===" + colorama.Style.RESET_ALL)
    
    # 檢查 Key
    if PICOVOICE_ACCESS_KEY == "YOUR_ACCESS_KEY_HERE":
        print(colorama.Fore.RED + "[Error] 請先在 main_v1.py 中填入 Picovoice AccessKey！" + colorama.Style.RESET_ALL)
        return

    try:
        # 檢查 Model Path 是否存在 (若有指定)
        if KEYWORD_PATHS and MODEL_PATH:
            import os
            if not os.path.exists(MODEL_PATH):
                print(colorama.Fore.RED + f"[Error] 找不到中文模型檔案！\n請下載 'porcupine_params_zh.pv' 並放到: {MODEL_PATH}" + colorama.Style.RESET_ALL)
                print(colorama.Fore.YELLOW + "下載位址: https://github.com/Picovoice/porcupine/blob/master/lib/common/porcupine_params_zh.pv" + colorama.Style.RESET_ALL)
                return

        listener = voice_trigger.WakeWordListener(
            access_key=PICOVOICE_ACCESS_KEY,
            keyword_paths=KEYWORD_PATHS,
            model_path=MODEL_PATH if KEYWORD_PATHS else None
        )
        print(f"正在監聽喚醒詞... (預設: Jarvis)")
        print(f"時間窗: {state_manager.START_HOUR:02d}:{state_manager.START_MINUTE:02d} ~ {state_manager.END_HOUR:02d}:{state_manager.END_MINUTE:02d}")
        print("按下 Ctrl+C 結束。")

        while True:
            # 1. 偵測喚醒詞
            keyword_index = listener.listen_one_frame()
            
            if keyword_index >= 0:
                print(colorama.Fore.CYAN + "\n[WakeWord] 聽到喚醒詞了！" + colorama.Style.RESET_ALL)
                
                # 2. 檢查條件
                if not state_manager.is_within_time_window():
                    print(colorama.Fore.YELLOW + "  [Skip] 非早晨時間，忽略呼叫。" + colorama.Style.RESET_ALL)
                    continue
                
                if state_manager.has_run_today():
                    print(colorama.Fore.YELLOW + "  [Skip] 今天已經執行過了，忽略呼叫。" + colorama.Style.RESET_ALL)
                    continue
                
                # 3. 暫停監聽 (避免聽到自己播報的聲音，雖然 Porcupine 主要是擋喚醒詞，但暫停 Mic 是好習慣)
                # 這裡簡單做法是：因為 run_morning_flow 是 blocking 的 (有 sleep 和 tts runAndWait)，
                # 所以主無窮迴圈會卡住，自然就不會去 read mic，這樣就達到了「不監聽」的效果！
                # Porcupine 的 stream read 也是在此 thread，所以很安全。
                
                run_morning_flow()
                
                # 流程結束，迴圈繼續，自動恢復監聽
                print("繼續監聽...")

    except KeyboardInterrupt:
        print("\n使用者中斷。")
    except Exception as e:
        print(f"\n發生錯誤: {e}")
    finally:
        if 'listener' in locals():
            listener.close()

if __name__ == "__main__":
    main()
