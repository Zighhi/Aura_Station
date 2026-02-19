from transformers import pipeline
import scipy.io.wavfile

def generate_audio(prompt, file_path):
    """
    Generates audio from a text prompt using a pre-trained model
    and saves it to a WAV file.
    """
    try:
        print("Initializing text-to-audio pipeline...")
        # Using a specific model revision to ensure compatibility
        synthesiser = pipeline("text-to-audio", "facebook/musicgen-small", revision="a609000")
        
        print(f"Generating audio for prompt: '{prompt}'")
        # The model returns the audio as a numpy array and the sampling rate
        music = synthesiser(prompt, forward_params={"do_sample": True})
        
        sampling_rate = music["sampling_rate"]
        audio_data = music["audio"]
        
        print(f"Saving audio to {file_path}...")
        scipy.io.wavfile.write(file_path, rate=sampling_rate, data=audio_data)
        
        print(f"Successfully generated and saved {file_path}")

    except Exception as e:
        print(f"An error occurred: {e}")
        print("Please ensure you have a stable internet connection for model download.")
        print("If the issue persists, there might be an incompatibility with the model or libraries.")

if __name__ == "__main__":
    # Define the creative prompt
    prompt_text = "A calm, atmospheric soundscape with gentle water sounds and a low, humming drone."
    
    # Define the output file path
    output_file = "musicgen_output.wav"
    
    generate_audio(prompt_text, output_file)
