import os
import json
import shutil
import csv
import datetime
import argparse

def create_review_pack(input_dir="audio_samples/processed", output_dir="review_packs"):
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M")
    pack_name = f"Aura_Review_Pack_{timestamp}"
    pack_dir = os.path.join(output_dir, pack_name)
    assets_dir = os.path.join(pack_dir, "assets")
    
    os.makedirs(assets_dir, exist_ok=True)
    
    tracks = []
    
    print(f"--- Scanning {input_dir} for masterpieces... ---")
    
    # 1. Scan and Copy
    for root, dirs, files in os.walk(input_dir):
        for f in files:
            if f == "soundscape.json":
                manifest_path = os.path.join(root, f)
                wav_path = os.path.join(root, "soundscape.wav")
                
                if os.path.exists(wav_path):
                    with open(manifest_path, 'r') as json_file:
                        data = json.load(json_file)
                        
                    track_id = data.get("track_id", "unknown")
                    theme = data.get("theme", "unknown")
                    binaural = f"{data.get('binaural_state', 'Unknown')} ({data.get('binaural_hz', 0):.1f}Hz)"
                    
                    # Copy WAV to pack assets with unique name
                    dest_filename = f"{track_id}.wav"
                    shutil.copy2(wav_path, os.path.join(assets_dir, dest_filename))
                    
                    tracks.append({
                        "id": track_id,
                        "theme": theme,
                        "binaural": binaural,
                        "filename": dest_filename,
                        "components": [
                            f"Drone: {data['layers']['drone']['source'][:15]}...",
                            f"Pulse: {data['layers']['pulse']['source'][:15]}..."
                        ]
                    })

    if not tracks:
        print("No tracks found! Check your processed folder.")
        return

    # 2. Generate CSV Feedback Form
    csv_path = os.path.join(pack_dir, "feedback.csv")
    with open(csv_path, 'w', newline='') as csvfile:
        fieldnames = ['Track ID', 'Theme', 'Rating (1-5)', 'Comments', 'Keep/Discard']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for t in tracks:
            writer.writerow({
                'Track ID': t['id'],
                'Theme': t['theme'],
                'Rating (1-5)': '',
                'Comments': '',
                'Keep/Discard': ''
            })
            
    print(f"--- Generated Feedback Form: {csv_path} ---")

    # 3. Generate HTML Player
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Aura Station Review | {timestamp}</title>
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #121212; color: #e0e0e0; padding: 20px; }}
            h1 {{ border-bottom: 2px solid #333; padding-bottom: 10px; color: #fff; }}
            .track-card {{ background: #1e1e1e; border-radius: 8px; padding: 20px; margin-bottom: 20px; border-left: 5px solid #333; }}
            .track-card.Water {{ border-left-color: #00bcd4; }}
            .track-card.Fire {{ border-left-color: #ff5722; }}
            .track-card.Earth {{ border-left-color: #8bc34a; }}
            .meta {{ color: #aaa; font-size: 0.9em; margin-bottom: 10px; display: flex; gap: 15px; }}
            .tag {{ background: #333; padding: 2px 8px; border-radius: 4px; }}
            audio {{ width: 100%; margin-top: 10px; }}
            .components {{ font-size: 0.8em; color: #666; margin-top: 10px; font-family: monospace; }}
        </style>
    </head>
    <body>
        <h1>Aura Station Review Kit ({timestamp})</h1>
        <p>Please review the tracks below and fill out <strong>feedback.csv</strong>.</p>
    """
    
    # Sort by Theme
    tracks.sort(key=lambda x: x['theme'])
    
    for t in tracks:
        html_content += f"""
        <div class="track-card {t['theme']}">
            <h3>{t['theme']} - {t['id']}</h3>
            <div class="meta">
                <span class="tag">{t['binaural']}</span>
                <span class="tag">{t['theme']}</span>
            </div>
            <div class="components">
                {t['components'][0]} | {t['components'][1]}
            </div>
            <audio controls>
                <source src="assets/{t['filename']}" type="audio/wav">
                Your browser does not support the audio element.
            </audio>
        </div>
        """
        
    html_content += """
    </body>
    </html>
    """
    
    html_path = os.path.join(pack_dir, "index.html")
    with open(html_path, 'w') as f:
        f.write(html_content)
        
    print(f"--- Generated HTML Player: {html_path} ---")
    print(f"===== REVIEW PACK READY: {pack_dir} =====")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a review pack from processed soundscapes.")
    parser.add_argument("--input_dir", type=str, default="audio_samples/processed", help="Path to processed audio folders.")
    args = parser.parse_args()
    
    create_review_pack(input_dir=args.input_dir)
