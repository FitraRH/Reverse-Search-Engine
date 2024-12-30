# Panel Admin Image Search

## Gambaran Umum

Proyek ini mengimplementasikan **Panel Admin Image Search** menggunakan **Selenium** dan **Streamlit**. Aplikasi ini memungkinkan pengguna untuk mencari dan mengunduh gambar secara otomatis dari Google Image Search atau mengunggah gambar secara manual ke dalam dataset. Aplikasi ini juga mendukung unggahan batch melalui file ZIP dan mengatur gambar ke dalam folder yang telah ditentukan.

## Fitur

1. **Pencarian dan Pengunduhan Gambar Otomatis:**
   - Menggunakan Selenium untuk mencari gambar di Google Images berdasarkan input pengguna.
   - Mengunduh gambar langsung ke folder yang dikategorikan.

2. **Unggahan Manual:**
   - Mendukung unggahan gambar individual.
   - Mendukung unggahan batch melalui file ZIP.

3. **Pengaturan Dataset:**
   - Secara otomatis mengategorikan gambar ke folder yang ditentukan.
   - Memastikan konvensi penamaan file yang valid.

4. **Panel Admin:**
   - Dibangun menggunakan Streamlit, menyediakan antarmuka web yang ramah pengguna untuk mengelola dataset.

5. **Logging:**
   - Mencatat tindakan dan kesalahan penting untuk debugging dan transparansi.

## Library yang Digunakan

- **os**: Untuk operasi direktori dan file.
- **time**: Untuk menghasilkan nama file unik dan penundaan.
- **requests**: Untuk mengunduh gambar.
- **logging**: Untuk mencatat aktivitas aplikasi.
- **Pillow**: Untuk pemrosesan gambar.
- **selenium**: Untuk scraping Google Images.
- **webdriver-manager**: Untuk mengelola ChromeDriver.
- **streamlit**: Untuk membuat antarmuka panel admin.
- **re**: Untuk menangani ekspresi reguler dalam penamaan file.
- **warnings**: Untuk menyembunyikan peringatan yang tidak diperlukan.
- **shutil**: Untuk menangani operasi file dan direktori.
- **pathlib**: Untuk bekerja dengan jalur file.
- **zipfile**: Untuk mengekstrak file ZIP.
- **tempfile**: Untuk membuat direktori sementara.

## Fungsi

### 1. **`setup_driver`**

Mengatur dan mengonfigurasi Selenium ChromeDriver.

**Fitur Utama:**
- Menjalankan Chrome dalam mode headless.
- Mengonfigurasi Chrome dengan berbagai optimasi dan solusi masalah.
- Menonaktifkan GPU dan fitur yang tidak diperlukan untuk stabilitas.

**Output:**
- Mengembalikan instance dari Selenium WebDriver yang telah dikonfigurasi.

### 2. **`search_images_selenium`**

Melakukan pencarian gambar di Google Images dan mengekstrak URL gambar menggunakan Selenium.

**Input:**
- `query`: Kata kunci pencarian.
- `num_results`: Jumlah URL gambar yang ingin diambil.

**Output:**
- Daftar URL gambar.

### 3. **`download_image`**

Mengunduh gambar dari URL dan   ke folder tertentu.

**Input:**
- `url`: URL gambar.
- `query`: Nama kategori atau kelas untuk gambar tersebut.

**Output:**
- Menyimpan gambar ke folder yang sesuai dan mengembalikan jalurnya.

### 4. **`handle_manual_upload`**

Memproses unggahan gambar individual melalui panel admin.

**Input:**
- `uploaded_files`: Daftar file gambar yang diunggah.
- `target_folder`: Folder tujuan untuk gambar.

**Output:**
- Menyimpan gambar yang diunggah ke folder tujuan dan mengembalikan jalurnya.

### 5. **`handle_zip_upload`**

Memproses unggahan file ZIP dan mengekstrak gambar ke folder tertentu.

**Input:**
- `zip_file`: File ZIP yang diunggah.
- `custom_class_name`: Nama folder/kelas tujuan.

**Output:**
- Mengekstrak dan menyimpan gambar dari file ZIP ke folder yang ditentukan.

### 6. **`get_existing_folders`**

Mengambil daftar folder dataset yang ada.

**Output:**
- Daftar nama folder di direktori dataset.

## Input dan Output

### Input

1. **Kata Kunci Pencarian:**
   - Kata kunci teks untuk pencarian gambar otomatis.

2. **Jumlah Gambar:**
   - Jumlah gambar yang ingin diambil selama pencarian otomatis.

3. **File yang Diunggah:**
   - File gambar individual atau file ZIP untuk unggahan manual.

4. **Nama Folder/Kelas:**
   - Nama folder tujuan untuk mengatur gambar yang diunggah.

### Output

1. **Gambar yang Diunduh:**
   - Gambar yang diambil dari Google Image Search dan disimpan ke folder.

2. **Gambar yang Diunggah:**
   - Gambar yang diunggah melalui proses manual atau file ZIP.

3. **Dataset yang Terorganisir:**
   - Semua gambar disimpan di direktori `101_ObjectCategories`, dikategorikan ke dalam folder.

## Setup dan Penggunaan

### Prasyarat

1. **Python 3.7+**
2. Instal library yang diperlukan:
   ```bash
   pip install selenium webdriver-manager Pillow streamlit requests
   ```

### Menjalankan Aplikasi

1. Jalankan panel admin Streamlit:
   ```bash
   streamlit run admin_panel.py
   ```
2. Gunakan tab untuk:
   - Melakukan pencarian dan pengunduhan gambar otomatis.
   - Mengunggah gambar individual atau file ZIP secara manual.

### Struktur Direktori

- Direktori dataset: `101_ObjectCategories`
- Gambar yang disimpan diatur ke dalam subfolder sesuai dengan nama kelas.

## Peningkatan

1. **Dukungan untuk Mesin Pencari Lain:** Menambahkan dukungan untuk Bing atau DuckDuckGo untuk kemampuan pencarian gambar yang lebih luas.
2. **Integrasi Cloud:** Memungkinkan penyimpanan dataset ke solusi cloud seperti AWS S3 atau Google Drive.
3. **Peningkatan Penanganan Error:** Menambahkan umpan balik terperinci untuk kesalahan umum selama proses unggah atau unduh.
4. **Format Gambar yang Lebih Luas:** Mendukung format gambar tambahan seperti TIFF atau WEBP.
5. **Tambahkan Filter Pencarian:** Memungkinkan penyaringan berdasarkan resolusi atau tipe gambar selama pencarian.

## Kesimpulan

Panel Admin Image Search menyediakan cara yang kuat dan intuitif untuk mengelola dataset melalui pengumpulan gambar otomatis dan manual. Desain modularnya memastikan kemudahan perpanjangan dan integrasi ke dalam alur kerja yang lebih besar.

