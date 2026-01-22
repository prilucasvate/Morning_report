import asyncio
import edge_tts
import pygame
import os
import time
from openai import OpenAI

# Edge TTS 設定
EDGE_VOICE = "zh-TW-HsiaoChenNeural"

# OpenAI TTS 設定
# models: tts-1 (快), tts-1-hd (高畫質)
# voices: alloy (中性), echo (男), fable (英式), onyx (男), nova (女, 推薦), shimmer (女, 溫柔)
OPENAI_MODEL = "tts-1"
OPENAI_VOICE = "sage"

OUTPUT_FILE = "tts_output.mp3"

def _play_audio(file_path):
    """使用 Pygame 播放音訊檔"""
    try:
        pygame.mixer.init()
        pygame.mixer.music.load(file_path)
        pygame.mixer.music.play()
        
        # 等待播放結束
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
            
        pygame.mixer.quit()
    except Exception as e:
        print(f"  [Audio Error] 播放失敗: {e}")

# --- Edge TTS ---
async def _generate_audio_edge(text, rate_str):
    communicate = edge_tts.Communicate(text, EDGE_VOICE, rate=rate_str)
    await communicate.save(OUTPUT_FILE)

# --- OpenAI TTS ---
def _generate_audio_openai(text, api_key):
    client = OpenAI(api_key=api_key)
    response = client.audio.speech.create(
        model=OPENAI_MODEL,
        voice=OPENAI_VOICE,
        input=text,
        speed=0.95 # 0.25 ~ 4.0
    )
    # 儲存到檔案
    response.stream_to_file(OUTPUT_FILE)

def speak(text, rate=130, provider="EDGE", openai_key=None):
    """
    執行語音播報
    :param provider: "EDGE" or "OPENAI"
    :param openai_key: if provider is OPENAI, this is required
    """
    
    if provider == "OPENAI":
        if not openai_key:
            print("  [TTS Error] 使用 OpenAI 需提供 API Key！切換回 Edge TTS。")
            provider = "EDGE"
        else:
            print(f"  [TTS] (OpenAI/{OPENAI_VOICE}) 正在合成: {text[:15]}...")
            try:
                _generate_audio_openai(text, openai_key)
                if os.path.exists(OUTPUT_FILE):
                    _play_audio(OUTPUT_FILE)
                    try: os.remove(OUTPUT_FILE) 
                    except: pass
                return # OpenAI 成功則返回
            except Exception as e:
                print(f"  [TTS Error] OpenAI 失敗: {e}。切換回 Edge TTS。")
                provider = "EDGE"

    # Edge TTS Fallback
    print(f"  [TTS] (Edge) 正在合成: {text[:15]}...")
    
    # 語速轉換
    if rate > 130: rate_str = "+10%"
    elif rate < 100: rate_str = "-10%"
    else: rate_str = "+0%"

    try:
        asyncio.run(_generate_audio_edge(text, rate_str))
        if os.path.exists(OUTPUT_FILE):
             _play_audio(OUTPUT_FILE)
             try: os.remove(OUTPUT_FILE)
             except: pass
    except Exception as e:
        print(f"  [TTS Error] Edge TTS 失敗: {e}")
