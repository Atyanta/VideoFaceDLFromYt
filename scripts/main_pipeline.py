import os
import csv
import shutil
import argparse
from downloader import download_all_videos
from face_cropper import process_all_videos  # Fungsi ini nanti sudah diperbarui

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(PROJECT_ROOT, '..'))  
VIDEO_LIST_PATH = os.path.join(PROJECT_ROOT, 'video_ids.txt')
TEMP_DIR = os.path.join(PROJECT_ROOT, 'temp_downloads')
OUTPUT_DIR = os.path.join(PROJECT_ROOT, 'output')
METADATA_FILE = os.path.join(OUTPUT_DIR, 'metadata.csv')

os.makedirs(TEMP_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

def initialize_metadata_csv(path):
    if not os.path.exists(path):
        with open(path, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([
                'video_id', 'person_name', 'height', 'width', 'start_frame',
                'end_frame', 'left', 'top', 'right', 'bottom',
                'gender', 'country', 'racial', 'age'
            ])

def read_video_list_with_metadata(file_path):
    """Baca file video_ids.txt dan parsing semua metadata per video"""
    videos = []
    with open(file_path, 'r') as f:
        for line in f:
            if not line.strip():
                continue
            parts = line.strip().split('|')
            if len(parts) < 7:
                print(f"[!] Warning: Format baris kurang lengkap: {line}")
                continue
            identity = parts[0]
            start_time = parts[1]
            duration = float(parts[2])
            gender = parts[3]
            age = parts[4]
            racial = parts[5]
            country = parts[6]

            if '_' not in identity:
                print(f"[!] Warning: Format identity salah: {identity}")
                continue
            person_name, video_id = identity.rsplit('_', 1)

            videos.append({
                'person_name': person_name,
                'video_id': video_id,
                'start_time': start_time,
                'duration': duration,
                'gender': gender,
                'age': age,
                'racial': racial,
                'country': country,
                'identity': identity
            })
    return videos

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--num_workers', type=int, default=4, help='Number of threads for download')
    parser.add_argument('--min_confidence', type=float, default=0.8, help='Minimum face detection confidence')
    parser.add_argument('--show_preview', action='store_true', help='Show detection preview (press Q to quit)')
    args = parser.parse_args()

    print("[✓] Initializing metadata CSV...")
    initialize_metadata_csv(METADATA_FILE)

    print("[1/3] Reading video list and metadata...")
    videos = read_video_list_with_metadata(VIDEO_LIST_PATH)

    # Buat temporary list file untuk download (hanya identity, agar kompatibel dengan downloader)
    temp_video_list_path = os.path.join(TEMP_DIR, 'download_list.txt')
    with open(temp_video_list_path, 'w') as f:
        for v in videos:
            f.write(v['identity'] + '\n')

    print("[2/3] Downloading YouTube videos...")
    download_all_videos(temp_video_list_path, TEMP_DIR, args.num_workers)

    print("[3/3] Detecting faces, cropping, and cutting clips...")
    process_all_videos(
        video_list_path=VIDEO_LIST_PATH,
        temp_dir=TEMP_DIR,
        output_dir=OUTPUT_DIR,
        metadata_path=METADATA_FILE,
        min_confidence=args.min_confidence,
        show_preview=args.show_preview
    )


    print("[4/4] Cleaning up temporary files...")
    shutil.rmtree(TEMP_DIR, ignore_errors=True)

    print("✅ Dataset pipeline completed successfully.")
