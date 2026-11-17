"""Document Scanner: foto kertas miring menjadi hasil scan yang lurus dan rapi.

Contoh:
    python src/main.py                              (menu interaktif)
    python src/main.py --image images/uji1_meja_kayu.jpg
"""
import argparse
import os
import sys

import cv2

from detection import (binarize_document, draw_document_outline,
                       find_document_by_rectangle, find_document_contour,
                       four_point_transform, full_image_points)
from menu import run_menu
from preprocessing import preprocess
from utils import resize_keep_ratio, save_image

PROCESS_HEIGHT = 500  # deteksi dilakukan di gambar kecil agar cepat

# Folder dihitung dari lokasi file ini, jadi program bisa dijalankan dari mana saja
PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMAGES_DIR = os.path.join(PROJECT_DIR, "images")
OUTPUT_DIR = os.path.join(PROJECT_DIR, "hasil")


def locate_document(steps, small_image):
    """Cari dokumen dengan beberapa strategi, dari yang paling akurat.

    Mengembalikan (4 titik, nama metode yang berhasil).
    """
    sources = (("tepi Canny", steps["closed"]), ("segmentasi Otsu", steps["mask"]))

    for source_name, binary_image in sources:
        points = find_document_contour(binary_image)
        if points is not None:
            return points, f"kontur 4 sudut ({source_name})"

    for source_name, binary_image in sources:
        points = find_document_by_rectangle(binary_image)
        if points is not None:
            return points, f"kotak minimum ({source_name})"

    # Kertas putih di meja putih: tandai lokasi lewat blok teks/tepi
    points = find_document_by_rectangle(steps["blob"], min_area_ratio=0.03,
                                        pad_ratio=0.08)
    if points is not None:
        return points, "blok teks/tepi (kertas menyatu dengan latar)"

    return full_image_points(small_image), "seluruh gambar (tepi kertas tidak terdeteksi)"


def scan_image(image):
    """Pipeline lengkap. Mengembalikan (dict hasil tiap tahap, nama metode)."""
    small_image, scale = resize_keep_ratio(image, PROCESS_HEIGHT)
    steps = preprocess(small_image)
    points, method = locate_document(steps, small_image)

    # Kembalikan titik ke ukuran gambar asli supaya hasil tetap tajam
    points_original = points.reshape(4, 2) / scale
    warped_image = four_point_transform(image, points_original)
    scanned_image = binarize_document(warped_image)

    steps["outline"] = draw_document_outline(small_image, points)
    steps["warped"] = warped_image
    steps["scanned"] = scanned_image
    return steps, method


def save_steps(steps, output_dir, name):
    """Simpan semua tahap proses ke folder hasil/<nama gambar>/.

    Nama file diberi nomor urut (01_gray.jpg, 02_blur.jpg, ...) supaya
    mudah dipakai sebagai tangkapan layar di laporan.
    """
    image_folder = os.path.join(output_dir, name)
    for number, (key, image) in enumerate(steps.items(), start=1):
        save_image(os.path.join(image_folder, f"{number:02d}_{key}.jpg"), image)


def run_on_image(path, output_dir):
    image = cv2.imread(path)
    if image is None:
        print(f"[ERROR] Gambar tidak bisa dibuka: {path}")
        return False

    steps, method = scan_image(image)
    name = os.path.splitext(os.path.basename(path))[0]
    save_steps(steps, output_dir, name)
    outline_number = list(steps).index("outline") + 1

    print(f"[OK] {name}: metode = {method}")
    print(f"     hasil disimpan di {os.path.join(output_dir, name)}")
    print(f"     Cek {outline_number:02d}_outline.jpg. Bila kotak hijau tidak pas "
          "dengan dokumen, foto ulang dengan latar yang lebih kontras.")
    return True


def parse_arguments():
    parser = argparse.ArgumentParser(description="Document Scanner")
    parser.add_argument("--image", nargs="+", help="satu atau lebih file gambar")
    parser.add_argument("--output", default=OUTPUT_DIR, help="folder output")
    return parser.parse_args()


def main():
    args = parse_arguments()
    if args.image:
        results = [run_on_image(p, args.output) for p in args.image]
        sys.exit(0 if all(results) else 1)
    else:
        run_menu(IMAGES_DIR, args.output, run_on_image)


if __name__ == "__main__":
    main()