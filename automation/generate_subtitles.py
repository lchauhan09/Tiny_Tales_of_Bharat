import os
import subprocess
from datetime import timedelta

BASE_DIR = "scripts/pending"
OUTPUT_SRT = os.path.join(BASE_DIR, "subtitles.srt")

# Ensure tools directory is in PATH for this process
tools_dir = os.path.join(os.getcwd(), "tools")
if os.path.exists(tools_dir):
    if tools_dir not in os.environ["PATH"]:
        os.environ["PATH"] += os.path.pathsep + tools_dir

AUDIO_SEQUENCE = [
    ("intro_narrator.mp3", "Welcome to Tiny Tales of Bharat! Today, we follow the mighty Hanuman on a brave mission to save his dear friend, Lakshmana."),
    ("scene1_narrator.mp3", "In the middle of the great battle, Lakshmana has fallen unconscious. Only one magical herb can save him — the Sanjivani, found on a distant mountain."),
    ("rama_line.mp3", "Hanuman… you are our hope."),
    ("hanuman_line1.mp3", "I will bring the Sanjivani, my Lord!"),
    ("scene2_narrator.mp3", "After a long journey, Hanuman reaches the mountain. But there’s a problem — many herbs glow in the moonlight, and he cannot tell which one is the real Sanjivani."),
    ("hanuman_line2.mp3", "If I cannot find the herb… I will take the whole mountain!"),
    ("outro_narrator1.mp3", "And that is how Hanuman teaches us that devotion gives us strength, and creative thinking helps us solve even the biggest problems."),
    ("outro_narrator2.mp3", "See you in the next tale — where the journey continues!"),
]

def run(cmd):
    return subprocess.run(cmd, check=True, capture_output=True, text=True)

def get_duration(path):
    if not os.path.exists(path):
        return 3.0
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        path,
    ]
    res = run(cmd)
    return float(res.stdout.strip())

def fmt(t):
    ms = int(t * 1000)
    td = timedelta(milliseconds=ms)
    s = str(td)
    if "." not in s:
        s += ".000"
    h, m, rest = s.split(":")
    sec, ms = rest.split(".")
    return f"{h.zfill(2)}:{m.zfill(2)}:{sec.zfill(2)},{ms[:3].ljust(3,'0')}"

def main():
    os.makedirs(os.path.dirname(OUTPUT_SRT), exist_ok=True)
    current = 0.0
    idx = 1
    with open(OUTPUT_SRT, "w", encoding="utf-8") as f:
        for filename, text in AUDIO_SEQUENCE:
            path = os.path.join(BASE_DIR, "audio", filename)
            dur = get_duration(path)
            start = current
            end = current + dur
            f.write(f"{idx}\n")
            f.write(f"{fmt(start)} --> {fmt(end)}\n")
            f.write(text + "\n\n")
            current = end
            idx += 1
    print(f"Subtitles generated: {OUTPUT_SRT}")

if __name__ == "__main__":
    main()
