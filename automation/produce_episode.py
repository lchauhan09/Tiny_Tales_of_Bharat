import subprocess

STEPS = [
    "python automation/generate_script.py",
    # Placeholder for future: "python automation/generate_storyboard.py",
    "python automation/generate_prompts.py",
    "python automation/generate_images.py",
    # Placeholder for future: "python automation/generate_tts.py",
    "python automation/generate_subtitles.py",
    "python automation/assemble_video.py",
    # Placeholder for future: "python automation/update_database.py",
]

def run(cmd):
    print(f"\n=== RUNNING: {cmd} ===\n")
    subprocess.run(cmd, shell=True, check=True)

def main():
    print("STARTING: Full episode production pipeline...")
    for step in STEPS:
        try:
            run(step)
        except subprocess.CalledProcessError as e:
            print(f"\nERROR: Pipeline stopped due to error in step: {step}")
            break
            
    print("\nCOMPLETED: Episode production complete.\n")

if __name__ == "__main__":
    main()
