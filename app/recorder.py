#!/usr/bin/env python3
"""
Audio recording module
"""

import sounddevice as sd
import numpy as np
from scipy.io import wavfile
import tempfile
import threading
import time


class AudioRecorder:
    def __init__(self, sample_rate=16000):
        self.sample_rate = sample_rate
        self.recording = False
        self.audio_data = []
        self.stream = None
        self.record_thread = None

    def start_recording(self):
        if self.recording:
            return False

        self.recording = True
        self.audio_data = []
        self.record_thread = threading.Thread(target=self._record, daemon=True)
        self.record_thread.start()

        return True

    def _record(self):
        def callback(indata, frames, time_info, status):
            if self.recording:
                self.audio_data.append(indata.copy())

        try:
            self.stream = sd.InputStream(
                samplerate=self.sample_rate,
                channels=1,
                dtype='int16',
                callback=callback
            )
            self.stream.start()

            while self.recording:
                time.sleep(0.1)

            self.stream.stop()
            self.stream.close()
            self.stream = None

        except Exception as e:
            print(f"Recording error: {e}")
            self.recording = False
            if self.stream:
                try:
                    self.stream.stop()
                    self.stream.close()
                except:
                    pass
                self.stream = None

    def stop_recording(self):
        if not self.recording:
            return None

        self.recording = False

        if self.record_thread:
            self.record_thread.join(timeout=3.0)

        if not self.audio_data:
            return None

        audio = np.concatenate(self.audio_data, axis=0)

        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
            tmp_path = tmp.name
            wavfile.write(tmp_path, self.sample_rate, audio)

        return tmp_path

    def is_recording(self):
        return self.recording
