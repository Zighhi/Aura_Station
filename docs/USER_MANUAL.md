# Aura Station: User Manual

Welcome to the Aura Station Generative Audio System. This guide will help you create high-quality, study-optimized soundscapes using the V6 Engine.

## Quick Start

### 1. Setup
Ensure you have installed the requirements:
```bash
pip install -r requirements.txt
```
(Note: You need ~10GB of disk space and a CUDA-capable GPU for best performance).

### 2. Add Impulse Responses (Optional but Recommended)
To get professional-grade reverb, place your Impulse Response `.wav` files (e.g., from a hall, cave, or forest) into:
`assets/impulses/`
*The system will automatically find and use them.*

### 3. Workflow

The process has two steps: **Generate Ingredients** -> **Cook the Meal**.

#### Step A: Generate Raw Assets (Ingredients)
First, you need raw samples. Run these commands to create them.

**Generate Atmospheric Drones (The Bed):**
```bash
python scripts/generate_soundscape.py Water --type atmospheric --count 5
```
*(Replace `Water` with `Fire` or `Earth`. 5 is a good batch size).*

**Generate Percussive Loops (The Pulse):**
```bash
python scripts/generate_soundscape.py Water --type percussive --count 5
```

#### Step B: Compose Soundscapes (The Meal)
Now, turn those assets into full 10-minute tracks.

```bash
python scripts/compose_soundscape.py Water --duration 10 --count 1
```

**What this does:**
1.  Picks 3 random Drones + 1 random Pulse Loop.
2.  Checks if this combination is unique (never repeats!).
3.  Applies the V6 Engine (Tri-Band Layering, Swirling Filters, Dual Convolution).
4.  Saves the result to `audio_samples/processed/water/{unique_id}/`.

### 4. Output
Your final files will be in `audio_samples/processed/{theme}/`.
Each folder contains:
*   `soundscape.wav`: The final master.
*   `soundscape.json`: The "Manifest" (Recipe) used to create it.

---

## Pro Tips

*   **Batch Processing:** You can generate 10 tracks in a row while you sleep:
    ```bash
    python scripts/compose_soundscape.py Fire --duration 60 --count 10
    ```
*   **Checking History:** The system remembers what it has made in `audio_samples/processed/history.json`. It will warn you if it runs out of unique combinations (generate more raw assets if this happens!).
