# Aura Station: Technical Deep Dive (V6 Engine)

This document provides a comprehensive technical overview of the **Aura Station** generative audio pipeline. It details the architecture, signal flow, and algorithmic logic used to create infinite, study-optimized soundscapes.

## 1. Architecture Overview

The system operates on a **Hybrid Generative/DSP Architecture**. It combines Machine Learning (MusicGen) for raw material generation with classic Digital Signal Processing (DSP) for arrangement, spatialization, and mixing.

### Core Components
*   **Generator (`scripts/generate_soundscape.py`):** Uses ML to create raw audio assets (Atmospheric Drones and Percussive Loops).
*   **Composer (`scripts/compose_soundscape.py`):** The orchestrator that selects assets, applies the DSP engine, and renders the final mix.
*   **DSP Engine (`src/audio_engine.py`):** A custom audio processing library built on `pedalboard`, `librosa`, and `numpy`.

---

## 2. Asset Generation Phase

### 2.1. Hybrid Prompting
We do not feed raw text to the MusicGen model. Instead, we use a **two-stage prompting system**:
1.  **Agent Selection:** A theme-specific agent (e.g., `WaterPromptAgent`) selects a structured base prompt from a curated list of keywords (e.g., *"A hypnotic water droplet loop..."*).
2.  **GPT-2 Expansion:** For atmospheric tracks, `gpt2-medium` expands this base prompt into a rich, evocative description to encourage textural complexity.

### 2.2. Audio Synthesis
*   **Model:** `facebook/musicgen-small` (Optimized for GPU).
*   **Modes:**
    *   **Atmospheric:** Generates 33 seconds of audio, then trims to 30s to remove the model's "cadence/resolution," ensuring a seamless loop point.
    *   **Percussive:** Generates 15 seconds of raw rhythmic texture without trimming.

---

## 3. The V7 Dynamic Engine (`src/audio_engine.py`)

This is the heart of the system. It transforms short 30s samples into 10-minute evolving soundscapes using a **Tri-Band Layering System** with analog-style modulation.

### 3.1. Layer 1: The Deep Drone (Foundation)
*   **Source:** Atmospheric Sample A.
*   **Process:**
    *   **PaulStretch:** Time-stretched by ~20x using a windowed overlap-add algorithm.
    *   **Filtering:** Low-Pass Filter (< 800Hz) to occupy the bass and lower-mids. (V7 Update: Raised cutoff for warmth).
    *   **Modulation:** Slow Chorus (0.05Hz) to add stereo width.
    *   **Tremolo:** Amplitude Modulation (AM) at ~0.1Hz to make the drone "breathe."

### 3.2. Layer 2: The Body (Emotion)
*   **Source:** Atmospheric Sample B.
*   **Process:**
    *   **Filtering:** Band-Pass (High-Pass > 80Hz + Low-Pass < 4000Hz).
    *   **V7 Warmth:** High-Pass lowered to 80Hz to preserve the "chest" of the sound.
    *   **Modulation:** Phaser (0.2Hz) + **Wide Delay** (randomized 0.1s - 1.2s) for deep echoes.

### 3.3. Layer 3: The Texture (Air)
*   **Source:** Atmospheric Sample C.
*   **Process:**
    *   **Filtering:** High-Pass (> 600Hz) to isolate "sparkle."
    *   **V7 Tape Wobble:** Uses a **Delay + Chorus** chain to simulate unstable tape echoes (pitch drift).
    *   **Modulation:** Fast Phaser (1.0Hz) for shimmering movement.

### 3.4. Layer 4: The Organic Pulse (Rhythm)
*   **Source:** Percussive Loop Sample.
*   **Logic:**
    *   **Granular Shuffling:** The loop is sliced into 8 grains and randomly reordered every bar.
    *   **Probabilistic Density:** Randomly silences bars (20% chance).
    *   **Modulated Delay:** Uses a dedicated delay line to smooth over the granular cuts.

### 3.5. Layer 5: The Binaural Engine (Focus)
*   **Logic:** Pure DSP Sine Wave Generation.
*   **States:** Randomly selects a brainwave target:
    *   **Delta (1-4Hz):** Deep Sleep.
    *   **Theta (4-8Hz):** Meditation.
    *   **Alpha (8-14Hz):** Relaxed Focus.
    *   **Beta (14-30Hz):** Active Study.
*   **Tremolo:** The binaural beat itself is amplitude-modulated to prevent listener fatigue ("listening fatigue").

---

## 4. Signal Chain & Mixing

### 4.1. Dual-Stage Convolution
To achieve hyper-realistic depth, we use Impulse Responses (IRs) in two stages:
1.  **Per-Layer Depth:** Individual layers may receive a specific IR (e.g., "Cave" for Drone) to place them "behind" the mix.
2.  **Master Bus Glue:** The final summed mix runs through a global "Room" IR (at ~40% mix) to cohesively blend all elements into a single physical space.

### 4.2. Mastering
*   **Compression:** A gentle ratio (2:1) on the master bus to glue dynamics.
*   **Limiting:** A safety ceiling at -1.0dB to prevent clipping.

### 4.3. Manifest System
Every generation produces a `manifest.json` containing:
*   **Source IDs:** The exact filenames of the raw samples used.
*   **Binaural State:** The exact frequency target.
*   **Mix Ratios:** The levels used for that specific render.
*   **Global IR:** The name of the Impulse Response file used.

---

## 5. Usage Guide

### Generate Raw Assets
```bash
# Generate Drones
python scripts/generate_soundscape.py Water --type atmospheric --count 5

# Generate Loops
python scripts/generate_soundscape.py Water --type percussive --count 5
```

### Compose Masterpiece
```bash
python scripts/compose_soundscape.py Water --duration 10 --count 1
```
This command triggers the entire V6 Engine, automatically selecting samples, applying the DSP chain, and saving the output to `audio_samples/processed/water/{id}/`.
