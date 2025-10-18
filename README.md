# Pink Voice

Fast voice transcription menu bar app for macOS (Apple Silicon only).

## Features

- Menu bar icon - always accessible
- Ctrl+Q hotkey - start/stop recording from any app
- Audio feedback - beeps on start, stop, and completion
- NVIDIA Parakeet TDT v3 - multilingual transcription model
- Auto-clipboard - transcription copied instantly
- Portable - everything in one folder

## Requirements

- macOS 12.0+ (Monterey or later)
- Apple Silicon (M1, M2, M3, M4, M5)
- Python 3.12+
- ~3GB free space (model + dependencies)

## Installation

```bash
# 1. Create virtual environment (requires Python 3.12)
python3.12 -m venv venv

# 2. Activate
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt
```

**Note:** First launch downloads the Parakeet model (~600MB) in the background.

## Usage

```bash
./start.sh
```

After launch:
1. Icon appears in menu bar
2. App loads model in background (first time only)
3. Press **Ctrl+Q** to start/stop recording
4. Transcription automatically copied to clipboard

### Menu Bar

Click the icon to see:
- **Loading...** - model loading
- **Start Recording** - ready to record
- **Stop Recording** - recording in progress
- **Transcribing...** - processing audio
- **Quit** - exit app

## Permissions

macOS will request permissions on first launch:
- **Microphone** - for audio recording
- **Accessibility** - for Ctrl+Q global hotkey

## Project Structure

```
pink-voice/
├── app/
│   ├── main.py         # Main application (menu bar + hotkey)
│   ├── transcriber.py  # Parakeet transcription engine
│   └── recorder.py     # Audio recording
├── assets/             # App icon
├── venv/               # Virtual environment
├── requirements.txt
├── start.sh
└── README.md
```

## Technical Details

**Stack:**
- Python - runtime environment
- NeMo Toolkit - NVIDIA framework for speech AI
- PyTorch - machine learning backend
- rumps - macOS native menu bar interface
- pynput - system-wide keyboard shortcuts
- sounddevice - audio capture via Core Audio

**Model:**
- nvidia/parakeet-tdt-0.6b-v3
- Multilingual support
- ~600MB model size (3GB with all dependencies)
- Optimized for Apple MPS (Metal Performance Shaders)

**Performance:**
- First launch: model downloads in background
- Memory usage: ~1.5GB RAM
- Transcription speed: ~1 second per 30 seconds of audio (M4 Pro with MPS)

## Portability

The entire `pink-voice/` folder is portable:
- Copy to another Mac - works immediately
- All dependencies bundled in `venv/`
- Model cached in `~/.cache/huggingface/`

## Repository

https://github.com/pinkhairedboy/pink-voice
