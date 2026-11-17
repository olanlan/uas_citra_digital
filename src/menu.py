"""Menu interaktif (CLI) untuk Document Scanner."""
import os

IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png", ".bmp", ".webp")


def list_images(images_dir):
    """Ambil daftar file gambar di folder images/."""
    if not os.path.isdir(images_dir):
        return []
    return sorted(f for f in os.listdir(images_dir)
                  if f.lower().endswith(IMAGE_EXTENSIONS))


def clean_path(raw_path):
    """Bersihkan path hasil drag-drop (sering ada tanda kutip)."""
    return raw_path.strip().strip('"').strip("'")


def choose_from_folder(images_dir):
    """Tampilkan daftar gambar di images/ dan minta user memilih nomor."""
    files = list_images(images_dir)
    if not files:
        print(f"\nFolder {images_dir} kosong. Pakai menu 2 untuk path sendiri.")
        return None
    print("\nGambar di folder images/:")
    for number, name in enumerate(files, start=1):
        print(f"  {number}. {name}")
    choice = input("Pilih nomor (Enter untuk batal): ").strip()
    if not choice.isdigit() or not 1 <= int(choice) <= len(files):
        print("Dibatalkan.")
        return None
    return os.path.join(images_dir, files[int(choice) - 1])


def ask_custom_path():
    """Minta path gambar dari lokasi mana saja."""
    path = clean_path(input("\nMasukkan path gambar (boleh drag-drop file): "))
    if not os.path.isfile(path):
        print("File tidak ditemukan.")
        return None
    return path


def print_menu():
    print("\n=========== DOCUMENT SCANNER ===========")
    print("1. Scan gambar dari folder images/")
    print("2. Scan gambar dari path sendiri")
    print("3. Scan semua gambar di folder images/")
    print("0. Keluar")


def run_menu(images_dir, output_dir, run_on_image):
    """Loop menu utama. Fungsi proses dikirim dari main.py."""
    while True:
        print_menu()
        choice = input("Pilih menu: ").strip()

        if choice == "1":
            path = choose_from_folder(images_dir)
            if path:
                run_on_image(path, output_dir)
        elif choice == "2":
            path = ask_custom_path()
            if path:
                run_on_image(path, output_dir)
        elif choice == "3":
            for name in list_images(images_dir):
                run_on_image(os.path.join(images_dir, name), output_dir)
        elif choice == "0":
            print("Selesai.")
            break
        else:
            print("Pilihan tidak valid.")