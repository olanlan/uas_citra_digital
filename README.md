# Document Scanner

Project UAS Pengolahan Citra Digital, Universitas Pamulang.

Aplikasi mengubah foto kertas atau halaman buku yang miring dan berlatar berantakan menjadi
hasil scan hitam putih yang lurus dan rapi, seperti aplikasi CamScanner.

## Teknik pengolahan citra yang dipakai

| Tahap | Teknik | Fungsi OpenCV |
|---|---|---|
| 1 | Grayscale | `cvtColor` |
| 2 | Gaussian blur | `GaussianBlur` |
| 3 | Canny edge detection | `Canny` |
| 4 | Morfologi closing | `morphologyEx` |
| 5 | Segmentasi Otsu | `threshold` (Otsu) |
| 6 | Kontur + aproksimasi poligon | `findContours`, `approxPolyDP`, `minAreaRect` |
| 7 | Perspective transform | `getPerspectiveTransform`, `warpPerspective` |
| 8 | Adaptive threshold | `adaptiveThreshold` |

Alur: gambar -> perkecil -> grayscale -> blur -> Canny -> closing -> cari 4 sudut dokumen ->
perspective transform (pada gambar asli) -> adaptive threshold -> hasil scan.

Pencarian 4 sudut memakai beberapa strategi yang dicoba berurutan sampai ada yang berhasil:

1. Kontur 4 sudut dari tepi Canny.
2. Kontur 4 sudut dari mask Otsu.
3. Kotak minimum (`minAreaRect`) dari Canny, lalu dari Otsu.
4. Blok tepi dan teks (kotak diperlebar 8 persen), untuk kertas yang menyatu dengan latar.
5. Seluruh gambar dianggap dokumen (cadangan terakhir).

Strategi yang berhasil dicetak di terminal. Bila yang tercetak `seluruh gambar`, artinya tepi
dokumen tidak ditemukan.

## Instalasi

Butuh Python 3.9 atau lebih baru.

```bash
pip install -r requirements.txt
```

Di Windows, bila `pip` atau `python` tidak dikenali, pakai `py -m pip install -r requirements.txt`
dan `py src\main.py`.

Opsional memakai virtual environment:

```bash
python -m venv venv
# Linux/Mac:   source venv/bin/activate
# Windows:     venv\Scripts\activate
pip install -r requirements.txt
```

## Input yang diperlukan

Foto dokumen berformat JPG, JPEG, PNG, BMP, atau WEBP. Letakkan di folder `images/`, atau
pakai path file dari lokasi mana saja. Hasil terbaik bila dokumen berada di atas alas yang
kontras, seluruh tepinya terlihat, fokus tajam, dan cahaya tidak berlebihan.

## Cara menjalankan

Cara termudah: jalankan tanpa argumen, lalu pilih dari menu.

```bash
python src/main.py
```

Menu: 1 scan dari folder `images/`, 2 scan dari path sendiri (boleh drag-drop file),
3 scan semua gambar di `images/`, 0 keluar.

Atau lewat perintah langsung:

```bash
# Scan satu atau banyak gambar
python src/main.py --image images/01_ideal_lurus.jpeg

# Ganti folder output
python src/main.py --image images/01_ideal_lurus.jpeg --output hasil_baru
```

## Hasil

Setiap gambar disimpan ke folder `hasil/<nama gambar>/` dengan file bernomor sesuai urutan proses:

| File | Isi |
|---|---|
| `01_gray` | Grayscale |
| `02_blur` | Setelah Gaussian blur |
| `03_edges` | Tepi Canny |
| `04_closed` | Tepi setelah closing |
| `05_mask` | Mask Otsu |
| `06_blob` | Blok tepi dan teks |
| `07_outline` | Kotak hijau dokumen yang terdeteksi |
| `08_warped` | Dokumen setelah diluruskan |
| `09_scanned` | Hasil akhir hitam putih |

## Struktur folder

```
PROJECT_UAS/
├── README.md
├── requirements.txt
├── images/            foto uji
├── hasil/             hasil uji tiap foto
└── src/
    ├── main.py            alur utama, pemilihan strategi, CLI
    ├── preprocessing.py   grayscale, blur, Canny, closing, Otsu, blok tepi
    ├── detection.py       kontur, kotak minimum, perspective transform, binarisasi
    ├── menu.py            menu interaktif
    └── utils.py           pengurutan titik, perkecil gambar, simpan hasil
```

Project ini tidak memakai dataset eksternal maupun model pretrained.

## Parameter yang bisa diubah (untuk tanya jawab dosen)

| Parameter | File | Nilai | Dampak bila diubah |
|---|---|---|---|
| `BLUR_KERNEL` | preprocessing.py | 5x5 | Besar: noise hilang tapi tepi kertas ikut kabur |
| `CANNY_LOW`, `CANNY_HIGH` | preprocessing.py | 50, 150 | Rendah: banyak tepi palsu. Tinggi: tepi kertas bisa hilang |
| `MORPH_KERNEL` | preprocessing.py | 5x5 | Besar: garis putus tersambung, tapi objek lain bisa ikut menyatu |
| `MIN_AREA_RATIO` | detection.py | 0,10 | Batas luas minimum kontur yang dianggap dokumen |
| `THRESHOLD_BLOCK` | detection.py | 21 | Besar: tahan bayangan lebar, detail halus berkurang |
| `C_MAX`, `C_MIN`, `C_PER_CONTRAST` | detection.py | 10, 3, 0,2 | Konstanta threshold mengikuti kontras foto. C kecil: lebih banyak teks tertangkap, bintik noise bertambah |
| `PROCESS_HEIGHT` | main.py | 500 | Kecil: lebih cepat tapi tepi tipis bisa hilang |

## Hasil pengujian

Dari 9 foto uji (halaman buku, kamera ponsel), dokumen terdeteksi benar pada 7 foto.
Foto `05_rotasi_45` dan `09_latar_ramai` gagal, dan `03_terang_berlebih` berhasil sebagian.
Rincian ada di laporan BAB IV.

## Keterbatasan

- Gagal bila tepi dokumen tidak cukup kontras terhadap latar (kertas putih di meja terang,
  atau halaman yang diputar di atas alas berwarna mirip).
- Gagal bila sebagian sudut kertas tertutup atau keluar frame.
- Hanya mendeteksi satu dokumen berbentuk 4 sudut per foto.
- Foto terlalu terang atau kurang fokus membuat teks kecil tidak terbaca.
- Hasil tidak diputar otomatis. Bila dokumen menyamping di foto, teks tampak vertikal.

## Pengungkapan (sesuai ketentuan UAS)

- Library: OpenCV dan NumPy.
- Pendekatan document scanner (kontur 4 titik dan perspective transform) adalah teknik umum
  yang banyak dibahas di dokumentasi dan tutorial OpenCV.
- Bantuan AI: kode program dan dokumentasi dikembangkan dengan bantuan Claude (Anthropic).
  Penulis menjalankan, menguji, dan memahami seluruh kode.
- Seluruh foto uji diambil sendiri oleh penulis.