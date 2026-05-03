import os
import subprocess
from datetime import datetime
from tqdm import tqdm
import logging

# --- CONFIG ---
BASE_DIR = "scripts/pending"
EP_PREFIX = "0001_Sanjivani_Mountain_P1"
OUTPUT_DIR = "videos/rough_cuts"

INTRO_VIDEO = "automation/utils/intro.mp4"
OUTRO_VIDEO = "automation/utils/outro.mp4"
BACKGROUND_MUSIC = "automation/utils/bg_music.mp3"
SUBTITLES_FILE = os.path.join(BASE_DIR, "subtitles.srt")
FALLBACK_IMAGE = "automation/utils/fallback.png"
FALLBACK_AUDIO = "automation/utils/silent.mp3"

SHOT_MAPPING = [
    ("shot1_intro.png", "intro_narrator.mp3"),
    ("shot2_lakshmana.png", "scene1_narrator.mp3"),
    ("shot3_hanuman_forward.png", "rama_line.mp3"),
    ("shot4_hanuman_leap.png", "hanuman_line1.mp3"),
    ("shot5_flying.png", "scene2_narrator.mp3"),
    ("shot6_mountain.png", 3.0),
    ("shot7_thinking.png", "hanuman_line2.mp3"),
    ("shot8_lift.png", 4.0),
    ("shot9_moral.png", "outro_narrator1.mp3"),
]

# Ensure tools directory is in PATH for this process
tools_dir = os.path.join(os.getcwd(), "tools")
if os.path.exists(tools_dir):
    if tools_dir not in os.environ["PATH"]:
        os.environ["PATH"] += os.path.pathsep + tools_dir

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs("automation/logs", exist_ok=True)
logging.basicConfig(
    filename="automation/logs/assemble.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

def run(cmd):
    logging.info("RUN: " + " ".join(cmd))
    return subprocess.run(cmd, check=True, capture_output=True, text=True)

def ensure_fallbacks():
    if not os.path.exists(FALLBACK_IMAGE):
        run([
            "ffmpeg", "-y",
            "-f", "lavfi", "-i", "color=c=blue:s=1280x720:d=1",
            FALLBACK_IMAGE
        ])
    if not os.path.exists(FALLBACK_AUDIO):
        run([
            "ffmpeg", "-y",
            "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo",
            "-t", "1", FALLBACK_AUDIO
        ])
    if not os.path.exists(INTRO_VIDEO):
        run([
            "ffmpeg", "-y",
            "-f", "lavfi", "-i", "color=c=black:s=1280x720:d=3",
            INTRO_VIDEO
        ])
    if not os.path.exists(OUTRO_VIDEO):
        run([
            "ffmpeg", "-y",
            "-f", "lavfi", "-i", "color=c=black:s=1280x720:d=3",
            OUTRO_VIDEO
        ])

def get_audio_duration(path):
    if not os.path.exists(path):
        logging.warning(f"Missing audio: {path}, using 3.0s")
        return 3.0
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        path,
    ]
    try:
        res = run(cmd)
        return float(res.stdout.strip())
    except Exception as e:
        logging.error(f"ffprobe failed for {path}: {e}")
        return 3.0

def create_image_video():
    images_txt = os.path.join(OUTPUT_DIR, "images.txt")
    total_duration = 0.0
    
    with open(images_txt, "w", encoding="utf-8") as f:
        for img_name, audio_ref in tqdm(SHOT_MAPPING, desc="Shots"):
            img_path = os.path.join(BASE_DIR, "images", img_name)
            if not os.path.exists(img_path):
                img_path = FALLBACK_IMAGE
            
            if isinstance(audio_ref, str):
                audio_path = os.path.join(BASE_DIR, "audio", audio_ref)
                duration = get_audio_duration(audio_path)
            else:
                duration = audio_ref
            
            total_duration += duration
            abs_img = os.path.abspath(img_path).replace("\\", "/")
            f.write(f"file '{abs_img}'\n")
            f.write(f"duration {duration}\n")
            
        # repeat last frame
        last_img = os.path.join(BASE_DIR, "images", SHOT_MAPPING[-1][0])
        if not os.path.exists(last_img):
            last_img = FALLBACK_IMAGE
        abs_last = os.path.abspath(last_img).replace("\\", "/")
        f.write(f"file '{abs_last}'\n")

    raw_video = os.path.join(OUTPUT_DIR, "images_raw.mp4")
    final_video = os.path.join(OUTPUT_DIR, "images_video.mp4")

    run([
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0",
        "-i", images_txt,
        "-vsync", "vfr",
        "-pix_fmt", "yuv420p",
        raw_video,
    ])

    # apply scale + gentle fade in/out (removed zoompan for stability)
    run([
        "ffmpeg", "-y",
        "-i", raw_video,
        "-vf",
        f"scale=1280:720,fade=t=in:st=0:d=0.5,fade=t=out:st={total_duration-0.5}:d=0.5",
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        final_video,
    ])

    return final_video

def create_audio_mix():
    audio_txt = os.path.join(OUTPUT_DIR, "audio.txt")
    audio_files = [ref for _, ref in SHOT_MAPPING if isinstance(ref, str)]
    audio_files.append("outro_narrator2.mp3")

    with open(audio_txt, "w", encoding="utf-8") as f:
        for name in audio_files:
            path = os.path.join(BASE_DIR, "audio", name)
            if not os.path.exists(path):
                path = FALLBACK_AUDIO
            abs_path = os.path.abspath(path).replace("\\", "/")
            f.write(f"file '{abs_path}'\n")

    narration = os.path.join(OUTPUT_DIR, "narration.wav")
    run([
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0",
        "-i", audio_txt,
        "-acodec", "pcm_s16le",
        narration,
    ])

    if os.path.exists(BACKGROUND_MUSIC):
        mixed = os.path.join(OUTPUT_DIR, "audio_mix.wav")
        run([
            "ffmpeg", "-y",
            "-i", narration,
            "-i", BACKGROUND_MUSIC,
            "-filter_complex",
            "[0:a]volume=1.0[a1];[1:a]volume=0.15[a2];"
            "[a1][a2]amix=inputs=2:duration=first[aout]",
            "-map", "[aout]",
            "-ac", "2",
            mixed,
        ])
        return mixed
    else:
        return narration

def assemble_episode():
    ensure_fallbacks()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    final_output = os.path.join(OUTPUT_DIR, f"{EP_PREFIX}_roughcut_{timestamp}.mp4")

    print("--- STEP 1: Creating image video ---")
    img_video = create_image_video()

    print("--- STEP 2: Creating audio mix ---")
    audio_mix = create_audio_mix()

    print("--- STEP 3: Merging intro + main + outro + waveform + subtitles ---")

    sub_path = SUBTITLES_FILE.replace("\\", "/")
    
    cmd = [
        "ffmpeg", "-y",
        "-i", INTRO_VIDEO,      # 0
        "-i", img_video,        # 1
        "-i", OUTRO_VIDEO,      # 2
        "-i", audio_mix,        # 3
        "-filter_complex",
        # concat videos
        "[0:v][1:v][2:v]concat=n=3:v=1:a=0[vcat];"
        # subtitles (if present)
        f"[vcat]subtitles='{sub_path}':[vsub];"
        # waveform from audio
        "[3:a]showwaves=s=1280x200:mode=line:colors=white[wave];"
        # stack video + waveform
        "[vsub][wave]vstack=inputs=2[vout]",
        "-map", "[vout]",
        "-map", "3:a",
        "-c:v", "libx264",
        "-c:a", "aac",
        "-shortest",
        final_output,
    ]

    if not os.path.exists(SUBTITLES_FILE):
        cmd[8] = (
            "[0:v][1:v][2:v]concat=n=3:v=1:a=0[vcat];"
            "[3:a]showwaves=s=1280x200:mode=line:colors=white[wave];"
            "[vcat][wave]vstack=inputs=2[vout]"
        )

    run(cmd)
    print(f"\nSUCCESS: Rough cut created: {final_output}")

if __name__ == "__main__":
    assemble_episode()
