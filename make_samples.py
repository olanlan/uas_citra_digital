"""Membuat 3 gambar uji sintetis (kertas berisi teks di atas meja).

Hanya untuk demo awal. Untuk laporan, sebaiknya pakai foto kertas asli
dari HP kamu sendiri dan simpan di folder images/.
"""
import cv2
import numpy as np

LINES = [
    "SURAT KETERANGAN",
    "Nama   : Olan Lastiant Afri",
    "Kampus : Universitas Pamulang",
    "Mata kuliah: Pengolahan Citra Digital",
    "Project UAS Document Scanner",
    "Tanggal: 12 Desember 2026",
]


def make_paper():
    paper = np.full((700, 500, 3), 250, np.uint8)
    for index, text in enumerate(LINES):
        scale = 0.9 if index == 0 else 0.6
        cv2.putText(paper, text, (30, 80 + index * 70),
                    cv2.FONT_HERSHEY_SIMPLEX, scale, (20, 20, 20), 2)
    return paper


def place_on_background(paper, background, corners, shadow=False):
    height, width = paper.shape[:2]
    source = np.float32([[0, 0], [width, 0], [width, height], [0, height]])
    matrix = cv2.getPerspectiveTransform(source, np.float32(corners))
    size = (background.shape[1], background.shape[0])
    warped = cv2.warpPerspective(paper, matrix, size)
    mask = cv2.warpPerspective(np.full(paper.shape[:2], 255, np.uint8),
                               matrix, size)
    output = background.copy()
    output[mask > 0] = warped[mask > 0]
    if shadow:  # gradasi gelap untuk simulasi pencahayaan tidak rata
        gradient = np.tile(np.linspace(1.0, 0.55, size[0]), (size[1], 1))
        output = (output * gradient[..., None]).astype(np.uint8)
    return output


def main():
    paper = make_paper()
    rng = np.random.default_rng(1)

    wood = np.full((900, 700, 3), (60, 100, 150), np.uint8)
    wood = cv2.add(wood, rng.integers(0, 25, wood.shape, dtype=np.uint8))
    scene1 = place_on_background(
        paper, wood, [[120, 100], [560, 140], [590, 780], [90, 740]])

    dark = np.full((900, 700, 3), (35, 35, 40), np.uint8)
    scene2 = place_on_background(
        paper, dark, [[200, 60], [650, 200], [520, 820], [60, 600]])

    gray_desk = np.full((900, 700, 3), (150, 150, 150), np.uint8)
    scene3 = place_on_background(
        paper, gray_desk, [[100, 120], [600, 110], [610, 790], [90, 800]],
        shadow=True)
    scene3 = cv2.add(scene3, rng.integers(0, 30, scene3.shape, dtype=np.uint8))

    cv2.imwrite("images/uji1_meja_kayu.jpg", scene1)
    cv2.imwrite("images/uji2_miring_gelap.jpg", scene2)
    cv2.imwrite("images/uji3_cahaya_tidak_rata.jpg", scene3)
    print("3 gambar uji dibuat di images/")


if __name__ == "__main__":
    main()
