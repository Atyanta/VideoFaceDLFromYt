# scripts/face_cropper.py
import os
import cv2
import ffmpeg
import pandas as pd
from tqdm import tqdm
import mediapipe as mp
import datetime

def parse_video_entry(entry):
    """Parses a line of format: Name_YTKey|start|duration|gender|age|racial|country"""
    parts = entry.strip().split('|')
    if len(parts) != 7:
        raise ValueError(f"Invalid format: {entry}")

    identity, start_time, duration, gender, age, racial, country = parts
    if '_' not in identity:
        raise ValueError(f"Invalid identity format: {identity}")
    person_name, video_id = identity.rsplit('_', 1)

    return {
        'person_name': person_name,
        'video_id': video_id,
        'start_time': start_time,
        'duration': int(duration),
        'gender': gender,
        'age': age,
        'racial': racial,
        'country': country
    }

def hms_to_seconds(hms_str):
    """Convert HH:MM:SS string to seconds"""
    t = datetime.datetime.strptime(hms_str, "%H:%M:%S")
    return t.hour * 3600 + t.minute * 60 + t.second

def process_all_videos(video_list_path, temp_dir, output_dir, metadata_path,
                       min_confidence=0.9, show_preview=False):

    mp_face_detection = mp.solutions.face_detection
    detector = mp_face_detection.FaceDetection(model_selection=0, min_detection_confidence=min_confidence)

    metadata_rows = []

    with open(video_list_path, 'r') as f:
        video_entries = [parse_video_entry(line) for line in f if line.strip()]

    for entry in tqdm(video_entries):
        try:
            filename = f"{entry['person_name']}_{entry['video_id']}.mp4"
            input_path = os.path.join(temp_dir, filename)
            person_folder = os.path.join(output_dir, entry['person_name'])
            os.makedirs(person_folder, exist_ok=True)

            result = process_single_video(
                input_path,
                person_folder,
                entry,
                detector,
                min_confidence,
                show_preview
            )

            if result:
                metadata_rows.append(result)

            os.remove(input_path)

        except Exception as e:
            print(f"[!] Error processing {entry['video_id']}: {e}")

    # Simpan metadata
    if metadata_rows:
        df = pd.DataFrame(metadata_rows)
        df.to_csv(metadata_path, mode='a', index=False, header=False)

def process_single_video(video_path, output_dir, entry, detector,
                         min_confidence=0.9, show_preview=False):

    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    start_time_sec = hms_to_seconds(entry['start_time'])
    start_frame = int(start_time_sec * fps)
    duration_frames = int(entry['duration'] * fps)
    end_frame = start_frame + duration_frames

    frames = []
    boxes = []
    frame_idx = 0

    while True:
        ret, frame = cap.read()
        if not ret or frame_idx > end_frame:
            break

        if frame_idx >= start_frame:
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = detector.process(rgb)

            if results.detections:
                best_detection = max(results.detections, key=lambda d: d.score[0])
                if best_detection.score[0] >= min_confidence:
                    box_data = best_detection.location_data.relative_bounding_box
                    x_min = int(box_data.xmin * width)
                    y_min = int(box_data.ymin * height)
                    w = int(box_data.width * width)
                    h = int(box_data.height * height)

                    l = max(0, x_min - int(w * 0.2))
                    t = max(0, y_min - int(h * 0.2))
                    r = min(width, x_min + w + int(w * 0.2))
                    b = min(height, y_min + h + int(h * 0.2))

                    frames.append(frame_idx)
                    boxes.append((l, t, r, b))

                    if show_preview:
                        preview = frame.copy()
                        cv2.rectangle(preview, (l, t), (r, b), (0, 255, 0), 2)
                        cv2.imshow("Face Detection", preview)
                        if cv2.waitKey(1) & 0xFF == ord('q'):
                            break

        frame_idx += 1

    cap.release()
    cv2.destroyAllWindows()

    if not frames:
        return None

    # Ambil deteksi awal untuk crop
    crop_l, crop_t, crop_r, crop_b = boxes[0]
    crop_w = crop_r - crop_l
    crop_h = crop_b - crop_t

    output_filename = f"{entry['video_id']}_cropped.mp4"
    output_path = os.path.join(output_dir, output_filename)

    try:
        input_stream = ffmpeg.input(video_path, ss=start_time_sec, t=entry['duration'])
        video = input_stream.video \
            .filter('crop', x=crop_l, y=crop_t, out_w=crop_w, out_h=crop_h) \
            .filter('scale', 'if(gt(iw,ih),300,-1)', 'if(gt(iw,ih),-1,300)')
        audio = input_stream.audio

        ffmpeg.output(video, audio, output_path, vcodec='libx264', acodec='aac', strict='experimental') \
            .overwrite_output() \
            .run(quiet=True)

    except ffmpeg.Error as e:
        print(f"[!] ffmpeg error in {entry['video_id']}: {e}")
        return None

    return {
        'video_id': entry['video_id'],
        'person_name': entry['person_name'],
        'height': height,
        'width': width,
        'start_frame': start_frame,
        'end_frame': end_frame,
        'left': crop_l,
        'top': crop_t,
        'right': crop_r,
        'bottom': crop_b,
        'gender': entry['gender'],
        'country': entry['country'],
        'racial': entry['racial'],
        'age': entry['age']
    }
