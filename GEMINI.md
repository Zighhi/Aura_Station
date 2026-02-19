# Aura Station: Generative Audio Pipeline

This project is an automated, generative pipeline for creating long-form audio soundscapes for the **Aura Station** YouTube channel. It is designed to produce high-quality, themed audio (Water, Fire, Earth) for focus, relaxation, and study.

## Project Overview

The pipeline leverages modern Machine Learning models to transform high-level themes into rich, descriptive prompts, which are then synthesized into immersive audio soundscapes.

### Main Technologies
- **Python:** The core programming language.
- **PyTorch:** Used for running the underlying machine learning models.
- **Transformers (Hugging Face):** Provides the `pipeline` API for text-generation and text-to-audio synthesis.
- **Models:**
    - **Prompt Generation:** `gpt2-medium` (expands themes into evocative descriptions).
    - **Audio Synthesis:** `facebook/musicgen-tiny` (default in main pipeline) or `facebook/musicgen-small` (for higher quality).
- **SciPy:** Used for saving the generated audio data as standard `.wav` files.

## Project Structure

- `.cache/`: Local cache for downloaded Hugging Face models (set via `HF_HOME`). **Ignored by Git.**
- `audio_samples/`: Output directory for generated audio.
    - `raw/`: Initial base samples.
    - `processed/`: Future directory for post-processed audio.
- `docs/`: Project documentation and research.
- `notebooks/`: Jupyter Notebooks for experimentation.
- `scripts/`: Runnable Python scripts for the pipeline.
    - `generate_soundscape.py`: The main end-to-end generation script.
    - `ml_audio_test.py`: A utility for testing the audio synthesis model.
- `src/`: Core Python modules.
    - `prompt_engineering.py`: Logic for theme-specific prompt agents (Fire, Water, Earth).
- `.venv/`: Python virtual environment. **Ignored by Git.**

## Building and Running

### Prerequisites
- Python 3.10+
- A virtual environment is recommended.
- **Note:** Installation currently requires ~10 GB of free space on the `E:` drive due to large model weights and GPU-enabled PyTorch.

### Installation
1. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   .\\.venv\\Scripts\\activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Pipeline
To generate a soundscape for a specific theme, run the following command from the project root:
```bash
.\\.venv\\Scripts\\python.exe scripts/generate_soundscape.py [Theme]
```
*Available themes:* `Water`, `Fire`, `Earth`.

### Testing
- To test the prompt agents independently: `python src/prompt_engineering.py`
- To test the audio model: `python scripts/ml_audio_test.py`

## Development Conventions

### Prompt Engineering
- The project uses `PromptAgent` classes in `src/prompt_engineering.py` to structure keywords and moods.
- `scripts/generate_soundscape.py` uses a "meta-prompt" approach with `gpt2-medium` for creative expansion.

### Cache Management
- The `HF_HOME` environment variable is explicitly set to `.cache/huggingface` in the scripts to keep models local to the project directory.

### Output Formatting
- Generated audio is saved as 16-bit PCM WAV files in `audio_samples/raw/{theme}/`.
- Filenames follow the pattern: `base_sample_{theme}_{timestamp}.wav`.

## Current Status & Blockers
- **Space Constraint:** The `E:` drive is nearly full, preventing the installation of the GPU-enabled PyTorch (~2.5 GB).
- **GPU Acceleration:** Currently limited by disk space; once resolved, the pipeline should be configured to use `device=0` (GPU) for significantly faster generation.
- **Quality Upgrades:** Future plans include switching the default model to `musicgen-small` or `musicgen-medium` once resources permit.
