"""Tahap preprocessing: grayscale, blur, deteksi tepi, morfologi."""
import cv2
import numpy as np

# Parameter yang bisa diubah saat ujian (dampaknya dijelaskan di README)
BLUR_KERNEL = (5, 5)
CANNY_LOW = 50
CANNY_HIGH = 150
MORPH_KERNEL = (5, 5)


def convert_to_grayscale(image):
    """Ubah BGR ke grayscale supaya proses lanjutan cukup 1 kanal."""
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


def blur_image(gray_image, kernel_size=BLUR_KERNEL):
    """Gaussian blur untuk meredam noise sebelum deteksi tepi."""
    return cv2.GaussianBlur(gray_image, kernel_size, 0)


def detect_edges(blurred_image, low=CANNY_LOW, high=CANNY_HIGH):
    """Canny edge detection untuk mencari batas kertas."""
    return cv2.Canny(blurred_image, low, high)


def close_edges(edge_image, kernel_size=MORPH_KERNEL):
    """Operasi morfologi closing: dilasi lalu erosi.

    Fungsinya menyambung garis tepi yang putus supaya kontur kertas
    menjadi satu bentuk tertutup.
    """
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, kernel_size)
    return cv2.morphologyEx(edge_image, cv2.MORPH_CLOSE, kernel, iterations=2)


def segment_paper(blurred_image):
    """Segmentasi kertas terang dari latar dengan threshold Otsu.

    Cadangan bila Canny gagal: kertas biasanya lebih terang dari meja,
    jadi Otsu memisahkan keduanya tanpa perlu menebak batas threshold.
    Closing dipakai untuk menutup lubang akibat teks di atas kertas.
    """
    _, mask = cv2.threshold(
        blurred_image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 15))
    return cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)


def merge_edges_to_blob(edge_image, kernel_size=(25, 25)):
    """Closing dengan kernel besar: tepi dan teks menyatu menjadi satu blok.

    Cadangan untuk kertas putih di atas meja putih, ketika tepi kertas
    tidak terlihat tetapi teks di dalamnya menandai lokasi dokumen.
    """
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, kernel_size)
    return cv2.morphologyEx(edge_image, cv2.MORPH_CLOSE, kernel, iterations=2)


def preprocess(image):
    """Jalankan seluruh preprocessing dan kembalikan tiap tahapnya."""
    gray_image = convert_to_grayscale(image)
    blurred_image = blur_image(gray_image)
    edge_image = detect_edges(blurred_image)
    closed_image = close_edges(edge_image)
    mask_image = segment_paper(blurred_image)
    blob_image = merge_edges_to_blob(edge_image)
    return {
        "gray": gray_image,
        "blur": blurred_image,
        "edges": edge_image,
        "closed": closed_image,
        "mask": mask_image,
        "blob": blob_image,
    }