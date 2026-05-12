import os
import subprocess
import tempfile
import sys
from pathlib import Path


# --------------------------------------------------------------
# Find most recent sequence folder or use provided path
# --------------------------------------------------------------

# Check if a valid path was provided (not a Jupyter kernel argument)
if len(sys.argv) > 1 and not sys.argv[1].startswith("-"):
    sequence_path = Path(sys.argv[1])
else:
    folders = sorted(
        Path("./output").glob("sequence_*"), key=os.path.getmtime, reverse=True
    )
    if not folders:
        sys.exit("No sequence folders found. Run 5-sora-remix.py first!")
    sequence_path = folders[0]

# --------------------------------------------------------------
# Find shot videos
# --------------------------------------------------------------

video_paths = [str(f.resolve()) for f in sorted(sequence_path.glob("shot_*.mp4"))]
if not video_paths:
    sys.exit(f"No shot videos found in {sequence_path}")

print(f"Stitching {len(video_paths)} shots from {sequence_path.name}")

# --------------------------------------------------------------
# Create concat file and stitch
# --------------------------------------------------------------

with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
    f.write("\n".join(f"file '{path}'" for path in video_paths))
    temp_path = f.name

output_file = sequence_path / "sequence.mp4"

try:
    result = subprocess.run(
        [
            "ffmpeg",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            temp_path,
            "-c:v",
            "libx264",
            "-c:a",
            "aac",
            str(output_file),
            "-y",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print("ffmpeg failed:")
        print(result.stderr)
        raise subprocess.CalledProcessError(result.returncode, result.args)
    print(f"Done: {output_file}")
finally:
    if os.path.exists(temp_path):
        os.unlink(temp_path)
