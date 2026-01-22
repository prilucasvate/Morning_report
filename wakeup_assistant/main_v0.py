import time
import keyboard
import colorama
from datetime import datetime

# 匯入我們寫的核心模組
from core import audio_control, tts_engine, state_manager

# 設定檔
HOTKEY = 'ctrl+alt+g'
USER_NAME = "主人"
DELAY_SECONDS = 15  # 刷牙走到廁所的時間

def morning_routine():
    """
    早晨喚醒流程：
    1. 檢查時間窗與狀態 (Double check)
    2. 暫停音樂
    3. 延遲
    4. 播報
    5. 恢復音樂
    6. 寫入狀態
    """
    print(colorama.Fore.CYAN + "\n[Trigger] 收到觸發訊號！檢查條件..." + colorama.Style.RESET_ALL)

    # 1. 條件檢查
    if not state_manager.is_within_time_window():
        print(colorama.Fore.YELLOW + "  [Skip] 現在不在早晨時間窗內 (06:30 - 11:00)。忽略。" + colorama.Style.RESET_ALL)
        return

    if state_manager.has_run_today():
        print(colorama.Fore.YELLOW + "  [Skip] 今天已經執行過早晨播報了。忽略。" + colorama.Style.RESET_ALL)
        return

    print(colorama.Fore.GREEN + "  [Go] 條件符合，開始執行早晨流程！" + colorama.Style.RESET_ALL)

    # 2. 暫停 Spotify
    audio_control.toggle_media_playback()

    # 3. 延遲 (讓你有時間走去刷牙)
    print(f"  [Wait] 等待 {DELAY_SECONDS} 秒 (請移動到廁所)...")
    time.sleep(DELAY_SECONDS)

    # 4. TTS 播報
    # 這裡先用 v0 的固定假資料
    now_str = datetime.now().strftime("%H點%M分")
    weather_summary = "今天天氣晴朗，氣溫 25 度，適合外出。"
    todo_summary = "上午 10 點有一個團隊會議。"
    
    script = f"早安，{USER_NAME}。現在時間是 {now_str}。{weather_summary} {todo_summary} 祝你有個美好的一天！"
    
    print(colorama.Fore.MAGENTA + "  [Speak] 開始播報..." + colorama.Style.RESET_ALL)
    tts_engine.speak(script)

    # 5. 恢復 Spotify
    print("  [Audio] 恢復音樂播放...")
    audio_control.toggle_media_playback()

    # 6. 紀錄狀態
    state_manager.mark_as_done()
    print(colorama.Fore.CYAN + "[Done] 流程結束。\n" + colorama.Style.RESET_ALL)


def main():
    colorama.init()
    print(colorama.Fore.YELLOW + "=== 早晨語音助理 v0 (Hotkey版) 啟動 ===" + colorama.Style.RESET_ALL)
    print(f"監聽熱鍵: {HOTKEY}")
    print(f"時間窗限制: {state_manager.START_HOUR:02d}:{state_manager.START_MINUTE:02d} ~ {state_manager.END_HOUR:02d}:{state_manager.END_MINUTE:02d}")
    print("按下 Ctrl+C 可結束程式。")

    # 註冊熱鍵
    # 注意：keyboard.add_hotkey 是非 blocking 的，會起一個 thread 監聽
    keyboard.add_hotkey(HOTKEY, morning_routine)

    # 保持主程式運作
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n程式結束。")

if __name__ == "__main__":
    main()
