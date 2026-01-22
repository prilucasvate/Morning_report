import pyttsx3
import colorama

def list_and_test_voices():
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    
    print(colorama.Fore.CYAN + "\n=== Windows 系統可用語音列表 ===" + colorama.Style.RESET_ALL)
    
    for idx, voice in enumerate(voices):
        print(f"ID: {colorama.Fore.YELLOW}{idx}{colorama.Style.RESET_ALL}")
        print(f"Name: {voice.name}")
        print(f"Languages: {voice.languages}")
        print("-" * 30)
        
    print(colorama.Fore.GREEN + "\n請輸入 ID 來試聽 (輸入 q 離開):" + colorama.Style.RESET_ALL)
    
    while True:
        choice = input("> ")
        if choice.lower() == 'q':
            break
            
        try:
            v_idx = int(choice)
            if 0 <= v_idx < len(voices):
                target_voice = voices[v_idx]
                print(f"正在試聽: {target_voice.name}")
                
                engine.setProperty('voice', target_voice.id)
                engine.say(f"你好，我是 {target_voice.name}，這是早晨助理的語音測試。")
                engine.runAndWait()
            else:
                print("無效的 ID")
        except ValueError:
            print("請輸入數字")

if __name__ == "__main__":
    colorama.init()
    list_and_test_voices()
