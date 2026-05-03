import os
import requests
from dotenv import load_dotenv

load_dotenv()

PROMPT_FILE = "scripts/pending/0001_Sanjivani_Mountain_P1_image_prompts.txt"
OUTPUT_DIR = "scripts/pending/images"
API_KEY = os.getenv("STABILITY_API_KEY")  # or your FLUX/SDXL key

API_URL = "https://api.stability.ai/v2beta/stable-image/generate/sd3"

def generate_image(prompt, filename):
    if not API_KEY:
        print(f"Skipping API call for {filename} (STABILITY_API_KEY not set).")
        return
    
    if not prompt or len(prompt.strip()) < 1:
        print(f"Skipping {filename} - Empty prompt.")
        return
        
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Accept": "image/*"
    }
    files = {"prompt": (None, prompt), "output_format": (None, "png")}
    
    print(f"Generating image for prompt: {prompt[:50]}...")
    resp = requests.post(API_URL, headers=headers, files=files)
    
    if resp.status_code == 200:
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        out_path = os.path.join(OUTPUT_DIR, filename)
        with open(out_path, "wb") as f:
            f.write(resp.content)
        print("Generated:", out_path)
    else:
        print("Error:", resp.status_code, resp.text)

def parse_prompts():
    prompts = []
    if not os.path.exists(PROMPT_FILE):
        print(f"Prompt file not found: {PROMPT_FILE}")
        return prompts
        
    with open(PROMPT_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()
        for i, line in enumerate(lines):
            line = line.strip()
            if line.startswith("Prompt:"):
                # Check if prompt is on the same line
                content = line.replace("Prompt:", "").strip().strip('"')
                if not content and i + 1 < len(lines):
                    # Check the next line
                    content = lines[i+1].strip().strip('"')
                
                if content:
                    prompts.append(content)
    return prompts

def main():
    prompts = parse_prompts()
    if not prompts:
        print("No prompts found.")
        return
        
    print(f"Found {len(prompts)} prompts. Starting generation...")
    for i, prompt in enumerate(prompts, start=1):
        generate_image(prompt, f"shot{i}.png")

if __name__ == "__main__":
    main()
