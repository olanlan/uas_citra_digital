"""Fungsi bantu umum: urutan titik, resize, dan penyimpanan hasil."""
import os

import cv2
import numpy as np


def order_points(points):
    """Urutkan 4 titik menjadi: kiri-atas, kanan-atas, kanan-bawah, kiri-bawah.

    Trik: titik kiri-atas punya jumlah (x+y) terkecil, kanan-bawah terbesar.
    Titik kanan-atas punya selisih (y-x) terkecil, kiri-bawah terbesar.
    """
    points = points.reshape(4, 2).astype("float32")
    ordered = np.zeros((4, 2), dtype="float32")

    sums = points.sum(axis=1)
    ordered[0] = points[np.argmin(sums)]
    ordered[2] = points[np.argmax(sums)]

    diffs = np.diff(points, axis=1)
    ordered[1] = points[np.argmin(diffs)]
    ordered[3] = points[np.argmax(diffs)]
    return ordered


def resize_keep_ratio(image, target_height):
    """Perkecil gambar ke tinggi tertentu tanpa merusak rasio.

    Mengembalikan gambar baru dan faktor skala (untuk memetakan titik
    kembali ke gambar asli).
    """
    height, width = image.shape[:2]
    scale = target_height / float(height)
    resized = cv2.resize(image, (int(width * scale), target_height))
    return resized, scale


def save_image(path, image):
    """Simpan gambar dan buat folder tujuan bila belum ada."""
    folder = os.path.dirname(path)
    if folder:
        os.makedirs(folder, exist_ok=True)
    cv2.imwrite(path, image)
