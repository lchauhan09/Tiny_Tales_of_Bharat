import os
import subprocess
import json
import logging
import sys
from datetime import datetime
from tqdm import tqdm

# Setup tools directory
tools_dir = os.path.join(os.getcwd(), "tools")
if os.path.exists(tools_dir):
    if tools_dir not in os.environ["PATH"]:
        os.environ["PATH"] += os.path.pathsep + tools_dir

# Paths
BASE_DIR = "scripts/pending"
EP_PREFIX = "0001_Sanjivani_Mountain_P1"
OUTPUT_DIR = "videos/rough_cuts"
LOG_DIR = "automation/logs"
UTILS_DIR = "automation/utils"

# Ensure directories exist
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(UTILS_DIR, exist_ok=True)

# Setup Logging
logging.basicConfig(
    filename=os.path.join(LOG_DIR, 'assemble.log'),
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Assets
INTRO_VIDEO = os.path.join(UTILS_DIR, "intro.mp4")
OUTRO_VIDEO = os.path.join(UTILS_DIR, "outro.mp4")
BACKGROUND_MUSIC = os.path.join(UTILS_DIR, "bg_music.mp3")
FALLBACK_IMAGE = os.path.join(UTILS_DIR, "fallback.png")
SILENT_AUDIO = os.path.join(UTILS_DIR, "silent.mp3")

def fix_path(path):
    return os.path.abspath(path).replace("\\", "/")

def run(cmd):
    logging.info(f"Running command: {' '.join(cmd)}")
    try:
        return subprocess.run(cmd, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        logging.error(f"Command failed with code {e.returncode}")
        logging.error(f"Stderr: {e.stderr}")
        raise

def generate_fallback_assets():
    if not os.path.exists(FALLBACK_IMAGE):
        run(["ffmpeg", "-y", "-f", "lavfi", "-i", "color=c=blue:s=1280x720:d=1", "-vframes", "1", fix_path(FALLBACK_IMAGE)])
    if not os.path.exists(SILENT_AUDIO):
        run(["ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo", "-t", "1", fix_path(SILENT_AUDIO)])
    if not os.path.exists(INTRO_VIDEO):
        run(["ffmpeg", "-y", "-f", "lavfi", "-i", "color=c=black:s=1280x720:d=1", "-pix_fmt", "yuv420p", fix_path(INTRO_VIDEO)])
    if not os.path.exists(OUTRO_VIDEO):
        run(["ffmpeg", "-y", "-f", "lavfi", "-i", "color=c=black:s=1280x720:d=1", "-pix_fmt", "yuv420p", fix_path(OUTRO_VIDEO)])

def get_audio_duration(file_path):
    if not os.path.exists(file_path): return 3.0
    cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", fix_path(file_path)]
    try:
        result = run(cmd)
        return float(result.stdout.strip())
    except Exception: return 3.0

def create_image_video():
    input_txt = os.path.join(OUTPUT_DIR, "images.txt")
    SHOT_MAPPING = [
        ("shot1_intro.png", "intro_narrator.mp3"), ("shot2_lakshmana.png", "scene1_narrator.mp3"),
        ("shot3_hanuman_forward.png", "rama_line.mp3"), ("shot4_hanuman_leap.png", "hanuman_line1.mp3"),
        ("shot5_flying.png", "scene2_narrator.mp3"), ("shot6_mountain.png", 3.0),
        ("shot7_thinking.png", "hanuman_line2.mp3"), ("shot8_lift.png", 4.0),
        ("shot9_moral.png", "outro_narrator1.mp3"),
    ]
    with open(input_txt, "w", encoding="utf-8") as f:
        for img_name, audio_ref in tqdm(SHOT_MAPPING, desc="Processing shots"):
            img_path = os.path.join(BASE_DIR, "images", img_name)
            if not os.path.exists(img_path): img_path = FALLBACK_IMAGE
            duration = get_audio_duration(os.path.join(BASE_DIR, "audio", audio_ref)) if isinstance(audio_ref, str) else audio_ref
            f.write(f"file '{fix_path(img_path)}'\n")
            f.write(f"duration {duration}\n")
        # Concat demuxer last file repeat
        f.write(f"file '{fix_path(os.path.join(BASE_DIR, 'images', SHOT_MAPPING[-1][0]) if os.path.exists(os.path.join(BASE_DIR, 'images', SHOT_MAPPING[-1][0])) else FALLBACK_IMAGE)}'\n")

    output = fix_path(os.path.join(OUTPUT_DIR, "images_video.mp4"))
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", fix_path(input_txt), "-vsync", "vfr", "-pix_fmt", "yuv420p", "-vf", "scale=1280:720,format=yuv420p", output])
    return output

def create_audio_track():
    output = fix_path(os.path.join(OUTPUT_DIR, "audio_track.mp3"))
    run(["ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo", "-t", "5", output])
    return output

def assemble_episode():
    generate_fallback_assets()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    final_output = fix_path(os.path.join(OUTPUT_DIR, f"{EP_PREFIX}_roughcut_{timestamp}.mp4"))
    v = create_image_video()
    a = create_audio_track()
    # Simple direct merge
    run(["ffmpeg", "-y", "-i", v, "-i", a, "-c:v", "copy", "-c:a", "aac", "-map", "0:v:0", "-map", "1:a:0", "-shortest", final_output])
    print(f"\n✅ Success! Rough cut created: {final_output}")

if __name__ == "__main__":
    assemble_episode()
