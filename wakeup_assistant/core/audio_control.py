import keyboard
import time

def toggle_media_playback():
    """
    模擬按下 Windows 的 'Play/Pause' 媒體鍵。
    如果音樂正在播放，會暫停；如果暫停，會播放。
    """
    print("  [Audio] 發送 Play/Pause 訊號...")
    keyboard.send('play/pause media')
    # 給系統一點反應時間
    time.sleep(0.5)
