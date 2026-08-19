import subprocess
import json
import os
import glob
import sys
import pandas as pd

def probe_file(filepath):
    """Run ffprobe on a single file and return JSON data."""
    cmd = [
        "ffprobe",
        "-v", "quiet",
        "-print_format", "json",
        "-show_format",
        "-select_streams", "v:0",
        "-show_streams",
        filepath
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error probing {filepath}: {result.stderr}")
        return None
    return json.loads(result.stdout)

def extract_codec_info(filepath, probe_data):
    """Pull out codec info per stream."""
    info = {"file": filepath}
    if not probe_data:
        return info

    for stream in probe_data.get("streams", []):
        info.update({
            "codec_name": stream.get("codec_name"),
            "codec_long_name": stream.get("codec_long_name"),
            "width": stream.get("width"),
            "height": stream.get("height"),
            "max_frame_rate": stream.get("r_frame_rate"),
            "avg_frame_rate": stream.get("avg_frame_rate"),
        })
    return info

def gather_codec_report(directory, extensions=("*.mp4", "*.mov", "*.mkv", "*.avi", "*.mp3", "*.wav")):
    filepaths = []
    for ext in extensions:
        filepaths.extend(glob.glob(os.path.join(directory, "**", ext), recursive=True))

    report = []
    for filepath in filepaths:
        probe_data = probe_file(filepath)
        report.append(extract_codec_info(filepath, probe_data))

    return report

def save_report(report, output_path="codec_report.json"):
    with open(output_path, "w") as report_file:
        json.dump(report, report_file, indent=2)

if __name__ == "__main__":
    target_directory = sys.argv[1] #"/mnt/d/Mike/Videos/Movies"  # change this to your folder
    codec_report = gather_codec_report(target_directory)
    df = pd.DataFrame(codec_report)
    df.to_excel(target_directory + '/codecs.xlsx')
    save_report(codec_report)
