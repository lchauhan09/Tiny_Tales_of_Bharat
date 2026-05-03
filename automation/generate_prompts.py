import os
import re

# Paths
PROMPTS_FILE = "scripts/pending/0001_Sanjivani_Mountain_P1_image_prompts.txt"
OUTPUT_DIR = "scripts/pending/images"

def parse_prompts(file_path):
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return []

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Regex to find [SHOT X] and the following prompt
    # Matches [SHOT 1 — INTRO] \n Prompt: \n "..."
    pattern = r"\[SHOT (\d+) — .*?\]\s*Prompt:\s*\"(.*?)\""
    matches = re.findall(pattern, content, re.DOTALL)
    
    return matches

def generate_prompts():
    print(f"Parsing prompts from {PROMPTS_FILE}...")
    prompts = parse_prompts(PROMPTS_FILE)
    
    if not prompts:
        print("No prompts found!")
        return

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # In a real scenario, this is where you'd call an Image Generation API
    # For now, we'll save them to a summary file or just print them
    for shot_num, prompt_text in prompts:
        print(f"Shot {shot_num}: {prompt_text[:50]}...")
        # Mocking the creation of an image filename
        # filename = f"shot{shot_num}.png"
        # with open(os.path.join(OUTPUT_DIR, filename), "w") as f: f.write("Mock Image Data")

    print(f"\nFound {len(prompts)} image prompts. Ready for generation.")

if __name__ == "__main__":
    generate_prompts()
