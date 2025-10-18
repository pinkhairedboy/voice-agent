#!/usr/bin/env python3
"""
Voice Input - Voice transcription for macOS
"""

import warnings
warnings.filterwarnings('ignore')

import os
os.environ['PYTHONWARNINGS'] = 'ignore'

import sys
sys.path.insert(0, os.path.dirname(__file__))

import rumps
import subprocess
import time
import threading
import signal
from pynput import keyboard

from transcriber import Transcriber
from recorder import AudioRecorder


class VoiceInputApp(rumps.App):
    def __init__(self):
        icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "icon.png")

        super(VoiceInputApp, self).__init__(
            name="Voice Input",
            icon=icon_path,
            quit_button="Quit"
        )

        self.transcriber = Transcriber()
        self.recorder = AudioRecorder()
        self.is_loading = True
        self.hotkey_listener = None
        self.is_processing = False  # защита от race condition

        self.action_button = rumps.MenuItem("Loading...", callback=self._menu_toggle_recording)

        self.menu = [
            self.action_button,
        ]

        threading.Thread(target=self._load_model, daemon=True).start()
        self._setup_hotkey()

    def _load_model(self):
        try:
            self.transcriber.load_model()
            self.is_loading = False

            rumps.notification(
                title="Voice Input",
                subtitle="Ready",
                message="Press Ctrl+Q or menu to start recording",
                sound=False
            )

            self.action_button.title = "Start Recording"

        except Exception as e:
            print(f"Error: {e}")
            rumps.alert(title="Error", message=f"Failed to load model: {e}")
            rumps.quit_application()

    def _setup_hotkey(self):
        self.hotkey_listener = keyboard.GlobalHotKeys({
            '<ctrl>+q': lambda: self._toggle_recording()
        })
        self.hotkey_listener.start()

    def _menu_toggle_recording(self, _):
        self._toggle_recording()

    def _toggle_recording(self):
        if self.is_loading or self.is_processing:
            return

        if self.recorder.is_recording():
            self._stop_recording()
        else:
            self._start_recording()

    def _start_recording(self):
        if self.recorder.start_recording():
            self.action_button.title = "Stop Recording"
            def delayed_beep():
                time.sleep(0.5)
                self._play_beep('/System/Library/Sounds/Ping.aiff')
            threading.Thread(target=delayed_beep, daemon=True).start()
        else:
            self.action_button.title = "Start Recording"

    def _stop_recording(self):
        if not self.recorder.is_recording():
            return

        self.is_processing = True
        self._play_beep('/System/Library/Sounds/Ping.aiff')
        self.action_button.title = "Transcribing..."
        threading.Thread(target=self._process_recording, daemon=True).start()

    def _process_recording(self):
        try:
            audio_path = self.recorder.stop_recording()

            if not audio_path:
                self.action_button.title = "Start Recording"
                self.is_processing = False
                return

            text = self.transcriber.transcribe(audio_path)

            self._play_beep('/System/Library/Sounds/Glass.aiff')
            self._copy_to_clipboard(text)

            rumps.notification(
                title="Voice Input",
                subtitle="Done",
                message=text[:100] + ("..." if len(text) > 100 else ""),
                sound=False
            )

            try:
                os.unlink(audio_path)
            except:
                pass

            self.action_button.title = "Start Recording"

        except Exception as e:
            print(f"Error: {e}")
            self.action_button.title = "Start Recording"
            rumps.alert(title="Error", message=f"Processing failed: {e}")

        finally:
            self.is_processing = False

    def _play_beep(self, sound_path):
        subprocess.Popen(['afplay', sound_path],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL)

    def _copy_to_clipboard(self, text):
        try:
            process = subprocess.Popen(['pbcopy'], stdin=subprocess.PIPE)
            process.communicate(str(text).encode('utf-8'))
        except Exception as e:
            print(f"Clipboard error: {e}")

    def cleanup(self):
        if self.recorder.is_recording():
            self.recorder.stop_recording()
        if self.hotkey_listener:
            self.hotkey_listener.stop()


def main():
    app = VoiceInputApp()

    def signal_handler(sig, frame):
        app.cleanup()
        os._exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        app.run()
    finally:
        app.cleanup()
        os._exit(0)


if __name__ == "__main__":
    main()
