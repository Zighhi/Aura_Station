import numpy as np
import librosa
import soundfile as sf
import random
import os
from pedalboard import Pedalboard, Reverb, Compressor, LowpassFilter, HighpassFilter, Chorus, Phaser, Limiter, Delay, Gain, Convolution, PitchShift
from pedalboard.io import AudioFile

class PaulStretch:
    """
    A robust Python implementation of the PaulStretch algorithm.
    Creates smooth, high-quality ambient textures by smearing audio over time.
    """
    def __init__(self, window_size_seconds=0.25):
        self.window_size_seconds = window_size_seconds

    def stretch(self, audio, sr, stretch_factor=8.0):
        n_samples = len(audio)
        window_size = int(self.window_size_seconds * sr)
        step = int(window_size / 2) # 50% overlap

        stft = librosa.stft(audio, n_fft=window_size, hop_length=step, window='hann')
        magnitude = np.abs(stft)
        
        n_frames = magnitude.shape[1]
        new_n_frames = int(n_frames * stretch_factor)
        
        old_times = np.linspace(0, n_frames, n_frames)
        new_times = np.linspace(0, n_frames, new_n_frames)
        
        new_magnitude = np.zeros((magnitude.shape[0], new_n_frames))
        for i in range(magnitude.shape[0]):
            new_magnitude[i, :] = np.interp(new_times, old_times, magnitude[i, :])

        new_phase = 2 * np.pi * np.random.rand(new_magnitude.shape[0], new_magnitude.shape[1])
        new_stft = new_magnitude * np.exp(1j * new_phase)
        stretched_audio = librosa.istft(new_stft, hop_length=step, window='hann')
        
        max_val = np.max(np.abs(stretched_audio))
        if max_val > 0:
            stretched_audio = stretched_audio / max_val * 0.8 
            
        return stretched_audio

class BinauralGenerator:
    """
    Generates binaural beats for various focus and relaxation states.
    """
    BRAINWAVE_STATES = {
        "Delta": (1, 4),   # Deep Sleep, Healing
        "Theta": (4, 8),   # Creativity, Meditation
        "Alpha": (8, 14),  # Relaxed Focus, Stress Reduction
        "Beta": (14, 30)   # Active Focus, Cognition
    }

    def __init__(self, sr=44100):
        self.sr = sr

    def get_random_state(self):
        state_name = random.choice(list(self.BRAINWAVE_STATES.keys()))
        min_hz, max_hz = self.BRAINWAVE_STATES[state_name]
        beat_hz = random.uniform(min_hz, max_hz)
        return state_name, beat_hz

    def generate_beat(self, duration_seconds, carrier_hz=200, beat_hz=10, volume_db=-25):
        t = np.linspace(0, duration_seconds, int(self.sr * duration_seconds), endpoint=False)
        left_wave = np.sin(2 * np.pi * carrier_hz * t)
        right_wave = np.sin(2 * np.pi * (carrier_hz + beat_hz) * t)
        amplitude = 10 ** (volume_db / 20)
        stereo_audio = np.vstack((left_wave * amplitude, right_wave * amplitude))
        return stereo_audio


class SoundscapeComposer:
    """
    Orchestrates the assembly of the final soundscape using Pedalboard.
    V5: Dual-Stage Convolution, Amplitude Modulation, Smart Pulse Arrangement.
    """
    def __init__(self, sr=44100, ir_dir="assets/impulses"):
        self.sr = sr
        self.stretcher = PaulStretch()
        self.binaural = BinauralGenerator(sr)
        
        self.ir_files = []
        if os.path.exists(ir_dir):
            for root, dirs, files in os.walk(ir_dir):
                for f in files:
                    if f.lower().endswith(".wav"):
                        self.ir_files.append(os.path.join(root, f))

    def _process_mono_to_stereo(self, audio):
        if len(audio.shape) > 1:
            return np.mean(audio, axis=0)
        return audio

    def _apply_tremolo(self, audio, rate_hz=0.5, depth=0.3):
        """Applies Amplitude Modulation (Tremolo) via Numpy."""
        t = np.linspace(0, audio.shape[1]/self.sr, audio.shape[1])
        modulator = (1.0 - depth) + depth * np.sin(2 * np.pi * rate_hz * t)
        return audio * modulator

    def _get_random_fx_chain(self, layer_type):
        """Generates a random FX chain based on layer type (Pre-Master)."""
        chain = []
        
        if layer_type == 'drone':
            chain.append(Chorus(rate_hz=random.uniform(0.05, 0.2), depth=0.3, mix=0.4))
            chain.append(LowpassFilter(cutoff_frequency_hz=random.uniform(200, 450)))
        
        elif layer_type == 'body':
            chain.append(Phaser(rate_hz=random.uniform(0.1, 0.3), depth=0.5, mix=0.3))
            chain.append(HighpassFilter(cutoff_frequency_hz=random.uniform(150, 300)))
            chain.append(Delay(delay_seconds=random.uniform(0.3, 0.6), feedback=0.3, mix=0.2))

        elif layer_type == 'texture':
            chain.append(Phaser(rate_hz=random.uniform(0.5, 1.5), depth=0.6, mix=0.4))
            chain.append(HighpassFilter(cutoff_frequency_hz=random.uniform(1500, 3000)))

        # Per-Layer Convolution (Depth)
        if self.ir_files and random.random() > 0.3:
            try:
                ir = random.choice(self.ir_files)
                chain.append(Convolution(ir, mix=random.uniform(0.2, 0.4)))
            except:
                chain.append(Reverb(room_size=0.7, wet_level=0.3))
        else:
            chain.append(Reverb(room_size=0.7, wet_level=0.3))

        chain.append(Compressor(threshold_db=-15, ratio=2.5))
        return Pedalboard(chain)

    def compose_layer(self, input_file, duration_minutes=10, layer_type='drone'):
        y, sr = librosa.load(input_file, sr=self.sr)
        y = self._process_mono_to_stereo(y)
        
        base_level = 1.0 if layer_type == 'drone' else 0.8
        level = base_level * random.uniform(0.8, 1.2)
        
        target_duration = duration_minutes * 60
        stretch_factor = target_duration / (len(y) / sr)
        
        print(f"   -> Processing {layer_type.upper()} (Level: {level:.2f})...")
        stretched = self.stretcher.stretch(y, sr, stretch_factor) * level
        stereo = np.vstack((stretched, stretched))
        
        # Apply Tremolo (Breathing)
        if layer_type in ['drone', 'body']:
            stereo = self._apply_tremolo(stereo, rate_hz=random.uniform(0.05, 0.2), depth=0.2)

        board = self._get_random_fx_chain(layer_type)
        return board(stereo.astype(np.float32), self.sr)

    def compose_pulse_layer(self, input_file, duration_minutes=10):
        """
        Layer 5: The V6 Organic Pulse.
        Uses Granular Shuffling and Probabilistic Density to create an evolving, non-repetitive rhythm.
        """
        y, sr = librosa.load(input_file, sr=self.sr)
        y = self._process_mono_to_stereo(y)
        
        # Ensure we have a clean loop length (cut to nearest beat if possible, but for now just use raw)
        loop_len = len(y)
        
        # Granular Settings
        num_grains = 8 # Slice loop into 8 grains
        grain_size = loop_len // num_grains
        grains = [y[i*grain_size : (i+1)*grain_size] for i in range(num_grains)]
        
        total_samples = int(duration_minutes * 60 * sr)
        output_buffer = np.zeros(total_samples, dtype=np.float32) # Mono buffer first
        
        current_idx = 0
        while current_idx < total_samples:
            # For each "bar" (repetition of the loop length), we generate a new variation
            
            # 1. Shuffle Grains (Variation)
            # We keep the first grain (downbeat) fixed 50% of the time to keep the groove anchored
            current_grains = grains.copy()
            if random.random() > 0.5:
                # Shuffle the rest
                middle = current_grains[1:]
                random.shuffle(middle)
                current_grains = [current_grains[0]] + middle
            else:
                random.shuffle(current_grains)
                
            # 2. Construct the Bar
            bar_audio = np.concatenate(current_grains)
            
            # 3. Probabilistic Density (Space)
            # Randomly silence 30% of the bar? Or pitch shift?
            # Let's pitch shift the whole bar occasionally
            pitch_shift = 0
            if random.random() > 0.7:
                pitch_shift = random.choice([-2, -5, 2])
                # We can't pitch shift easily in pure numpy without duration change or artifacts.
                # So we skip pitch shifting here and rely on Pedalboard FX later?
                # Actually, skipping/silencing is safer for "organic" feel.
                
            if random.random() > 0.8:
                # Silence this bar completely (Space)
                bar_audio = np.zeros_like(bar_audio)
            
            # Add to buffer
            len_to_add = min(len(bar_audio), total_samples - current_idx)
            output_buffer[current_idx : current_idx + len_to_add] = bar_audio[:len_to_add]
            current_idx += len_to_add
            
        # Make Stereo
        stereo_loop = np.vstack((output_buffer, output_buffer))
        
        # FX Chain
        board = Pedalboard([
            HighpassFilter(cutoff_frequency_hz=random.uniform(300, 600)),
            Phaser(rate_hz=random.uniform(0.1, 0.4), depth=0.6, mix=0.4),
            # Add Delay to fill the gaps created by shuffling/silence
            Delay(delay_seconds=0.25, feedback=0.4, mix=0.3),
            Compressor(threshold_db=-18, ratio=2.5),
            Gain(gain_db=-3.0) 
        ])
        
        return board(stereo_loop.astype(np.float32), self.sr)

    def compose_binaural_layer(self, duration_minutes=10, beat_hz=10):
        duration_seconds = duration_minutes * 60
        beat_audio = self.binaural.generate_beat(duration_seconds, beat_hz=beat_hz)
        beat_audio = self._apply_tremolo(beat_audio, rate_hz=0.1, depth=0.15)
        return beat_audio.astype(np.float32)

    def apply_master_bus(self, mixed_audio, ir_path=None):
        chain = []
        if ir_path:
            try:
                chain.append(Convolution(ir_path, mix=random.uniform(0.3, 0.5)))
            except: pass
        else:
            chain.append(Reverb(room_size=0.8, wet_level=0.3))
            
        chain.append(Compressor(threshold_db=-12, ratio=2.0))
        chain.append(Limiter(threshold_db=-1.0))
        
        board = Pedalboard(chain)
        return board(mixed_audio.astype(np.float32), self.sr)

    def mix_track(self, layers):
        max_len = max([L.shape[1] for L in layers])
        mixed_audio = np.zeros((2, max_len), dtype=np.float32)
        
        for layer in layers:
            if layer.shape[1] < max_len:
                padded = np.zeros((2, max_len), dtype=np.float32)
                padded[:, :layer.shape[1]] = layer
                mixed_audio += padded
            else:
                mixed_audio += layer[:, :max_len]
                
        peak = np.max(np.abs(mixed_audio))
        if peak > 0.98:
            mixed_audio = mixed_audio / peak * 0.98
            
        return mixed_audio

if __name__ == "__main__":
    print("Audio Engine Module Loaded.")
