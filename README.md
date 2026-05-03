# Tiny Tales of Bharat 🕉️

A semi-automated YouTube channel creating 6-minute, kid-friendly mythological videos from the Ramayana, Mahabharata, and Upanishads.

## 📁 Folder Structure

- **`content/`**: The "brain" of the channel.
  - `content_bible.json`: Character traits, canonical incidents, and morals.
  - `episode_database.json`: Tracks every episode, part number, and status.
  - `visuals/`: Character sheets and style references for consistent AI generation.
- **`scripts/`**:
  - `pending/`: Newly generated AI scripts awaiting review.
  - `approved/`: Scripts ready for production.
- **`automation/`**: Python scripts for generating content, storyboards, TTS, and video assembly.
- **`videos/`**:
  - `rough_cuts/`: Auto-generated drafts.
  - `final/`: Polished videos ready for upload.
- **`.github/workflows/`**: Automation pipeline (e.g., daily script generation).

## 🚀 Getting Started

1. **Script Generation**: Scripts are auto-generated daily via GitHub Actions.
2. **Review**: Check `scripts/pending/`, refine them, and move to `scripts/approved/`.
3. **Production**: Use the scripts in `automation/` to generate assets and assemble the video.

## 🛠️ Tech Stack
- **Logic**: Python
- **Automation**: GitHub Actions
- **AI**: Script generation, Image generation, TTS (planned)