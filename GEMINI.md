# Aura Station: Generative Audio Pipeline

This project is an automated, generative pipeline for creating long-form audio soundscapes for the **Aura Station** YouTube channel. It is designed to produce high-quality, themed audio (Water, Fire, Earth) for focus, relaxation, and study.

## Project Overview

The pipeline leverages modern Machine Learning models to transform high-level themes into rich, descriptive prompts, which are then synthesized into immersive audio soundscapes.

### Main Technologies
- **Python:** The core programming language.
- **PyTorch:** Used for running the underlying machine learning models with GPU acceleration.
- **Transformers (Hugging Face):** Provides the `pipeline` API for text-generation and text-to-audio synthesis.
- **Models:**
    - **Hybrid Prompt Generation:** Combines `src/prompt_engineering.py` (structured agents) with `gpt2-medium` (creative expansion).
    - **Audio Synthesis:** `facebook/musicgen-small` (optimized for speed/quality balance).
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
To generate soundscape(s) for specific themes, run the following command from the project root:
```bash
.\\.venv\\Scripts\\python.exe scripts/generate_soundscape.py [Theme1] [Theme2]... [--count N]
```
*Available themes:* `Water`, `Fire`, `Earth`, `All`.

*Example (5 samples per theme):*
```bash
.\\.venv\\Scripts\\python.exe scripts/generate_soundscape.py All --count 5
```

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

## Documentation
- **[Technical Deep Dive](docs/TECHNICAL_Deep_Dive.md):** A comprehensive architectural overview of the V6 Engine, detailing the signal flow, DSP algorithms, and granular pulse logic.

## Current Status & Progress (V6 "Organic" Engine)

The project has reached a stable, production-ready state with the release of the **V6 Dynamic Engine**.

- **Generative DSP:**
    - **Tri-Band Layering:** Automatically separates Low (Drone), Mid (Body), and High (Texture) frequencies for a clean mix.
    - **Organic Pulse:** Uses granular shuffling and probabilistic density to turn short loops into evolving, non-repetitive rhythmic textures.
    - **Dual Convolution:** Combines per-layer depth with a global master-bus "room" for hyper-realistic spatialization.
- **Workflow:**
    - **Manifests:** Full JSON logging for every generated track.
    - **History Tracking:** Prevents duplicate sample combinations.
    - **Asset Management:** Automated folder structures for Themes and Loops.

## Next Steps
- **Production Run:** Continue generating high-volume batches for the channel.
- **Quality QA:** Listen to V6 outputs and fine-tune the "Granular Shuffle" probability if rhythms feel too chaotic.
