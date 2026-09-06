# 3D Wireframe Engine

![Python](https://img.shields.io/badge/Python-3.x-3776AB?style=flat-square&logo=python&logoColor=white)
![Pygame](https://img.shields.io/badge/Library-Pygame-yellow?style=flat-square)
![Math](https://img.shields.io/badge/Focus-Linear%20Algebra-green?style=flat-square)

Software rendering engine 3D berbasis CPU yang dibangun dari nol menggunakan Python dan Pygame, tanpa ketergantungan pada pustaka grafika 3D seperti OpenGL.

Aplikasi ini mengimplementasikan matematika proyeksi perspektif, matriks transformasi 3D, serta sistem kamera interaktif untuk merender objek wireframe dari berkas `.obj` (termasuk model 3D Tank T-34 dan Sphere).

---

## Fitur Utama

- **Pipeline Proyeksi Perspektif**: Menghitung transformasi koordinat 3D dunia (world space) menjadi koordinat 2D layar (screen space).
- **Matriks Transformasi Linier**: Implementasi rotasi (sumbu X, Y, Z), translasi, dan penskalaan koordinat poligon secara manual.
- **Sistem Kamera 6-DOF**: Kontrol pergerakan kamera dinamis (maju, mundur, geser, rotasi sudut pandang) secara realtime.
- **Wavefront (.obj) Parser**: Membaca dan memetakan vertex dan face dari file model 3D eksternal ke dalam ruang render.

---

## Struktur Berkas Inti

```text
├── camera.py             # Logika posisi, arah pandang, dan matriks kamera
├── matrix_functions.py   # Fungsi aljabar linier dan transformasi matriks
├── object_3d.py          # Definisi objek poligon, simpul (vertices), dan sisi (faces)
├── projection.py         # Matriks proyeksi perspektif ke viewport layar
├── main.py               # Render loop utama berbasis Pygame (resolusi 1280x720, 60 FPS)
└── resources/            # Berkas model 3D (t_34_obj.obj, sphere.obj)
```

---

## Cara Menjalankan

### Prasyarat
- Python 3.10 atau versi yang lebih baru
- Pustaka Pygame

### Instalasi dan Eksekusi
1. Clone repositori:
   ```bash
   git clone https://github.com/mshadiqaf/3d-wireframe-engine.git
   cd 3d-wireframe-engine
   ```
2. Pasang dependensi:
   ```bash
   pip install pygame
   ```
3. Jalankan aplikasi:
   ```bash
   python main.py
   ```

### Kontrol Kamera
- **W, A, S, D**: Bergerak maju, kiri, mundur, dan kanan
- **Spasi / Shift**: Bergerak naik / turun
- **Panah Keyboard / Mouse**: Merotasi orientasi sudut pandang kamera

---

## Konteks Akademik
Proyek ini dikembangkan sebagai pemenuhan Tugas Besar mata kuliah Grafika Komputer 3D, Program Studi Informatika, Institut Teknologi Kalimantan.
