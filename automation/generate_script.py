import json
import os
from datetime import datetime

# Paths
CONTENT_BIBLE_PATH = "content/content_bible.json"
EPISODE_DB_PATH = "content/episode_database.json"
PENDING_SCRIPTS_DIR = "scripts/pending"

def load_json(path):
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def generate_script():
    bible = load_json(CONTENT_BIBLE_PATH)
    db = load_json(EPISODE_DB_PATH)

    # 1. Determine which incident to work on
    # Find incidents already in DB
    existing_incidents = {}
    for entry in db:
        canonical = entry["incident_canonical"]
        existing_incidents[canonical] = max(existing_incidents.get(canonical, 0), entry["part_number"])

    target_incident = None
    next_part = 1

    # Check if there's an ongoing incident that needs more parts (simplified logic: check if any incident in DB is NOT 'published')
    # For now, we'll just pick the first one from bible that isn't in DB, or increment if we had a "needs_more_parts" flag.
    # Since we don't have a "needs_more_parts" flag yet, let's assume each incident has 1 part unless we find a reason to add more.
    # To demonstrate the part logic, let's say if we find it in DB, we could increment, but we need a way to know when it's DONE.
    
    for item in bible:
        canonical = item["incident_canonical"]
        if canonical not in existing_incidents:
            target_incident = item
            next_part = 1
            break
        else:
            # For demonstration, let's say we only do 1 part per incident for now 
            # unless the user manually adds a "draft" or we change logic.
            # But the user wants "canonical incident + part_number logic so multi-part episodes never conflict".
            # Let's check if the last part of this incident is 'published'. If it is, we move to next incident.
            # If we wanted to force a part 2, we'd need a trigger.
            continue

    if not target_incident:
        print("No new incidents found in Content Bible!")
        return

    # 2. Generate Episode ID
    ep_id = f"{len(db) + 1:04d}"
    
    # 3. Create Script Content
    script_content = f"""# Episode {ep_id}: {target_incident['incident_canonical']} (Part {next_part})
# Character: {target_incident['character']}
# Visual Theme: {target_incident['visual_theme']}
# Moral: {target_incident['moral']}

[INTRO - 30s]
Narrator: Welcome back to Tiny Tales of Bharat! Today, we follow the brave {target_incident['character']}...

[SCENE 1 - 2m]
(Visual: {target_incident['visual_theme']})
Narrator: In the heart of the story, {target_incident['character']} faces the challenge of {target_incident['incident_canonical']}...

[CLIMAX - 2m]
Narrator: With great courage, the goal is achieved!

[OUTRO - 1m]
Narrator: And that is how we learn that {target_incident['moral']}. 
Narrator: See you in the next tale!
"""

    # 4. Save Script File
    filename = f"{ep_id}_{target_incident['incident_canonical'].replace(' ', '_')}_P{next_part}.txt"
    file_path = os.path.join(PENDING_SCRIPTS_DIR, filename)
    
    os.makedirs(PENDING_SCRIPTS_DIR, exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(script_content)

    # 5. Update Episode Database
    new_entry = {
        "episode_id": ep_id,
        "character": target_incident["character"],
        "incident_canonical": target_incident["incident_canonical"],
        "part_number": next_part,
        "visual_theme": target_incident["visual_theme"],
        "status": "pending",
        "date_generated": datetime.now().strftime("%Y-%m-%d")
    }
    db.append(new_entry)
    save_json(EPISODE_DB_PATH, db)

    print(f"Generated script: {file_path}")

if __name__ == "__main__":
    generate_script()
