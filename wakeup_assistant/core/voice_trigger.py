import pvporcupine
import pyaudio
import struct
import colorama

class WakeWordListener:
    def __init__(self, access_key, keyword_paths=None, model_path=None, sensitivity=0.5):
        """
        初始化 Porcupine
        :param access_key: Picovoice Console 取得的 AccessKey
        :param keyword_paths: 自訂喚醒詞檔案的路徑列表 (.ppn)。若為 None，則使用預設關鍵詞。
        :param model_path: (Optional) 語言模型檔案路徑 (.pv)，若唤醒詞非英文則必須提供。
        :param sensitivity: 靈敏度 (0~1)
        """
        try:
            # 如果有自訂檔案 (.ppn) 就用 keyword_paths
            if keyword_paths:
                self.porcupine = pvporcupine.create(
                    access_key=access_key,
                    keyword_paths=keyword_paths,
                    model_path=model_path,
                    sensitivities=[sensitivity] * len(keyword_paths)
                )
            else:
                # 預設使用 'jarvis'

                print(colorama.Fore.YELLOW + "  [Init] 未指定喚醒詞檔案，使用預設喚醒詞: Jarvis" + colorama.Style.RESET_ALL)
                self.porcupine = pvporcupine.create(
                    access_key=access_key,
                    keywords=['jarvis']
                )

            self.pa = pyaudio.PyAudio()
            self.stream = self.pa.open(
                rate=self.porcupine.sample_rate,
                channels=1,
                format=pyaudio.paInt16,
                input=True,
                frames_per_buffer=self.porcupine.frame_length
            )
        except Exception as e:
            print(colorama.Fore.RED + f"  [Error] Porcupine 初始化失敗: {e}" + colorama.Style.RESET_ALL)
            raise e

    def listen_one_frame(self):
        """
        讀取一段音訊並檢測
        :return: keyword_index (如果偵測到) or -1 (沒偵測到)
        """
        try:
            pcm = self.stream.read(self.porcupine.frame_length, exception_on_overflow=False)
            pcm = struct.unpack_from("h" * self.porcupine.frame_length, pcm)
            keyword_index = self.porcupine.process(pcm)
            return keyword_index
        except Exception as e:
            # print(f"Audio Error: {e}") 
            return -1

    def close(self):
        if self.stream is not None:
            self.stream.close()
        if self.pa is not None:
            self.pa.terminate()
        if self.porcupine is not None:
            self.porcupine.delete()
