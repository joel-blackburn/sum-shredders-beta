#!/usr/bin/env python3
"""Turn a voice-pack zip from studio.html into game-ready clips.

Usage:  python3 tools/process_voice.py path/to/sum-shredders-voice-YYYY-MM-DD.zip

For every clip: high-pass (remove rumble), trim silence at both ends, level to a
consistent loudness (peaks capped), then save as mono 44.1 kHz MP3 in voice/.
Clips already in voice/ that are not in the zip are kept, so packs can arrive in batches.
voice/index.json lists every clip the game may use.
"""
import json, os, re, subprocess, sys, tempfile, time, zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'voice')
TARGET_MEAN = -19.0   # dB mean volume
PEAK_CAP = -1.5       # dB max peak
ID_RE = re.compile(r'^[a-z0-9_]{1,40}$')

def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)

def volume(path):
    r = run(['ffmpeg', '-hide_banner', '-i', path, '-af', 'volumedetect', '-f', 'null', '-'])
    mean = re.search(r'mean_volume: (-?[\d.]+) dB', r.stderr)
    peak = re.search(r'max_volume: (-?[\d.]+) dB', r.stderr)
    return (float(mean.group(1)) if mean else None, float(peak.group(1)) if peak else None)

TRIM = ('highpass=f=80,'
        'silenceremove=start_periods=1:start_threshold=-42dB:start_silence=0.03:detection=peak,'
        'areverse,'
        'silenceremove=start_periods=1:start_threshold=-42dB:start_silence=0.06:detection=peak,'
        'areverse')

def process(src, dst, tmp):
    mid = os.path.join(tmp, 'mid.wav')
    r = run(['ffmpeg', '-hide_banner', '-y', '-i', src, '-af', TRIM, '-ac', '1', '-ar', '44100', mid])
    if r.returncode or not os.path.exists(mid) or os.path.getsize(mid) < 2000:
        return 'empty after trimming (silent or too quiet?)'
    mean, peak = volume(mid)
    if mean is None or mean < -60:
        return 'too quiet'
    gain = min(TARGET_MEAN - mean, PEAK_CAP - peak)
    af = f'volume={gain:.2f}dB,adelay=15|15,apad=pad_dur=0.04'
    r = run(['ffmpeg', '-hide_banner', '-y', '-i', mid, '-af', af, '-ac', '1', '-ar', '44100',
             '-codec:a', 'libmp3lame', '-b:a', '64k', dst])
    if r.returncode:
        return 'encode failed: ' + r.stderr[-200:]
    return None

def main(zpath):
    os.makedirs(OUT, exist_ok=True)
    done, problems = [], []
    with tempfile.TemporaryDirectory() as tmp, zipfile.ZipFile(zpath) as z:
        man = json.loads(z.read('manifest.json'))
        for c in man.get('clips', []):
            cid, f = c.get('id', ''), c.get('file', '')
            if not ID_RE.match(cid) or '/' in f or '..' in f:
                problems.append((cid or '?', 'bad name, skipped')); continue
            src = os.path.join(tmp, 'in_' + os.path.basename(f))
            with open(src, 'wb') as fh:
                fh.write(z.read(f))
            err = process(src, os.path.join(OUT, cid + '.mp3'), tmp)
            (problems.append((cid, err)) if err else done.append(cid))
    have = sorted(f[:-4] for f in os.listdir(OUT) if f.endswith('.mp3'))
    with open(os.path.join(OUT, 'index.json'), 'w') as fh:
        json.dump({'v': time.strftime('%Y%m%d%H%M'), 'clips': have}, fh, indent=0)
    print(f'processed {len(done)} clips, {len(have)} total in voice/')
    for cid, err in problems:
        print(f'  ! {cid}: {err}')

if __name__ == '__main__':
    main(sys.argv[1])
