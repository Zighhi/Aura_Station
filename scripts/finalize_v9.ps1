$batchPid = 20476
Write-Host "Monitoring Batch Process ID: $batchPid"

# Wait for process to finish
while (Get-Process -Id $batchPid -ErrorAction SilentlyContinue) {
    Start-Sleep -Seconds 30
}

Write-Host "Batch finished. Organizing files..."

# Create V9 Archive
$v9Dir = "audio_samples/archive_v9"
New-Item -ItemType Directory -Force -Path $v9Dir | Out-Null

# Move Processed files (Water, Fire, Earth folders) to V9 Archive
# We assume 'processed' contains the new folders.
# Note: compose_soundscape saves to audio_samples/processed/{theme}/{id}
# We want to move the CONTENTS of processed to archive_v9, effectively clearing processed for next time?
# Or just copy? Let's move.

Get-ChildItem "audio_samples/processed" -Directory | Move-Item -Destination $v9Dir -Force

Write-Host "Files moved to $v9Dir"

# Generate Review Pack from the V9 Archive
Write-Host "Generating Review Pack..."
python scripts/create_review_pack.py --input_dir $v9Dir

Write-Host "Done! Check review_packs folder."
