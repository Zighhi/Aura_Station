import os
import re
import torch
import numpy as np
import scipy.io.wavfile
import argparse
import datetime
import sys

# Ensure the project root is in sys.path
sys.path.append(os.getcwd())

# --- Set Cache Directory BEFORE importing transformers ---
print("--- Setting up local cache directory... ---")
cache_dir = os.path.join(os.getcwd(), '.cache', 'huggingface')
os.environ['HF_HOME'] = cache_dir
os.makedirs(cache_dir, exist_ok=True)

os.environ['HF_HUB_DISABLE_SYMLINKS_WARNING'] = '1' # Suppress symlink warning

from transformers import pipeline
from src.prompt_engineering import WaterPromptAgent, FirePromptAgent, EarthPromptAgent, PercussivePromptAgent

# --- 1. PROMPT GENERATION ---

def get_theme_agent(theme, type="atmospheric"):
    """Returns the appropriate PromptAgent for a given theme and type."""
    if type == "percussive":
        return PercussivePromptAgent()
    
    if theme == "Water": return WaterPromptAgent()
    elif theme == "Fire": return FirePromptAgent()
    elif theme == "Earth": return EarthPromptAgent()
    return None

def generate_rich_prompt(theme, type="atmospheric", text_gen_model="gpt2-medium"):
    """
    Uses a hybrid approach:
    1. Generates a structured base prompt from a specialized PromptAgent.
    2. Uses a text-generation model to creatively expand it (for atmospheric only).
    """
    agent = get_theme_agent(theme, type)
    if not agent:
        print(f"No specialized agent found for theme: {theme}")
        return None
    
    # Percussive agent handles theme internally
    if type == "percussive":
        base_prompt = agent.generate_prompt(theme)
    else:
        base_prompt = agent.generate_prompt()
        
    print(f"--- Base Structured Prompt ---")
    print(base_prompt)

    # For Percussive loops, the structured prompt is usually enough. Expansion often dilutes the rhythm.
    if type == "percussive":
        return f"Rhythmic loop: {base_prompt}, high fidelity, 3d spatial audio."

    print(f"--- Initializing '{text_gen_model}' for prompt expansion... ---")
    try:
        prompt_generator = pipeline('text-generation', model=text_gen_model)
    except Exception as e:
        print(f"Error loading text generation model: {e}")
        return base_prompt # Fallback to base prompt if ML fails

    # Meta-prompt now uses the structured prompt as a starting point
    meta_prompt = (
        f"Expand the following sound design description into a more evocative, rich, and detailed paragraph "
        f"suitable for a 30-second atmospheric soundscape. Focus on sensory details and textures. "
        f"Ensure the tone is study-safe: consistent, steady-state, and non-distracting background layers. "
        f"CRITICAL: Avoid any musical climax, sudden impacts, or resolution at the end. "
        f"The sound should be a continuous ambient bed that could fade out or loop seamlessly. "
        f"Keep the mood serene and relaxing.\n\n"
        f"Description: {base_prompt}\n\n"
        f"Expanded Version:"
    )

    print("--- Generating expanded rich prompt... ---")
    try:
        generated_output = prompt_generator(
            meta_prompt, max_new_tokens=100, num_return_sequences=1, temperature=0.75, do_sample=True
        )
    except Exception as e:
        print(f"Error during text generation: {e}")
        return base_prompt

    # --- Output Cleaning ---
    full_text = generated_output[0]['generated_text']
    newly_generated_text = full_text.replace(meta_prompt, "").strip()
    
    # We want a more substantial expansion now, so let's take up to three sentences
    sentences = re.split(r'(?<=[.!?])\s+', newly_generated_text)
    expansion = " ".join(sentences[:3])
    
    final_prompt = f"Study-friendly {theme} soundscape: {base_prompt} {expansion}"
    
    print("--- Final Hybrid Prompt ---")
    print(final_prompt)
    
    return final_prompt

# --- 2. AUDIO GENERATION ---

def generate_audio_from_prompt(prompt, type="atmospheric", audio_model="facebook/musicgen-small"):
    """
    Generates a high-quality creative soundscape or loop from a text prompt.
    """
    print(f"--- Initializing '{audio_model}' for audio generation... ---")
    device = 0 if torch.cuda.is_available() else -1
    try:
        synthesiser = pipeline("text-to-audio", audio_model, device=device)
    except Exception as e:
        print(f"Error loading audio generation model: {e}")
        return None, None

    # Determine length based on type
    if type == "percussive":
        # 750 tokens is approx 15 seconds. Good for loops.
        token_count = 750
        trim = False
        print(f"--- Generating rhythmic loop (~15s)... ---")
    else:
        # Atmospheric: Generate 33s, trim to 30s
        token_count = 1650 
        trim = True
        print(f"--- Generating soundscape (~33s -> 30s)... ---")

    try:
        music = synthesiser(prompt, forward_params={"do_sample": True, "max_new_tokens": token_count})
        audio_data = music["audio"]
        sampling_rate = music["sampling_rate"]
        
        if trim:
            # Slice to exactly 30 seconds
            target_length_samples = sampling_rate * 30
            audio_data = audio_data[:target_length_samples]
        
        return audio_data, sampling_rate
    except Exception as e:
        print(f"Error during audio generation: {e}")
        return None, None

# --- 3. MAIN EXECUTION ---

def main(theme, type="atmospheric", output_dir="audio_samples/raw"):
    """
    Main function to run the end-to-end soundscape generation pipeline.
    """
    print(f"===== STARTING GENERATION: {theme} ({type.upper()}) =====")
    
    rich_prompt = generate_rich_prompt(theme, type=type)
    if not rich_prompt:
        print("Halting pipeline due to prompt generation failure."); return

    audio_data, sampling_rate = generate_audio_from_prompt(rich_prompt, type=type)
    if audio_data is None:
        print("Halting pipeline due to audio generation failure."); return

    # --- Save the audio file ---
    # Organize percussive loops into a subfolder? Or just suffix?
    # Let's use subfolder: audio_samples/raw/water/loops/
    if type == "percussive":
        theme_output_dir = os.path.join(output_dir, theme.lower(), "loops")
    else:
        theme_output_dir = os.path.join(output_dir, theme.lower())
        
    os.makedirs(theme_output_dir, exist_ok=True)
    
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{type}_loop_{theme.lower()}_{timestamp}.wav" if type == "percussive" else f"base_sample_{theme.lower()}_{timestamp}.wav"
    output_path = os.path.join(theme_output_dir, filename)
    
    print(f"--- Saving audio to {output_path}... ---")
    # Normalize
    normalized_audio = audio_data / np.max(np.abs(audio_data)) * 0.9
    pcm_audio = (normalized_audio * 32767).astype(np.int16)
    
    scipy.io.wavfile.write(output_path, rate=sampling_rate, data=pcm_audio)
    
    print(f"===== SUCCESS! Saved to {output_path} =====")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate soundscapes or loops based on themes.")
    parser.add_argument(
        "themes", 
        type=str, 
        nargs="+",
        choices=["Water", "Fire", "Earth", "All"],
        help="The theme(s) for the generation. Use 'All' for all themes."
    )
    parser.add_argument(
        "--count",
        type=int,
        default=1,
        help="Number of samples to generate per theme (default: 1)."
    )
    parser.add_argument(
        "--type",
        type=str,
        default="atmospheric",
        choices=["atmospheric", "percussive"],
        help="Type of generation: 'atmospheric' (30s drone) or 'percussive' (15s rhythm loop)."
    )
    
    args = parser.parse_args()
    
    target_themes = args.themes
    if "All" in target_themes:
        target_themes = ["Water", "Fire", "Earth"]
    
    for theme in target_themes:
        for i in range(args.count):
            print(f"\n>>> Generating Sample {i+1}/{args.count} for Theme: {theme} <<<")
            main(theme, type=args.type)
