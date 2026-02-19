import numpy as np
import librosa
import soundfile as sf
import random
import os
from pedalboard import Pedalboard, Reverb, Compressor, LowpassFilter, HighpassFilter, Chorus, Phaser, Limiter, Delay, Gain, Convolution, PitchShift, Distortion
from pedalboard.io import AudioFile

class PaulStretch:
    def __init__(self, window_size_seconds=0.25):
        self.window_size_seconds = window_size_seconds

    def stretch(self, audio, sr, stretch_factor=8.0):
        n_samples = len(audio)
        window_size = int(self.window_size_seconds * sr)
        step = int(window_size / 2)

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
    BRAINWAVE_STATES = {
        "Delta": (1, 4), "Theta": (4, 8), "Alpha": (8, 14), "Beta": (14, 30)
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
        left = np.sin(2*np.pi*carrier_hz*t)
        right = np.sin(2*np.pi*(carrier_hz+beat_hz)*t)
        amp = 10**(volume_db/20)
        return np.vstack((left*amp, right*amp))

class SoundscapeComposer:
    """
    V9 Engine: Polyrhythmic Design + Tonal Variety
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
        if len(audio.shape) > 1: return np.mean(audio, axis=0)
        return audio

    def _apply_tremolo(self, audio, rate_hz=0.5, depth=0.3):
        t = np.linspace(0, audio.shape[1]/self.sr, audio.shape[1])
        modulator = (1.0 - depth) + depth * np.sin(2 * np.pi * rate_hz * t)
        return audio * modulator

    def _get_random_fx_chain(self, layer_type):
        chain = []
        if layer_type == 'drone':
            chain.append(Distortion(drive_db=random.uniform(1.0, 3.5))) 
            chain.append(LowpassFilter(cutoff_frequency_hz=random.uniform(450, 1000)))
            if random.random() > 0.3:
                chain.append(Chorus(rate_hz=random.uniform(0.01, 0.1), depth=0.3, mix=0.4))
        elif layer_type == 'body':
            chain.append(LowpassFilter(cutoff_frequency_hz=random.uniform(2500, 6000)))
            if random.random() > 0.5:
                chain.append(Phaser(rate_hz=random.uniform(0.1, 0.3), depth=0.5, mix=0.3))
            if random.random() > 0.5:
                chain.append(Delay(delay_seconds=random.uniform(0.1, 1.2), feedback=random.uniform(0.2, 0.5), mix=random.uniform(0.1, 0.3)))
        elif layer_type == 'texture':
            if random.random() > 0.4:
                chain.append(Phaser(rate_hz=random.uniform(0.5, 1.5), depth=0.6, mix=0.4))
            chain.append(Delay(delay_seconds=random.uniform(0.1, 0.8), feedback=random.uniform(0.3, 0.6), mix=random.uniform(0.2, 0.5)))
            chain.append(Chorus(rate_hz=0.5, depth=0.2, mix=0.2)) 
            chain.append(HighpassFilter(cutoff_frequency_hz=random.uniform(600, 1500)))

        if self.ir_files and random.random() > 0.3:
            try: chain.append(Convolution(random.choice(self.ir_files), mix=random.uniform(0.2, 0.4)))
            except: chain.append(Reverb(room_size=0.7, wet_level=0.3))
        else:
            chain.append(Reverb(room_size=0.7, wet_level=0.3))
        chain.append(Compressor(threshold_db=-15, ratio=2.5))
        return Pedalboard(chain)

    def compose_layer(self, input_file, duration_minutes=10, layer_type='drone'):
        y, sr = librosa.load(input_file, sr=self.sr)
        y = self._process_mono_to_stereo(y)
        base_level = 1.0 if layer_type == 'drone' else 0.95
        level = base_level * random.uniform(0.9, 1.1)
        target_duration = duration_minutes * 60
        stretch_factor = target_duration / (len(y) / sr)
        print(f"   -> Processing {layer_type.upper()} (Level: {level:.2f})...")
        stretched = self.stretcher.stretch(y, sr, stretch_factor) * level
        stereo = np.vstack((stretched, stretched))
        if layer_type in ['drone', 'body']:
            stereo = self._apply_tremolo(stereo, rate_hz=random.uniform(0.05, 0.2), depth=0.2)
        board = self._get_random_fx_chain(layer_type)
        return board(stereo.astype(np.float32), self.sr)

    def compose_pulse_layer(self, input_file, duration_minutes=10):
        y, sr = librosa.load(input_file, sr=self.sr)
        y = self._process_mono_to_stereo(y)
        loop_len = len(y)
        num_grains = 8
        grain_size = loop_len // num_grains
        grains = [y[i*grain_size : (i+1)*grain_size] for i in range(num_grains)]
        
        total_samples = int(duration_minutes * 60 * sr)
        output_buffer = np.zeros(total_samples, dtype=np.float32)
        
        # V9: Euclidean Rhythm Mask
        # Randomly select a rhythm pattern for this entire track
        # 1 = Play Grain, 0 = Silence
        # Examples: [1,0,1,0] (Steady), [1,0,0,1] (Syncopated)
        rhythm_seeds = [
            [1, 0, 1, 0, 1, 0, 1, 0], # Steady 4/4
            [1, 0, 0, 1, 0, 0, 1, 0], # Tresillo
            [1, 0, 0, 0, 1, 0, 0, 0], # Half-time
            [1, 1, 0, 1, 0, 1, 1, 0], # Dense
            [1, 0, 0, 0, 0, 0, 1, 0], # Sparse
        ]
        mask = random.choice(rhythm_seeds)
        
        # V9: Octave Selection (Bass vs High)
        octave_shift = random.choice([-12, 0, 0, 12]) 
        
        current_idx = 0
        while current_idx < total_samples:
            current_grains = grains.copy()
            # Random shuffle every bar
            if random.random() > 0.5:
                random.shuffle(current_grains)
            
            # Apply Mask
            masked_grains = []
            for i, grain in enumerate(current_grains):
                if mask[i % 8] == 1:
                    masked_grains.append(grain)
                else:
                    masked_grains.append(np.zeros_like(grain))
            
            bar_audio = np.concatenate(masked_grains)
            
            # Density Check (Silence whole bar?)
            if random.random() > 0.85: # Less frequent silence than V8
                bar_audio = np.zeros_like(bar_audio)
            
            len_to_add = min(len(bar_audio), total_samples - current_idx)
            output_buffer[current_idx : current_idx + len_to_add] = bar_audio[:len_to_add]
            current_idx += len_to_add
            
        stereo_loop = np.vstack((output_buffer, output_buffer))
        
        # V9: Stereo Cross-Delay for Evolving Echoes
        # Instead of one static delay, we use two with different times to create rhythm.
        board = Pedalboard([
            PitchShift(semitones=octave_shift),
            HighpassFilter(cutoff_frequency_hz=random.uniform(100, 400)),
            Phaser(rate_hz=random.uniform(0.1, 0.4), depth=0.6, mix=0.4),
            
            # Delay 1: Fast & Light
            Delay(delay_seconds=random.uniform(0.15, 0.3), feedback=0.3, mix=0.25),
            
            # Delay 2: Slow & Deep (creates polyrhythm against Delay 1)
            Delay(delay_seconds=random.uniform(0.4, 0.7), feedback=0.5, mix=0.2),
            
            # Modulate the tails
            Chorus(rate_hz=0.8, depth=0.3, mix=0.3), 
            
            Compressor(threshold_db=-18, ratio=2.5),
            Gain(gain_db=-2.0) 
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
            try: chain.append(Convolution(ir_path, mix=random.uniform(0.3, 0.5)))
            except: pass
        else: chain.append(Reverb(room_size=0.8, wet_level=0.3))
        chain.append(Compressor(threshold_db=-12, ratio=2.0))
        chain.append(Limiter(threshold_db=-1.0))
        return Pedalboard(chain)(mixed_audio.astype(np.float32), self.sr)

    def mix_track(self, layers):
        max_len = max([L.shape[1] for L in layers])
        mixed_audio = np.zeros((2, max_len), dtype=np.float32)
        for layer in layers:
            if layer.shape[1] < max_len:
                padded = np.zeros((2, max_len), dtype=np.float32)
                padded[:, :layer.shape[1]] = layer
                mixed_audio += padded
            else: mixed_audio += layer[:, :max_len]
        peak = np.max(np.abs(mixed_audio))
        if peak > 0.98: mixed_audio = mixed_audio / peak * 0.98
        return mixed_audio

if __name__ == "__main__": print("Audio Engine Module Loaded.")
