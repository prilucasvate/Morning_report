import os
import sys
import json
import pyaudio
import colorama

try:
    from vosk import Model, KaldiRecognizer
except ImportError:
    print("請先安裝 vosk: pip install vosk")
    sys.exit(1)

# 模型預設路徑 (可從外部傳入)
DEFAULT_MODEL_PATH = r"C:\Users\user\Desktop\wakeup\vosk-model-small-cn-0.22"

class VoskGrammarListener:
    def __init__(self, model_path=DEFAULT_MODEL_PATH, trigger_word="早安"):
        """
        初始化 Vosk 監聽器 (Grammar Mode)
        :param model_path: 模型路徑
        :param trigger_word: 欲觸發的詞 (e.g. "早安")
        """
        if not os.path.exists(model_path):
            print(colorama.Fore.RED + f"[Error] 找不到 Vosk 模型: {model_path}" + colorama.Style.RESET_ALL)
            raise FileNotFoundError(f"Model not found at {model_path}")

        print(f"  [Init] 載入 Vosk 模型 ({model_path})...")
        self.model = Model(model_path)
        self.trigger_word = trigger_word
        
        # 設定只接受 trigger_word 和 [unk] (未知雜訊)
        # 注意: Vosk 的 grammar 需要是 json dump 的 list string
        # IMPORTANT: ensure_ascii=False 是必須的，否則會變成 unicode code points，Vosk 看不懂
        grammar = json.dumps([trigger_word, "[unk]"], ensure_ascii=False)
        self.recognizer = KaldiRecognizer(self.model, 16000, grammar)

        self.pa = pyaudio.PyAudio()
        self.stream = self.pa.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=16000,
            input=True,
            frames_per_buffer=4000
        )
        self.stream.start_stream()
        print(f"  [Init] Vosk 監聽器已就緒。觸發詞: {trigger_word}")

    def listen_chunk(self):
        """
        讀取一個音訊區塊並判斷是否觸發
        :return: True (觸發), False (未觸發)
        """
        try:
            data = self.stream.read(4000, exception_on_overflow=False)
            if self.recognizer.AcceptWaveform(data):
                result = json.loads(self.recognizer.Result())
                text = result.get("text", "").replace(" ", "")
                
                # 若完全匹配觸發詞
                if text == self.trigger_word:
                    return True
            else:
                # Partial result (通常不用管，除非要做 real-time feedback)
                pass
                
        except Exception as e:
            print(f"  [Audio Error] {e}")
        
        return False

    def close(self):
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        if self.pa:
            self.pa.terminate()
