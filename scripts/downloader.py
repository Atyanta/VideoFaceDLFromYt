import os
import argparse
import multiprocessing as mp
from functools import partial
from tqdm import tqdm
from yt_dlp import YoutubeDL

def parse_line(line):
    """Ambil PersonName_YTKey dari line dengan format extended."""
    parts = line.strip().split('|')
    if not parts:
        return None
    identity = parts[0]
    return identity

def download_video(output_dir, line):
    """Download video berdasarkan format extended: PersonName_YTKey|..."""
    identity = parse_line(line)
    if not identity or '_' not in identity:
        print(f"[!] Skipped invalid format: {line}")
        return

    person_name, video_id = identity.rsplit('_', 1)
    output_filename = f"{person_name}_{video_id}.mp4"
    output_path = os.path.join(output_dir, output_filename)

    if os.path.exists(output_path):
        print(f"[✓] File already exists: {output_filename}")
        return

    url = f"https://www.youtube.com/watch?v={video_id}"
    ydl_opts = {
        'outtmpl': output_path.replace('.mp4', '.%(ext)s'),
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]',
        'merge_output_format': 'mp4',
        'quiet': True,
        'noplaylist': True,
        'postprocessors': [{'key': 'FFmpegMetadata'}]
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        print(f"[✓] Downloaded: {output_filename}")
    except Exception as e:
        print(f"[!] Failed to download {output_filename}: {e}")

def download_all_videos(input_list, output_dir, num_workers):
    with open(input_list, 'r') as f:
        lines = [line.strip() for line in f if line.strip()]

    os.makedirs(output_dir, exist_ok=True)
    downloader = partial(download_video, output_dir)

    with mp.Pool(num_workers) as pool:
        list(tqdm(pool.imap_unordered(downloader, lines), total=len(lines)))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_list', type=str, required=True, help='Path to file with YouTube video IDs')
    parser.add_argument('--output_dir', type=str, default='data/youtube_videos', help='Directory to save videos')
    parser.add_argument('--num_workers', type=int, default=4, help='Number of parallel download workers')
    args = parser.parse_args()

    download_all_videos(args.input_list, args.output_dir, args.num_workers)
