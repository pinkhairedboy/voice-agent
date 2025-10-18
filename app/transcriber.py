#!/usr/bin/env python3
"""
Transcription module using Parakeet TDT v3
"""

import os
os.environ['NEMO_LOG_LEVEL'] = 'CRITICAL'
os.environ['HYDRA_FULL_ERROR'] = '0'
os.environ['PYTHONWARNINGS'] = 'ignore'

import sys
from io import StringIO

import warnings
warnings.filterwarnings('ignore')

import logging
logging.basicConfig(level=logging.CRITICAL)
for logger_name in ['nemo_logger', 'nemo', 'pytorch_lightning', 'pytorch_lightning.utilities',
                     'lightning', 'lightning.pytorch']:
    logging.getLogger(logger_name).setLevel(logging.CRITICAL)

import torch
import nemo.collections.asr as nemo_asr


class Transcriber:
    def __init__(self):
        self.model = None
        self.device = None

    def load_model(self):
        print("Loading Parakeet TDT v3...")

        old_stdout_fd = os.dup(1)
        old_stderr_fd = os.dup(2)
        devnull_fd = os.open(os.devnull, os.O_WRONLY)

        try:
            os.dup2(devnull_fd, 1)
            os.dup2(devnull_fd, 2)

            self.model = nemo_asr.models.ASRModel.from_pretrained(
                "nvidia/parakeet-tdt-0.6b-v3"
            )

            if torch.backends.mps.is_available():
                self.device = 'mps'
            else:
                self.device = 'cpu'

            try:
                self.model = self.model.to(self.device)
            except:
                self.device = 'cpu'
                self.model = self.model.to('cpu')
        finally:
            os.dup2(old_stdout_fd, 1)
            os.dup2(old_stderr_fd, 2)
            os.close(devnull_fd)
            os.close(old_stdout_fd)
            os.close(old_stderr_fd)

        print(f"Ready! Press Ctrl+Q to start/stop recording (using {self.device.upper()})")

    def transcribe(self, audio_path):
        if self.model is None:
            raise RuntimeError("Model not loaded")

        old_stdout_fd = os.dup(1)
        old_stderr_fd = os.dup(2)
        devnull_fd = os.open(os.devnull, os.O_WRONLY)

        try:
            os.dup2(devnull_fd, 1)
            os.dup2(devnull_fd, 2)

            result = self.model.transcribe([audio_path], verbose=False, batch_size=1)
        finally:
            os.dup2(old_stdout_fd, 1)
            os.dup2(old_stderr_fd, 2)
            os.close(devnull_fd)
            os.close(old_stdout_fd)
            os.close(old_stderr_fd)

        if isinstance(result, list) and len(result) > 0:
            first_result = result[0]
            if hasattr(first_result, 'text'):
                return first_result.text
            else:
                return str(first_result)
        else:
            return str(result)

    def is_ready(self):
        return self.model is not None
