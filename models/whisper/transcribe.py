import os
import whisper


# --------------------------------------------------------------
# Config
# --------------------------------------------------------------
print(whisper.available_models())
model = whisper.load_model("turbo")
media_path = "./media/your-media.mp4"

# --------------------------------------------------------------
# Transcribe
# --------------------------------------------------------------

result = model.transcribe(media_path)

# --------------------------------------------------------------
# Save transcript
# --------------------------------------------------------------

os.makedirs("output", exist_ok=True)
output_path = f"output/{os.path.splitext(os.path.basename(media_path))[0]}.txt"
open(output_path, "w").write(result["text"])
