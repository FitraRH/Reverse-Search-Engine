# Reverse Image Search Engine

## Gambaran Umum

Proyek ini mengimplementasikan Reverse Image Search Engine menggunakan model deep learning ResNet-50 yang telah dilatih sebelumnya. Sistem ini mengekstrak fitur gambar dan membandingkannya untuk mengidentifikasi gambar serupa dalam dataset (Caltech 101). Proyek ini mencakup antarmuka web berbasis Streamlit untuk interaksi pengguna.

## Fitur

1. **Ekstraksi Fitur:** Mengekstraksi fitur berbasis deep learning dari gambar menggunakan ResNet-50.
2. **Pemrosesan Batch:** Memproses gambar dalam batch untuk efisiensi.
3. **Pencarian Berdasarkan Kelas:** Memungkinkan pencarian gambar dalam kelas tertentu.
4. **Pencarian Kemiripan:** Menemukan gambar paling mirip berdasarkan cosine similarity.
5. **Auto-Koreksi:** Menyarankan nama kelas yang benar untuk input yang diberikan pengguna menggunakan pencocokan fuzzy.
6. **Antarmuka Web Streamlit:** Antarmuka yang ramah pengguna untuk mengunggah gambar dan melihat hasil pencarian.

## Library yang Digunakan

- **os:** Untuk operasi direktori dan jalur file.
- **numpy:** Untuk operasi numerik dan manipulasi matriks.
- **torch:** Untuk bekerja dengan model deep learning dan tensor.
- **torchvision:** Untuk mengakses model yang telah dilatih sebelumnya dan transformasi gambar.
- **scikit-learn (cosine\_similarity):** Untuk menghitung skor kemiripan.
- **Pillow:** Untuk manipulasi gambar.
- **streamlit:** Untuk membuat antarmuka web.
- **warnings:** Untuk menyembunyikan peringatan yang tidak diperlukan.
- **difflib:** Untuk auto-koreksi nama kelas menggunakan pencocokan fuzzy.

## Dataset

- Sistem menggunakan dataset Caltech 101, yang terdiri dari 101 kategori objek.
- Struktur direktori:
  ```
  101_ObjectCategories/
      class_1/
          image_1.jpg
          image_2.jpg
          ...
      class_2/
          ...
  ```

## Input dan Output

### Input

1. **File Gambar:** File gambar yang diunggah (JPEG, PNG).
2. **Nama Kelas (Opsional):** String yang mewakili nama kelas yang diinginkan untuk memfilter hasil pencarian.

### Output

1. **Hasil Pencarian:**
   - Ditampilkan sebagai grid gambar dengan skor kemiripan.
   - Gambar diambil dari dataset.

## Detail Kode

### 1. Model Pre-Trained

- **ResNet-50:** Model deep learning yang telah dilatih sebelumnya dari torchvision.
- Lapisan klasifikasi terakhir dihapus untuk menggunakan model sebagai ekstraktor fitur.
- Gambar input diubah ukurannya menjadi 224x224 dan dinormalisasi.

### 2. Transformasi Gambar

Gambar diproses menggunakan:

- **Resize:** Mengubah ukuran gambar menjadi (224x224).
- **ToTensor:** Mengubah gambar menjadi tensor PyTorch.
- **Normalize:** Menormalkan gambar dengan nilai mean dan standar deviasi yang sesuai untuk ResNet-50.

### 3. Pemrosesan Batch

- Gambar diproses dalam batch untuk mengoptimalkan penggunaan memori dan waktu komputasi.
- **Dataset dan DataLoader:** Utilitas PyTorch untuk mengelola dataset dan batching.

### 4. Ekstraksi Fitur

Fitur diekstraksi dari gambar menggunakan model ResNet-50 dan disimpan sebagai array NumPy untuk penggunaan di masa depan.

### 5. Auto-Koreksi untuk Nama Kelas

- Menggunakan fungsi `difflib.get_close_matches` untuk menyarankan koreksi untuk input pengguna.
- Pencocokan fuzzy memastikan penanganan yang robust untuk kesalahan ketik atau input parsial.

### 6. Pencarian Cosine Similarity

- Membandingkan fitur gambar query dengan fitur dataset.
- Mengambil top-k gambar yang paling mirip.

### 7. Antarmuka Streamlit

#### Halaman Utama:

- **Upload Image:** Memungkinkan pengguna untuk mengunggah gambar untuk pencarian.
- **Nama Kelas (Opsional):** Bidang input untuk memfilter hasil pencarian.
- **Search Button:** Memicu fungsi pencarian.

#### Sidebar:

- Menampilkan daftar semua kelas yang tersedia dalam dataset.

### Fungsi

#### 1. `extract_features_in_batches`

Mengekstraksi fitur dari daftar jalur gambar dalam batch.

**Input:**

- `image_paths`: Daftar jalur file gambar.
- `batch_size`: Jumlah gambar untuk diproses per batch (default=32).

**Output:**

- Tensor fitur yang diekstraksi.
- Daftar jalur gambar.

#### 2. `update_dataset`

Memproses dataset untuk mengekstraksi fitur dan label untuk semua gambar. Menyimpan data untuk penggunaan di masa depan.

#### 3. `extract_features_single`

Mengekstraksi fitur untuk satu gambar.

**Input:**

- `image_path`: Jalur ke file gambar.

**Output:**

- Array NumPy fitur yang diekstraksi.

#### 4. `auto_correct_class_name`

Menyarankan koreksi untuk nama kelas yang diberikan pengguna.

**Input:**

- `input_text`: Teks input pengguna.
- `class_names`: Daftar nama kelas yang tersedia.

**Output:**

- Nama kelas yang dikoreksi atau input asli.

#### 5. `find_similar_images`

Menemukan gambar serupa berdasarkan cosine similarity atau penyaringan nama kelas.

**Input:**

- `query_image_path`: Jalur ke gambar query.
- `filter_class`: Nama kelas untuk penyaringan (opsional).
- `top_k`: Jumlah gambar serupa yang akan diambil (default=5).

**Output:**

- Daftar tuple yang berisi nama kelas, skor kemiripan, dan jalur gambar.

## Setup dan Penggunaan

### Prasyarat

- Python 3.7+
- Install library yang diperlukan menggunakan:
  ```bash
  pip install numpy torch torchvision scikit-learn pillow streamlit
  ```

### Menjalankan Aplikasi

1. Pastikan dataset (`101_ObjectCategories`) berada di direktori yang sama dengan skrip.
2. Mulai aplikasi Streamlit:
   ```bash
   streamlit run search_engine.py
   ```
3. Unggah gambar atau tentukan nama kelas untuk mencari gambar serupa.
