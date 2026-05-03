import os
import re
import json
import base64
import shutil
import requests
from dotenv import load_dotenv

load_dotenv()

# ============================================
# CONFIG
# ============================================

PROMPT_FILE = "scripts/pending/0001_Sanjivani_Mountain_P1_image_prompts.txt"
OUTPUT_DIR = "scripts/pending/images"
FALLBACK_IMAGE = "automation/utils/fallback.png"

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
STABILITY_API_KEY = os.getenv("STABILITY_API_KEY")
MIDJOURNEY_API_KEY = os.getenv("MIDJOURNEY_API_KEY")

# Character keywords for auto-detection
CHARACTER_KEYWORDS = [
    "hanuman", "rama", "lakshmana", "sita",
    "monkey god", "vanara", "prince", "warrior"
]

# ============================================
# ENGINE HELPERS
# ============================================

def is_character_shot(prompt: str) -> bool:
    """Detect if prompt contains recurring characters."""
    p = prompt.lower()
    return any(k in p for k in CHARACTER_KEYWORDS)

# ============================================
# ENGINE: OpenAI (DALL-E 3)
# ============================================

def try_openai(prompt):
    if not OPENAI_API_KEY:
        return None, "Missing OPENAI_API_KEY"

    try:
        url = "https://api.openai.com/v1/images/generations"
        headers = {"Authorization": f"Bearer {OPENAI_API_KEY}"}
        data = {
            "model": "dall-e-3",
            "prompt": prompt,
            "n": 1,
            "size": "1024x1024",
            "response_format": "b64_json"
        }

        resp = requests.post(url, headers=headers, json=data)
        if resp.status_code != 200:
            return None, resp.text

        img_b64 = resp.json()["data"][0]["b64_json"]
        img_bytes = base64.b64decode(img_b64)
        return img_bytes, None

    except Exception as e:
        return None, str(e)

# ============================================
# ENGINE: Stability SD3
# ============================================

def try_stability(prompt):
    if not STABILITY_API_KEY:
        return None, "Missing STABILITY_API_KEY"

    try:
        url = "https://api.stability.ai/v2beta/stable-image/generate/sd3"
        headers = {
            "Authorization": f"Bearer {STABILITY_API_KEY}",
            "Accept": "image/*"
        }
        files = {
            "prompt": (None, prompt),
            "output_format": (None, "png")
        }

        resp = requests.post(url, headers=headers, files=files)
        if resp.status_code != 200:
            return None, resp.text

        return resp.content, None

    except Exception as e:
        return None, str(e)

# ============================================
# ENGINE: Midjourney (placeholder)
# ============================================

def try_midjourney(prompt):
    if not MIDJOURNEY_API_KEY:
        return None, "Missing MIDJOURNEY_API_KEY"
    return None, "Midjourney API not implemented yet"

# ============================================
# FALLBACK
# ============================================

def save_fallback(filename):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    out_path = os.path.join(OUTPUT_DIR, filename)
    if os.path.exists(FALLBACK_IMAGE):
        shutil.copy(FALLBACK_IMAGE, out_path)
        print(f"🟦 Fallback used for {filename}")
    else:
        print(f"⚠️ Fallback image missing: {FALLBACK_IMAGE}")

# ============================================
# PROMPT PARSER
# ============================================

def parse_prompts():
    prompts = []
    if not os.path.exists(PROMPT_FILE):
        return prompts

    with open(PROMPT_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()

    current = None
    for i, line in enumerate(lines):
        line = line.strip()
        if line.startswith("[SHOT"):
            if current:
                prompts.append(current)
            try:
                shot_num = int(line.split()[1])
                current = {"shot": shot_num, "prompt": ""}
            except:
                continue
        elif line.startswith("Prompt:"):
            if current:
                content = line.replace("Prompt:", "").strip().strip('"')
                if not content and i + 1 < len(lines):
                    content = lines[i+1].strip().strip('"')
                current["prompt"] = content

    if current:
        prompts.append(current)

    return prompts

# ============================================
# MAIN GENERATION LOGIC
# ============================================

def main():
    prompts = parse_prompts()
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    for item in prompts:
        shot = item["shot"]
        prompt = item["prompt"]
        filename = f"shot{shot}.png"

        print(f"\n=== SHOT {shot} ===")
        print(f"Prompt snippet: {prompt[:80]}...")

        # Decide engine order based on character detection
        if is_character_shot(prompt):
            print("👤 Character detected! Prioritizing OpenAI for consistency.")
            engine_order = ["openai", "midjourney", "stability"]
        else:
            print("🏞️ Environment shot. Prioritizing Stability for efficiency.")
            engine_order = ["stability", "openai", "midjourney"]

        print("Engine priority order:", " -> ".join(engine_order))

        # Try engines in order
        success = False
        for engine in engine_order:
            print(f"→ Trying {engine}...")

            if engine == "openai":
                img_bytes, err = try_openai(prompt)
            elif engine == "midjourney":
                img_bytes, err = try_midjourney(prompt)
            elif engine == "stability":
                img_bytes, err = try_stability(prompt)
            else:
                img_bytes, err = None, "Unknown engine"

            if img_bytes:
                out_path = os.path.join(OUTPUT_DIR, filename)
                with open(out_path, "wb") as f:
                    f.write(img_bytes)
                print(f"✅ {engine.upper()} succeeded for {filename}")
                success = True
                break
            else:
                # Log error snippet
                err_msg = str(err)[:100].replace('\n', ' ')
                print(f"❌ {engine.upper()} failed: {err_msg}")

        if not success:
            print("→ All engines failed. Falling back to local placeholder.")
            save_fallback(filename)

    print("\n🎉 Image generation complete.\n")

if __name__ == "__main__":
    main()
