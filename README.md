# Multimodal Intelligent Gesture and Voice Response Assistant

A Windows-oriented final-year project prototype based on the supplied 14-page synopsis. It combines webcam hand landmarks, voice commands, spoken feedback, confidence filtering, SQLite history, and a custom gesture dataset workflow.

## Features currently implemented
- Real-time hand tracking with OpenCV and MediaPipe (21 hand landmarks).
- Index-finger cursor movement and thumb-index pinch click.
- Voice command handling for apps/websites, search, time/date, screenshot, scroll and volume.
- Offline Vosk speech-recognition path when a model is installed; English/Hindi/Marathi command phrases are mapped in `intent_parser.py`.
- Confidence thresholds and de-duplication in `fusion_engine.py`; low-confidence commands are ignored and disruptive commands are not executed.
- Offline speech output using pyttsx3.
- SQLite command history and calibration storage (`database.py`).
- Dataset capture (`capture_dataset.py`) and optional SVM baseline evaluation (`evaluate_dataset.py`).

## Setup (Windows 10/11)
1. Install 64-bit Python 3.10 or 3.11.
2. Extract this folder to a short path, e.g. `C:\MultimodalAssistant`.
3. Run `install_windows.bat`.
4. Download a Vosk model from https://alphacephei.com/vosk/models and extract it into `models/`. Example: `models/vosk-model-small-en-us-0.15/`.
5. Copy `.env.example` to `.env` if the installer did not create it; set `VOSK_MODEL_PATH` to the extracted model folder.
6. Run `run_windows.bat`. Keep the terminal open.

The assistant can still demonstrate gesture control if no Vosk model is present; voice input will not operate offline until the model is installed. Do not substitute Google online speech recognition if your requirement is fully offline.

## Voice commands
Try: `open calculator`, `open notepad`, `open browser`, `open YouTube`, `search for machine learning`, `volume up`, `volume down`, `mute`, `take screenshot`, `what time is it`, `undo`, `repeat that`, `help`, `stop assistant`. Common Hindi/Marathi phrase aliases are included, but recognition depends on the selected language model.

## Gesture controls
- Move index fingertip to move cursor.
- Pinch thumb and index finger to click.
- PyAutoGUI fail-safe is enabled: moving the cursor to the upper-left corner stops unsafe mouse automation.

## Dataset workflow
Run `python capture_dataset.py --label click --count 100` and repeat with at least two labels. The CSV is stored under `data/gesture_dataset.csv`. For an optional evaluation baseline, run `pip install -r requirements-ml.txt` then `python evaluate_dataset.py`. This evaluation is a classical SVM baseline over landmarks, not a CNN. The main runtime currently uses rule-based MediaPipe landmarks for reliability. A CNN model is not supplied pre-trained; train and evaluate a CNN separately before claiming CNN results in your report.

## Architecture files
- `main.py`: voice, gesture, TTS and action workers.
- `intent_parser.py`: maps recognised multilingual phrases to intents.
- `fusion_engine.py`: confidence filtering, de-duplication and action safety.
- `database.py`: SQLite history and calibration records.
- `capture_dataset.py`: webcam landmark dataset collection.
- `evaluate_dataset.py`: optional train/test baseline evaluation.

## Troubleshooting
- MediaPipe import/API errors: use the project's `.venv` and pinned requirements; do not run with an unrelated Python environment.
- Webcam unavailable: close Camera/Teams/Zoom and retry.
- Voice model missing: check `VOSK_MODEL_PATH` and ensure the folder contains the model files, not just a nested folder.
- Microphone error: allow microphone access in Windows privacy settings and check the selected input device.
- No TTS audio: check Windows output volume/device.

## Important scope statement
This is a runnable prototype aligned with the supplied synopsis, not a validated research result. The synopsis proposes a CNN classifier, multilingual offline voice recognition, confidence-weighted fusion, few-shot calibration and full offline operation. This package provides an operational baseline and dataset workflow; CNN training/integration and systematic experimental evaluation remain work to complete. Record only measured accuracy/latency in the final report.
