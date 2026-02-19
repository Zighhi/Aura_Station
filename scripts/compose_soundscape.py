import argparse
import os
import sys
import numpy as np
import soundfile as sf
import random
import json
import datetime

# Ensure project root is in path
sys.path.append(os.getcwd())

from src.audio_engine import SoundscapeComposer

class HistoryTracker:
    """
    Manages a persistent history of used sample combinations to ensure uniqueness.
    """
    def __init__(self, history_file="audio_samples/processed/history.json"):
        self.history_file = history_file
        self.history = self._load_history()

    def _load_history(self):
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return {"combinations": []}
        return {"combinations": []}

    def _save_history(self):
        os.makedirs(os.path.dirname(self.history_file), exist_ok=True)
        with open(self.history_file, 'w') as f:
            json.dump(self.history, f, indent=4)

    def is_unique(self, file_list):
        """Checks if this specific combination of files (order-independent) has been used."""
        combo_key = sorted(file_list) # Sort to ignore order (set uniqueness)
        return combo_key not in self.history["combinations"]

    def add_combination(self, file_list):
        combo_key = sorted(file_list)
        self.history["combinations"].append(combo_key)
        self._save_history()

def save_manifest(output_wav_path, metadata):
    """
    Saves a JSON manifest alongside the generated WAV file.
    """
    manifest_path = output_wav_path.replace('.wav', '.json')
    
    # Add timestamp
    metadata["generated_at"] = datetime.datetime.now().isoformat()
    
    with open(manifest_path, 'w') as f:
        json.dump(metadata, f, indent=4)
    print(f"--- Manifest saved to {manifest_path} ---")

def main(theme, input_dir="audio_samples/raw", output_dir="audio_samples/processed", duration_minutes=10):
    print(f"===== STARTING SOUNDSCAPE COMPOSITION (V3 Dynamic Engine): {theme} =====")
    
    # Initialize History Tracker
    history = HistoryTracker()
    
    # 1. Find source samples
    theme_dir = os.path.join(input_dir, theme.lower())
    if not os.path.exists(theme_dir):
        print(f"Error: No samples found for theme '{theme}' in {theme_dir}")
        return

    samples = [f for f in os.listdir(theme_dir) if f.endswith(".wav")]
    if len(samples) < 3:
        print(f"Error: Need at least 3 samples for V3 layering. Found {len(samples)}.")
        return
        
    # Select 3 distinct samples for layering with History Check
    source_files = []
    attempts = 0
    max_attempts = 50
    
    while attempts < max_attempts:
        candidate_files = random.sample(samples, 3)
        if history.is_unique(candidate_files):
            source_files = candidate_files
            break
        attempts += 1
        
    if not source_files:
        print("Warning: Could not find a unique combination after 50 attempts. Using random selection.")
        source_files = random.sample(samples, 3)
    else:
        print(f"--- Unique Combination Found (Attempt {attempts+1}) ---")
        history.add_combination(source_files)

    drone_source = os.path.join(theme_dir, source_files[0])
    body_source = os.path.join(theme_dir, source_files[1])
    texture_source = os.path.join(theme_dir, source_files[2])
    
    print(f"--- Selected Sources ---")
    print(f"   Drone Base: {source_files[0]}")
    print(f"   Body Pad:   {source_files[1]}")
    print(f"   Texture:    {source_files[2]}")

    # 2. Initialize Composer
    composer = SoundscapeComposer()
    
    # 3. Create Layers
    print(f"--- Generating Layer 1: Deep Drone... ---")
    L1 = composer.compose_layer(drone_source, duration_minutes=duration_minutes, layer_type='drone')
    
    print(f"--- Generating Layer 2: Evolving Body... ---")
    L2 = composer.compose_layer(body_source, duration_minutes=duration_minutes, layer_type='body')
    
    print(f"--- Generating Layer 3: High Texture... ---")
    L3 = composer.compose_layer(texture_source, duration_minutes=duration_minutes, layer_type='texture')
    
    # Layer 4: Binaural Beat (Random State)
    state_name, beat_hz = composer.binaural.get_random_state()
    print(f"--- Generating Layer 4: Binaural Beat ({state_name} State - {beat_hz:.1f}Hz)... ---")
    L4 = composer.compose_binaural_layer(duration_minutes=duration_minutes, beat_hz=beat_hz)
    
    # Layer 5: Rhythmic Pulse (Optional)
    L5 = None
    loops_dir = os.path.join(theme_dir, "loops")
    if os.path.exists(loops_dir):
        loop_samples = [f for f in os.listdir(loops_dir) if f.endswith(".wav")]
        if loop_samples:
            pulse_source = os.path.join(loops_dir, random.choice(loop_samples))
            print(f"--- Generating Layer 5: Rhythmic Pulse ({os.path.basename(pulse_source)})... ---")
            L5 = composer.compose_pulse_layer(pulse_source, duration_minutes=duration_minutes)
    
    # 4. Mix
    print("--- Mixing Layers... ---")
    # Mix Ratios: Drone (70%), Body (50%), Texture (40%), Binaural (12% - Boosted), Pulse (30%)
    
    # Ensure all layers match the shortest length
    min_len = min(L1.shape[1], L2.shape[1], L3.shape[1], L4.shape[1])
    if L5 is not None:
        min_len = min(min_len, L5.shape[1])
    
    mix_L1 = L1[:, :min_len] * 0.7
    mix_L2 = L2[:, :min_len] * 0.5
    mix_L3 = L3[:, :min_len] * 0.4
    mix_L4 = L4[:, :min_len] * 0.12 # Boosted Binaural
    
    layers_to_mix = [mix_L1, mix_L2, mix_L3, mix_L4]
    if L5 is not None:
        mix_L5 = L5[:, :min_len] * 0.3
        layers_to_mix.append(mix_L5)
    
    raw_mix = composer.mix_track(layers_to_mix)
    
    # 5. Master Bus (Global Convolution + Limiting)
    print("--- Applying Master Bus (Global Space & Limiter)... ---")
    global_ir = None
    if composer.ir_files:
        global_ir = random.choice(composer.ir_files)
        print(f"   -> Using Impulse Response: {os.path.basename(global_ir)}")
        
    final_master = composer.apply_master_bus(raw_mix, ir_path=global_ir)
    
    # 6. Save Audio & Manifest
    
    def get_id(fname):
        parts = fname.split('_')
        if len(parts) >= 4:
            return parts[-1].replace('.wav', '') 
        return fname[:6]

    id_str = f"{get_id(source_files[0])}_{get_id(source_files[1])}_{get_id(source_files[2])}"
    track_id = f"aura_{theme.lower()}_{state_name.lower()}_{id_str}"
    
    # Create unique folder for this track
    track_dir = os.path.join(output_dir, theme.lower(), track_id)
    os.makedirs(track_dir, exist_ok=True)
    
    output_wav_path = os.path.join(track_dir, "soundscape.wav")
    
    print(f"--- Saving Masterpiece to {output_wav_path}... ---")
    sf.write(output_wav_path, final_master.T, composer.sr, subtype='PCM_24')
    
    # Create Metadata Dictionary
    metadata = {
        "track_id": track_id,
        "theme": theme,
# ... (rest is same)
        "duration_minutes": duration_minutes,
        "binaural_state": state_name,
        "binaural_hz": beat_hz,
        "global_ir": os.path.basename(global_ir) if global_ir else "Algorithmic",
        "layers": {
            "drone": {
                "source": source_files[0],
                "description": "Deep Drone Base"
            },
            "body": {
                "source": source_files[1],
                "description": "Evolving Body Pad"
            },
            "texture": {
                "source": source_files[2],
                "description": "High Frequency Texture"
            },
            "pulse": {
                "source": os.path.basename(pulse_source) if L5 is not None else "None",
                "description": "Rhythmic Pulse Layer"
            }
        },
        "mix_ratios": {
            "drone": 0.7,
            "body": 0.5,
            "texture": 0.4,
            "binaural": 0.12,
            "pulse": 0.3 if L5 is not None else 0
        }
    }
    
    save_manifest(output_wav_path, metadata)
    
    print("===== COMPOSITION COMPLETE! =====")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compose a long-form soundscape from raw samples.")
    parser.add_argument("theme", type=str, help="The theme to compose (Water, Fire, Earth).")
    parser.add_argument("--duration", type=int, default=10, help="Duration in minutes (default: 10).")
    parser.add_argument("--count", type=int, default=1, help="Number of variations to generate.")
    
    args = parser.parse_args()
    
    for i in range(args.count):
        print(f"\n>>> Generating Variation {i+1}/{args.count} <<<")
        main(args.theme, duration_minutes=args.duration)
