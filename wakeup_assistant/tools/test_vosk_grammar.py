import os
import sys
import pyaudio
import json
import colorama

try:
    from vosk import Model, KaldiRecognizer
except ImportError:
    print("請先安裝 vosk: pip install vosk")
    sys.exit(1)

# 模型路徑 (你之前的路徑)
MODEL_PATH = r"C:\Users\user\Desktop\wakeup\vosk-model-small-cn-0.22"

def main():
    colorama.init()
    print(colorama.Fore.YELLOW + "=== Vosk 強制語法模式測試 (Grammar Mode) ===" + colorama.Style.RESET_ALL)

    if not os.path.exists(MODEL_PATH):
        print(colorama.Fore.RED + f"找不到模型: {MODEL_PATH}" + colorama.Style.RESET_ALL)
        return

    print("正在載入模型...")
    model = Model(MODEL_PATH)

    # 關鍵：設定 grammar 只接受「早安」和「[unk]」(代表未知/雜音)
    # 這樣就絕對不會跑出「小」、「而」、「壞了」這種怪字
    # 格式: list of strings
    grammar = '["早安", "[unk]"]'
    
    recognizer = KaldiRecognizer(model, 16000, grammar)

    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=4000)
    stream.start_stream()

    print(colorama.Fore.GREEN + "\n準備就緒！請說「早安」..." + colorama.Style.RESET_ALL)
    print("(你會發現現在雜音都不會顯示了，只有真的很像「早安」時才會出現)")

    try:
        while True:
            data = stream.read(4000, exception_on_overflow=False)
            if recognizer.AcceptWaveform(data):
                result = json.loads(recognizer.Result())
                text = result.get("text", "")
                
                # 這裡過濾掉 [unk]
                if text == "早安":
                    print(colorama.Fore.CYAN + f"  [偵測到] {text} !!!" + colorama.Style.RESET_ALL)
                elif text == "[unk]":
                    # 這是雜音，我們忽略不印
                    pass
                elif text:
                    print(f"  (其他): {text}")
                    
    except KeyboardInterrupt:
        print("\n停止測試。")
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()

if __name__ == "__main__":
    main()
