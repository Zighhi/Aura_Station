# Aura Station: Generative Audio Engine

**Aura Station** is an automated, AI-powered generative audio pipeline designed to create infinite, high-fidelity soundscapes for focus, study, and relaxation.

It combines modern Deep Learning (`MusicGen`, `GPT-2`) with advanced Digital Signal Processing (`PaulStretch`, `Pedalboard`, `Binaural Beats`) to transform simple text themes into hour-long, evolving sonic environments.

---

## 🌊 Features (V7 Engine)

*   **Hybrid AI Generation:** Uses `MusicGen-Small` + `GPT-2` to generate unique raw audio assets (Drones & Percussive Loops) based on thematic prompts (Water, Fire, Earth).
*   **Tri-Band Layering:** Automatically separates and mixes Low (Drone), Mid (Body), and High (Texture) frequencies for a professional, non-muddy mix.
*   **Organic Pulse Engine:** Uses granular shuffling and probabilistic density to turn short rhythmic loops into evolving, non-repetitive textures.
*   **Hyper-Realistic Spatialization:** Uses **Dual-Stage Convolution Reverb** (Per-Layer + Master Bus) with real-world Impulse Responses (IRs) to place sounds in physical spaces.
*   **Binaural Entrainment:** Generates scientifically-tuned binaural beats (Delta, Theta, Alpha, Beta) for cognitive enhancement.
*   **Analog Warmth:** Simulates tape wobble, modulation, and tube saturation for an organic feel.

---

## 🚀 Quick Start

### 1. Installation
```bash
pip install -r requirements.txt
```
*(Requires Python 3.10+ and ~10GB disk space for models)*

### 2. Generate Assets (The Ingredients)
Generate 5 raw atmospheric samples and 5 percussive loops for the "Water" theme:
```bash
python scripts/generate_soundscape.py Water --type atmospheric --count 5
python scripts/generate_soundscape.py Water --type percussive --count 5
```

### 3. Compose Masterpiece (The Meal)
Compose a 10-minute unique soundscape using the generated assets:
```bash
python scripts/compose_soundscape.py Water --duration 10 --count 1
```
*This picks random samples, applies the V7 Engine, and saves the result to `audio_samples/processed/water/{id}/`.*

---

## 📚 Documentation

*   **[User Manual](docs/USER_MANUAL.md):** Detailed usage guide.
*   **[Technical Deep Dive](docs/TECHNICAL_Deep_Dive.md):** Architecture, DSP logic, and signal flow.

---

## 📂 Output Structure

Every generated track comes with a `manifest.json` "Recipe" file:
```
audio_samples/processed/water/aura_water_theta_1234_5678/
├── soundscape.wav      # The Audio File
└── manifest.json       # The Recipe (Source files, FX settings, Binaural Hz)
```

---

*Powered by Python, PyTorch, and Pedalboard.*
