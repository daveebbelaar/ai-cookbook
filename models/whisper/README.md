# Whisper Transcription

Transcribes media to text using OpenAI's open-source Whisper model.

## Setup

```bash
uv pip install -r requirements.txt
```

## Usage

Edit `media_path` in `transcribe.py` and run:

```bash
uv run transcribe.py
```

Outputs plain text transcript to `output/{media_name}.txt`.

## Models

Available models can be listed by: `whisper.available_models()`

| Model | Type | Speed | Accuracy | Use Case |
|-------|------|-------|----------|----------|
| `tiny.en` / `tiny` | English-only / Multilingual | Fastest | Lowest | Quick tests, low accuracy needs |
| `base.en` / `base` | English-only / Multilingual | Fast | Low | General purpose, English preferred |
| `small.en` / `small` | English-only / Multilingual | Medium | Medium | Balanced speed/accuracy |
| `medium.en` / `medium` | English-only / Multilingual | Slow | High | Better accuracy, multilingual |
| `large-v1` / `large-v2` / `large-v3` | Multilingual | Slowest | Highest | Maximum accuracy (v3 latest) |
| `large` | Multilingual | Slowest | Highest | Latest large model (v3) |
| `turbo` (alias: `large-v3-turbo`) | Multilingual | ~8x faster than large-v3 | ~Same as large-v3 | Best balance: high accuracy + speed (recommended) |