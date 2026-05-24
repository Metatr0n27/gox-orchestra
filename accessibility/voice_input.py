#!/home/metatron/HERMES/venv/bin/python3
import speech_recognition as sr
import sys

def listen():
    r = sr.Recognizer()
    r.energy_threshold = 400  
    r.dynamic_energy_threshold = True
    r.pause_threshold = 0.8
    
    with sr.Microphone(device_index=None) as src:
        print("[SPEAK NOW]", flush=True)
        r.adjust_for_ambient_noise(src, duration=1)
        try:
            audio = r.listen(src, timeout=10, phrase_time_limit=20)
            text = r.recognize_google(audio)
            return text
        except sr.UnknownValueError:
            print("[TRY AGAIN - unclear]", flush=True)
            return None
        except sr.RequestError as e:
            print(f"[SERVICE ERROR] {e}", flush=True)
            return None
        except Exception as e:
            print(f"[ERROR] {e}", flush=True)
            return None

if __name__ == "__main__":
    result = listen()
    if result:
        print(result)
