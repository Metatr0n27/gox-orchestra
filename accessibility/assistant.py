#!/home/metatron/HERMES/venv/bin/python3
import subprocess
import sys

MODEL = "goxpilot"

def speak(text):
    subprocess.run(['espeak-ng', '-v', 'en-us', '-s', '160', text])

def query_ai(prompt):
    proc = subprocess.Popen(
        ['ollama', 'run', MODEL],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True
    )
    stdout, _ = proc.communicate(input=prompt)
    return stdout.strip()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        prompt = " ".join(sys.argv[1:])
    else:
        prompt = sys.stdin.read().strip()
    
    if not prompt:
        speak("Ready for command.")
        sys.exit(0)
    
    response = query_ai(prompt)
    print(response)
    speak(response[:400])
