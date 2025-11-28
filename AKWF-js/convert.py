#!/usr/bin/env python3
"""
Convert AKWF WAV files to JSON format for web player.
Reads 600-sample, 16-bit mono WAV files and outputs normalized float arrays.
Skips any stereo files.

Usage: python3 convert.py [path-to-AKWF-directory]

Adventure Kid Waveforms(AKWF) Open waveforms library
https://www.adventurekid.se/akrt/waveforms/adventure-kid-waveforms/

"""

import wave
import struct
import json
import sys
from pathlib import Path


def read_wav(filepath):
    """Read WAV file and return normalized float samples (-1.0 to 1.0).
    Returns None for stereo files (skipped)."""
    with wave.open(str(filepath), 'rb') as wav:
        n_channels = wav.getnchannels()
        if n_channels != 1:
            return None  # Skip stereo files

        n_frames = wav.getnframes()
        raw_data = wav.readframes(n_frames)

        # 16-bit signed PCM, little-endian
        samples = struct.unpack(f'<{n_frames}h', raw_data)

        # Normalize to -1.0 to 1.0, round to 6 decimal places
        return [round(s / 32768.0, 6) for s in samples]


def process_bank(bank_dir, output_dir):
    """Process all WAV files in a bank directory."""
    bank_name = bank_dir.name
    waveforms = {}

    for wav_file in sorted(bank_dir.glob('*.wav')):
        name = wav_file.stem  # filename without extension
        samples = read_wav(wav_file)
        if samples is not None:
            waveforms[name] = samples

    if waveforms:
        output_file = output_dir / f'{bank_name}.json'
        with open(output_file, 'w') as f:
            json.dump(waveforms, f)
        print(f'Processed {bank_name}: {len(waveforms)} waveforms')

    return bank_name if waveforms else None


def main():
    work_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('.')
    output_dir = Path(__file__).parent

    if not work_dir.is_dir():
        print(f'Error: Directory {work_dir} not found', file=sys.stderr)
        sys.exit(1)

    bank_dirs = sorted(work_dir.glob('AKWF_*'))
    if not bank_dirs:
        print(f'Error: No AKWF_* directories found in {work_dir}', file=sys.stderr)
        sys.exit(1)

    bank_names = []
    for bank_dir in bank_dirs:
        if bank_dir.is_dir():
            name = process_bank(bank_dir, output_dir)
            if name:
                bank_names.append(name)

    # Generate manifest
    manifest = {'banks': bank_names}
    with open(output_dir / 'manifest.json', 'w') as f:
        json.dump(manifest, f, indent=2)

    print(f'Generated {len(bank_names)} bank files and manifest.json')


if __name__ == '__main__':
    main()
