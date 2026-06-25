# Templat PRD (Versi Ringkas)

> Sesuai untuk: keperluan ringkas, komunikasi dalaman, permulaan projek yang cepat  
> Nota: templat ini **tidak merangkumi keperluan prestasi** dan **tidak merangkumi kriteria penerimaan**

## 1. Maklumat Dokumen

- Nama projek:
- Nama keperluan:

## 2. Latar Belakang

### 2.1 Ringkasan Latar Belakang

Terangkan secara ringkas mengapa keperluan ini perlu dilaksanakan dan apakah masalah atau peluang yang wujud pada masa ini.

### 2.2 Objektif

Nyatakan dengan jelas apa yang ingin dicapai melalui keperluan ini.

Contoh:

- Meningkatkan kecekapan sesuatu proses
- Melengkapkan keupayaan asas yang masih tiada
- Menambah baik pengalaman pengguna

## 3. Skop

### 3.1 Dalam Skop

Terangkan apa yang termasuk dalam keperluan ini.

Contoh:

- Menambah fungsi XX
- Mengubah suai halaman XX
- Mengoptimumkan aliran kerja XX

### 3.2 Di Luar Skop

Terangkan apa yang secara jelas tidak termasuk supaya tiada salah faham.

Contoh:

- Tidak melibatkan perubahan pada backend admin
- Tidak melibatkan migrasi data
- Tidak melibatkan penyesuaian untuk mudah alih

## 4. Pengguna dan Senario Penggunaan

### 4.1 Pengguna Sasaran

Terangkan siapa yang akan menggunakan fungsi ini.

Contoh:

- Pengguna umum platform
- Kakitangan operasi
- Pentadbir dalaman

### 4.2 Senario Utama

Terangkan bila dan bagaimana pengguna akan menggunakan fungsi ini.

Contoh:

1. Apabila pengguna perlu melakukan XX, mereka boleh menyelesaikannya melalui XX
2. Apabila kakitangan operasi perlu mengurus XX, mereka boleh melakukannya di halaman XX

## 5. Keperluan Fungsi

### 5.1 Gambaran Keseluruhan Fungsi

Gunakan satu perenggan ringkas untuk menerangkan logik keseluruhan fungsi.

### 5.2 Butiran Fungsi

#### Fungsi 1: Nama Fungsi

- Penerangan:
- Cara dicetuskan:
- Logik pemprosesan:
- Input:
- Output:
- Situasi pengecualian:

#### Fungsi 2: Nama Fungsi

- Penerangan:
- Cara dicetuskan:
- Logik pemprosesan:
- Input:
- Output:
- Situasi pengecualian:

> Jika perlu, tambah lagi item fungsi dengan format yang sama

## 6. Peraturan Perniagaan

Terangkan peraturan, had, syarat dan perubahan status yang berkaitan dengan fungsi ini.

Contoh:

- Pengguna hanya boleh melakukan XX apabila berada dalam status XX
- Jika medan A kosong, penghantaran tidak dibenarkan
- Jika pengguna mengulangi tindakan, paparkan mesej XX

## 7. Penerangan Halaman / Interaksi

Jika keperluan ini melibatkan halaman atau aliran penggunaan, terangkan di sini.

### 7.1 Penerangan Halaman

- Nama halaman:
- Titik masuk:
- Elemen halaman:
- Tindakan butang:

### 7.1.1 Nota Keperluan Carta (jika satu atau beberapa carta diperlukan)

- Nama carta:
- Jenis carta: garis / bar / pai / carta jadual / lain-lain
- Sumber data:
- Medan utama:
- Logik medan:
- Nota dimensi / metrik / paksi:
- Syarat carian atau penapis:
- Paparan data terperinci:
- Hubungan antara beberapa carta:
- Interaksi carta: penapisan berkait / drill-down / pertukaran tab / tooltip / penapisan klik dan sebagainya

### 7.1.2 Rujukan Susun Atur Pelbagai Carta (jika beberapa carta diperlukan)

Jika halaman mengandungi satu atau lebih carta, pilih susun atur berdasarkan hierarki data, keperluan perbandingan dan ruang yang tersedia:

1. **Uniform Grid / Grid Seragam**: Semua bekas carta bersaiz sama dan tersusun kemas seperti papan catur; sesuai untuk papan pemantauan, kad data setara dan halaman ringkasan status.
2. **Primary-Detail / Hero Layout**: Satu carta utama menggunakan 50%-70% ruang atas atau kiri, dengan carta sokongan di sisi atau bawah; sesuai untuk halaman analisis seperti carta trend besar bersama carta komposisi dan jadual terperinci.
3. **Nested / Drill-down Layout**: Satu carta mengandungi, memaut atau mengemas kini carta lain; sesuai untuk analisis penerokaan dan drill-down.
4. **Tabbed Layout**: Beberapa carta homogen berkongsi satu bekas dan ditukar melalui tab; sesuai untuk paparan Hari/Minggu/Bulan apabila ruang terhad.
5. **Masonry / Waterfall Layout**: Item mempunyai lebar konsisten tetapi tinggi berbeza dan mengisi ruang kosong secara berturutan; sesuai untuk laporan media campuran, halaman H5 mudah alih dan suapan, tetapi gunakan dengan berhati-hati dalam dashboard.

### 7.1.3 Nota Halaman Proses Perniagaan (jika proses terlibat)

- Nama proses:
- Pencetus proses:
- Peranan yang terlibat:
- Nod proses:
- Tindakan nod dan perubahan status:
- Laluan pengecualian / pemulangan / penamatan:
- Nota carta alir:
- Halaman berkaitan: halaman permulaan / senarai tugasan / halaman butiran dan sejarah proses / konfigurasi / pengurusan kebenaran
- Peraturan kebenaran:

### 7.2 Aliran Interaksi

Aliran boleh diterangkan dalam bentuk teks dan, jika perlu, ditambah dengan carta alir.

Contoh:

1. Pengguna memasuki halaman XX
2. Pengguna menekan butang XX
3. Sistem memaparkan kandungan XX
4. Selepas dihantar, pengguna melihat hasil XX

## 8. Teks dan Salinan

Senaraikan mesej halaman, label butang, mesej ralat dan teks lain yang berkaitan.

Contoh:

- Teks butang: Hantar Sekarang
- Keadaan kosong: Tiada data
- Mesej ralat: Penghantaran gagal. Sila cuba lagi kemudian.

## 9. Data dan Kebergantungan

Terangkan sama ada keperluan ini bergantung pada sistem lain, API, konfigurasi atau sumber data.

Contoh:

- Bergantung pada pusat pengguna untuk memulangkan maklumat pengguna
- Bergantung pada platform konfigurasi untuk menghantar suis ciri
- Bergantung pada API XX untuk menyediakan hasil carian

## 10. Risiko dan Perhatian

Senaraikan risiko yang diketahui, kekangan, atau perkara yang perlu disahkan lebih awal.

Contoh:

- API berkaitan masih belum siap; jadual integrasi perlu disahkan
- Pengguna sedia ada mungkin memerlukan masa untuk menyesuaikan diri dengan aliran baharu
- Sebahagian definisi medan masih menunggu pengesahan akhir daripada pihak perniagaan
