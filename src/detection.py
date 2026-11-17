"""Deteksi dokumen: contour, perspective transform, dan binarisasi."""
import cv2
import numpy as np

from utils import order_points

MIN_AREA_RATIO = 0.10  # dokumen minimal 10% dari luas gambar
EPSILON_RATIOS = (0.02, 0.03, 0.04, 0.05)  # toleransi penyederhanaan kontur

# Parameter adaptive threshold (bisa diubah saat ujian)
THRESHOLD_BLOCK = 21   # ukuran jendela lokal, harus ganjil
C_MAX = 10             # konstanta pengurang untuk foto kontras normal
C_MIN = 3              # batas bawah untuk foto kontras rendah
C_PER_CONTRAST = 0.2   # C = kontras x 0,2, lalu dibatasi C_MIN sampai C_MAX


def find_document_contour(closed_image):
    """Cari kontur 4 sudut terbesar yang dianggap sebagai kertas.

    Langkah: findContours, urutkan dari luas terbesar, lalu
    approxPolyDP untuk menyederhanakan bentuk. Kontur pertama yang
    punya 4 titik dan cukup luas dipilih.
    Mengembalikan array 4 titik, atau None bila tidak ditemukan.
    """
    contours, _ = cv2.findContours(
        closed_image, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE
    )
    contours = sorted(contours, key=cv2.contourArea, reverse=True)
    min_area = MIN_AREA_RATIO * closed_image.shape[0] * closed_image.shape[1]

    for contour in contours[:10]:
        if cv2.contourArea(contour) < min_area:
            break
        if touches_border(contour, closed_image.shape):
            continue
        perimeter = cv2.arcLength(contour, True)
        # Coba beberapa toleransi: sudut melengkung butuh toleransi lebih besar
        for epsilon_ratio in EPSILON_RATIOS:
            approx = cv2.approxPolyDP(contour, epsilon_ratio * perimeter, True)
            if len(approx) == 4:
                return approx
    return None


def touches_border(contour, image_shape, margin=3):
    """True bila kontur menempel ke tepi foto di 2 sisi atau lebih.

    Kontur seperti itu biasanya latar (meja), bukan dokumen.
    """
    x, y, width, height = cv2.boundingRect(contour)
    image_height, image_width = image_shape[:2]
    sides = [
        x <= margin,
        y <= margin,
        x + width >= image_width - margin,
        y + height >= image_height - margin,
    ]
    return sum(sides) >= 2


def find_document_by_rectangle(binary_image, min_area_ratio=MIN_AREA_RATIO,
                               pad_ratio=0.0):
    """Cadangan: bungkus kontur terbesar dengan persegi panjang miring.

    Dipakai bila kontur tidak bisa disederhanakan menjadi 4 titik
    (misalnya struk dengan sudut melengkung, atau tepi kertas samar).
    pad_ratio memperlebar kotak sedikit, berguna bila kotak hanya
    membungkus area teks dan bukan seluruh kertas.
    """
    contours, _ = cv2.findContours(
        binary_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )
    contours = sorted(contours, key=cv2.contourArea, reverse=True)
    min_area = min_area_ratio * binary_image.shape[0] * binary_image.shape[1]

    for contour in contours[:10]:
        if cv2.contourArea(contour) < min_area:
            break
        if touches_border(contour, binary_image.shape):
            continue
        (center_x, center_y), (width, height), angle = cv2.minAreaRect(contour)
        scale = 1.0 + pad_ratio
        box = cv2.boxPoints(((center_x, center_y),
                             (width * scale, height * scale), angle))
        return box.astype(np.int32).reshape(4, 1, 2)
    return None


def full_image_points(image):
    """Cadangan terakhir: seluruh gambar dianggap dokumen.

    Untuk foto yang sudah di-crop sehingga tidak ada tepi kertas.
    """
    height, width = image.shape[:2]
    corners = [[0, 0], [width - 1, 0], [width - 1, height - 1], [0, height - 1]]
    return np.array(corners, dtype=np.int32).reshape(4, 1, 2)


def four_point_transform(image, points):
    """Luruskan dokumen miring menjadi tampak atas (perspective warp)."""
    top_left, top_right, bottom_right, bottom_left = order_points(points)

    width_bottom = np.linalg.norm(bottom_right - bottom_left)
    width_top = np.linalg.norm(top_right - top_left)
    max_width = int(max(width_bottom, width_top))

    height_right = np.linalg.norm(top_right - bottom_right)
    height_left = np.linalg.norm(top_left - bottom_left)
    max_height = int(max(height_right, height_left))

    source = np.array(
        [top_left, top_right, bottom_right, bottom_left], dtype="float32"
    )
    destination = np.array(
        [[0, 0], [max_width - 1, 0],
         [max_width - 1, max_height - 1], [0, max_height - 1]],
        dtype="float32",
    )
    matrix = cv2.getPerspectiveTransform(source, destination)
    return cv2.warpPerspective(image, matrix, (max_width, max_height))


def estimate_contrast(gray_image):
    """Perkirakan kontras teks terhadap kertas.

    Selisih antara kecerahan kertas (median) dan tinta (persentil ke-3),
    dihitung di area tengah saja supaya spiral dan bayangan di tepi
    tidak ikut terhitung. Foto normal bernilai sekitar 45 sampai 65,
    foto terlalu terang atau pudar bernilai di bawah 30.
    """
    height, width = gray_image.shape
    center = gray_image[int(height * 0.1):int(height * 0.9),
                        int(width * 0.1):int(width * 0.9)]
    return float(np.median(center) - np.percentile(center, 3))


def binarize_document(warped_image):
    """Ubah hasil luruskan menjadi hitam-putih ala hasil scan.

    Memakai adaptive threshold karena pencahayaan di kertas tidak rata.
    Konstanta C mengikuti kontras foto: foto normal memakai C maksimum,
    foto terlalu terang (teks pucat) memakai C lebih kecil supaya teks
    tidak dianggap sebagai latar.
    """
    gray_image = cv2.cvtColor(warped_image, cv2.COLOR_BGR2GRAY)
    contrast = estimate_contrast(gray_image)
    constant = float(np.clip(contrast * C_PER_CONTRAST, C_MIN, C_MAX))
    return cv2.adaptiveThreshold(
        gray_image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY, THRESHOLD_BLOCK, constant,
    )


def draw_document_outline(image, points):
    """Gambar garis hijau di sekeliling dokumen yang terdeteksi."""
    output = image.copy()
    cv2.drawContours(output, [points.astype(int)], -1, (0, 255, 0), 3)
    return output