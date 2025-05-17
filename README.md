# Video Face Cropper & Dataset Pipeline from Youtube

## Deskripsi

Program ini bertujuan untuk membuat dataset video wajah dari kumpulan video YouTube. Pipeline ini melakukan beberapa proses utama:

1. **Download video YouTube** berdasarkan daftar video yang diberikan.
2. **Memotong video** berdasarkan waktu mulai dan durasi yang diatur pada file `video_ids.txt`.
3. **Mendeteksi wajah** menggunakan MediaPipe Face Detection.
4. **Meng-crop wajah** pada frame yang terdeteksi dan membuat potongan video pendek yang fokus pada wajah tersebut.
5. **Menyimpan metadata** hasil deteksi dan pemotongan dalam format CSV.

---

## Struktur Folder

project_root/
│
├── data/ # (Optional) Bisa digunakan untuk menyimpan data mentah tambahan
│
├── output/ # Folder hasil output video yang sudah dipotong dan metadata
│ ├── <person_name>/ # Folder per orang berisi video crop wajah milik orang tersebut
│ └── metadata.csv # File CSV berisi metadata wajah (posisi, ukuran, atribut tambahan)
│
├── scripts/ # Folder berisi semua script utama program
│ ├── downloader.py # Modul untuk download video dari YouTube
│ ├── face_cropper.py # Modul untuk mendeteksi dan crop wajah dari video
│ └── main_pipeline.py # Script utama pipeline yang menjalankan keseluruhan proses
│
├── video_ids.txt # File berisi daftar video YouTube dan metadata terkait:
│ # Format: person_name, video_id, start_time, duration, gender, country, racial, age
│
├── requirements.txt # File daftar library yang harus diinstall
└── README.md # Dokumentasi ini


---

## Cara Menggunakan

### 1. Siapkan file `video_ids.txt`

Format tiap baris file ini harus seperti berikut (dipisahkan dengan spasi atau tab):
<person_name> <video_id> <start_time> <duration_in_seconds> <gender> <country> <racial> <age>

Contoh:
john_doe dQw4w9WgXcQ 00:01:00 10 male USA caucasian 30
jane_smith xYzAbc12345 00:02:30 15 female UK asian 25

### 2. Jalankan pipeline utama
Jalankan script main_pipeline.py dari terminal di folder project root:

python scripts/main_pipeline.py --num_workers 4 --min_confidence 0.8 --show_preview
--num_workers: jumlah proses paralel untuk download video (default 4)

--min_confidence: threshold confidence untuk deteksi wajah (default 0.8)

--show_preview: tampilkan preview deteksi wajah (opsional)

### 3. Output
Setelah selesai, folder output/ akan berisi:

Subfolder per orang (sesuai nama di video_ids.txt) yang berisi video crop wajah pendek hasil pemrosesan.

File metadata.csv yang berisi detail metadata tiap video crop (posisi wajah, atribut gender, umur, dll).

### Catatan
Video asli akan disimpan sementara di folder temp_downloads/ selama proses berlangsung dan otomatis dihapus setelah selesai.

Pastikan koneksi internet stabil saat proses download YouTube.

Jika ingin mengubah durasi crop atau pengaturan lain, sesuaikan file video_ids.txt dan parameter saat menjalankan pipeline.
