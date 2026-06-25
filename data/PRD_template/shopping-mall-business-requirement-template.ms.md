# Templat Keperluan Perniagaan Pusat Beli-belah Dalam Talian
> Untuk senario pusat beli-belah seperti pengurusan produk, troli, checkout, bayaran, promosi, keahlian pelanggan, khidmat selepas jualan, penyelarasan inventori, dan analitik perdagangan.  
> Gantikan petunjuk dalam `[]` dengan kandungan perniagaan sebenar; buang item yang tidak berkaitan.

## 1. Maklumat Asas

| Medan | Kandungan |
| --- | --- |
| Nama templat | Templat Keperluan Perniagaan Pusat Beli-belah Dalam Talian |
| Nama keperluan | [Pembinaan pusat beli-belah jenama] |
| Projek | [Masukkan nama projek] |
| Jenis keperluan | Binaan baharu / Pengoptimuman / Refaktor |
| Keutamaan | Tinggi / Sederhana / Rendah |
| Jabatan pemohon | [Masukkan jabatan pemohon] |
| Pemohon | [Masukkan pemohon] |
| Tarikh permintaan | [YYYY-MM-DD] |
| Versi | V1.0 |

## 2. Latar Belakang Perniagaan

### 2.1 Ringkasan latar belakang

[Huraikan latar belakang perdagangan, saluran jualan, dan sebab pembinaan pusat beli-belah]

Penerangan: Jualan produk kini bergantung pada kedai fizikal, komuniti, dan pesanan manual. Maklumat produk, inventori, diskaun, pesanan, dan selepas jualan diurus berasingan. Pusat beli-belah bersatu diperlukan untuk paparan produk, pembelian ahli, bayaran dalam talian, pemenuhan pesanan, khidmat selepas jualan, dan analitik operasi.

### 2.2 Masalah semasa

- [Maklumat produk dan harga tersebar serta tidak konsisten antara frontend dan backend]
- [Pesanan, kutipan bayaran, potongan inventori, dan penghantaran tiada gelung tertutup]
- [Promosi bergantung pada konfigurasi dan kiraan manual serta mudah salah]
- [Bayaran balik, khidmat pelanggan, dan data operasi tiada penjejakan bersatu]

## 3. Objektif Perniagaan

### 3.1 Objektif perniagaan

- [Bina sistem paparan produk, SKU, harga, dan inventori yang bersatu]
- [Sambungkan troli, pesanan, bayaran, penghantaran, dan selepas jualan dalam satu gelung transaksi]
- [Sokong kupon, potongan penuh, jualan kilat, harga ahli, dan mekanik kempen]
- [Kumpul data pelanggan, pesanan, penukaran, dan pembelian semula untuk keputusan operasi]

### 3.2 Metrik kuantitatif

- [Tingkatkan penukaran checkout sebanyak 15%]
- [Capai kadar bayaran berjaya 98%]
- [Kurangkan purata masa selepas jualan sebanyak 40%]
- [Kurangkan masa konfigurasi promosi sebanyak 60%]

## 4. Skop Perniagaan

### 4.1 Dalam skop

- Kategori produk, SPU/SKU, harga, dan pengurusan listing
- Carian, penapis, butiran produk, troli, dan checkout
- Penciptaan pesanan, bayaran, batal, penghantaran, dan pengesahan terima
- Kupon, potongan penuh, jualan kilat, harga ahli, dan halaman kempen
- Profil ahli, alamat, simpanan, pelayaran, dan operasi pelanggan
- Bayaran balik/pulangan, kerjasama khidmat pelanggan, dan papan pemuka perdagangan

### 4.2 Di luar skop

- Kastam rentas sempadan dan pengiraan cukai antarabangsa
- Onboarding dan penyelesaian pedagang marketplace yang kompleks
- Pembinaan semula POS luar talian
- Membangunkan enjin live commerce dari awal

## 5. Peranan dan Senario Teras

### 5.1 Peranan sasaran

- Pelawat: semak produk, cari, lihat kempen, dan log masuk/daftar
- Ahli: tambah ke troli, pesan, bayar, lihat pesanan, dan mohon selepas jualan
- Operator: selenggara produk, kempen, cadangan, dan halaman kandungan
- Khidmat pelanggan: kendali pertanyaan, pengecualian pesanan, pulangan, dan aduan
- Staf gudang: terima pesanan, pilih, hantar, dan segerakkan nombor tracking
- Kewangan: lihat bayaran, bayaran balik, rekonsiliasi, dan invois
- Pentadbir sistem: selenggara kebenaran, kamus, bayaran, dan parameter pusat beli-belah

### 5.2 Senario perniagaan teras

1. Operator menyenaraikan produk dan mengkonfigurasi inventori, harga, dan tag kempen.
2. Pengguna mencari produk, masuk halaman butiran, tambah ke troli, dan menghantar pesanan.
3. Sistem mengira diskaun, caj penghantaran, dan jumlah perlu bayar; pengguna menyelesaikan bayaran dalam talian.
4. Gudang menerima pesanan untuk dihantar, memilih barang, menghantar, dan memulangkan nombor tracking.
5. Pengguna memohon bayaran balik/pulangan, khidmat pelanggan menyemak dan mencetuskan bayaran balik.
6. Operator melihat data penukaran, nilai pesanan purata, pembelian semula, inventori, dan prestasi kempen.

## 6. Keperluan Fungsi

### 6.1 Gambaran fungsi

[Ringkaskan keupayaan teras yang perlu dibina untuk sistem pusat beli-belah]

Penerangan: Keperluan ini merangkumi tujuh kumpulan keupayaan: produk, troli, pesanan dan bayaran, promosi, ahli dan pelanggan, selepas jualan, serta analitik.

### 6.2 Butiran fungsi

#### 6.2.1 Pengurusan produk dan SKU

- Penerangan: Menyelenggara kategori, jenama, SPU/SKU, imej, spesifikasi, harga, inventori, dan status listing.
- Pencetus: Operator mencipta atau mengemas kini produk.
- Peraturan / logik perniagaan:
-   Sokong hierarki kategori, jenama, atribut spesifikasi, dan gabungan SKU
-   Sokong draf, pratonton, listing/nyahlisting, susunan, dan tag cadangan
-   Sokong harga, inventori, had pembelian, dan kawasan jualan
- Input: Data produk, SKU, harga, inventori, imej, tag
- Output: Butiran produk, senarai SKU, status listing
- Pengendalian pengecualian: Konflik SKU, inventori tidak cukup, harga abnormal, produk dirujuk oleh pesanan

#### 6.2.2 Troli dan checkout

- Penerangan: Menyokong tambah ke troli, pilih item, ubah kuantiti, kira diskaun, dan hantar pesanan.
- Pencetus: Pengguna klik tambah ke troli atau checkout.
- Peraturan / logik perniagaan:
-   Sokong kuantiti troli, status dipilih, dan petunjuk item tidak sah
-   Sokong kupon, potongan penuh, harga ahli, potongan mata, dan kiraan penghantaran
-   Sokong alamat, invois, catatan, dan pilihan penghantaran
- Input: Pengguna, SKU, kuantiti, diskaun, alamat, cara penghantaran
- Output: Troli, helaian checkout, jumlah perlu bayar
- Pengendalian pengecualian: Inventori tidak cukup, harga berubah, diskaun tidak tersedia, alamat tidak boleh dihantar

#### 6.2.3 Pesanan dan bayaran

- Penerangan: Mengurus penciptaan pesanan, bayaran, batal, tutup tamat masa, penghantaran, dan pengesahan terima.
- Pencetus: Pengguna menghantar pesanan atau callback bayaran diterima.
- Peraturan / logik perniagaan:
-   Sokong mesin status pesanan, rekod bayaran, rekod bayaran balik, dan log operasi
-   Sokong pelbagai kaedah bayaran, pengesahan callback, dan tutup tamat masa
-   Sokong pecah pesanan, penghantaran separa, dan catatan pesanan
- Input: Pesanan, rekod bayaran, pengguna, produk, jumlah, status
- Output: Butiran pesanan, keputusan bayaran, tugasan penghantaran
- Pengendalian pengecualian: Bayaran berulang, bayaran gagal, pesanan tamat masa, jumlah tidak sepadan

#### 6.2.4 Promosi dan operasi ahli

- Penerangan: Mengkonfigurasi kupon, potongan penuh, jualan kilat, harga ahli, slot cadangan, dan halaman kempen.
- Pencetus: Operator mencipta kempen atau pengguna mengambil bahagian.
- Peraturan / logik perniagaan:
-   Sokong masa kempen, skop produk, skop pengguna, dan peraturan tindanan
-   Sokong pengambilan kupon, penebusan, tamat tempoh, dan ambang penggunaan
-   Sokong statistik prestasi kempen dan tag audiens
- Input: Kempen, kupon, tahap ahli, audiens, skop produk
- Output: Keputusan diskaun, halaman kempen, laporan pemasaran
- Pengendalian pengecualian: Konflik kempen, tindanan salah, inventori ditempah

#### 6.2.5 Selepas jualan dan khidmat pelanggan

- Penerangan: Mengendalikan bayaran balik, pulangan, pertukaran, aduan, dan pengecualian pesanan.
- Pencetus: Pengguna menghantar permohonan selepas jualan atau khidmat pelanggan mencipta tiket.
- Peraturan / logik perniagaan:
-   Sokong sebab, bukti, semakan, penghantaran balik, dan bayaran balik
-   Sokong catatan khidmat pelanggan, rekod rundingan, dan peringatan tamat masa
-   Sokong aliran status selepas jualan dan atribusi tanggungjawab
- Input: Kes selepas jualan, pesanan, bayaran, bukti, rekod khidmat
- Output: Keputusan semakan, keputusan bayaran balik, kemajuan selepas jualan
- Pengendalian pengecualian: Melebihi tempoh selepas jualan, item tidak boleh dipulangkan, bayaran balik gagal, penghantaran hilang

#### 6.2.6 Analitik perdagangan

- Penerangan: Menyediakan papan pemuka untuk jualan, penukaran, inventori, pelanggan, dan kempen.
- Pencetus: Operator atau pengurus melihat data.
- Peraturan / logik perniagaan:
-   Sokong statistik jumlah pesanan, nilai pesanan purata, penukaran, dan pembelian semula
-   Sokong jualan produk, pusingan inventori, ROI kempen, dan analisis saluran
-   Sokong eksport laporan dan definisi metrik
- Input: Pesanan, bayaran, produk, tingkah laku pengguna, data kempen
- Output: Papan pemuka operasi, laporan produk, analisis pelanggan
- Pengendalian pengecualian: Kelewatan data, kebenaran tidak cukup, definisi metrik berubah

## 7. Halaman dan Proses

| Halaman / laluan masuk | Laluan masuk | Elemen utama | Tindakan utama | Aliran |
| --- | --- | --- | --- | --- |
| Laman utama pusat beli-belah | Laluan masuk pelanggan | Carian, banner, kategori, produk disyorkan, kempen | Cari, semak, buka produk, log masuk/daftar | Pengguna masuk ke produk melalui kategori, carian, atau kempen. |
| Butiran produk | Senarai produk / hasil carian | Imej, harga, spesifikasi, inventori, ulasan, cadangan | Pilih spesifikasi, tambah troli, beli sekarang, simpan | Pengguna mengesahkan produk dan menambah ke troli atau membeli terus. |
| Troli dan checkout | Laluan masuk troli | Item, diskaun, alamat, penghantaran, invois, butiran jumlah | Ubah kuantiti, pilih diskaun, hantar pesanan | Sistem mengesahkan inventori dan harga sebelum mencipta pesanan belum bayar. |
| Pusat pesanan | Pusat ahli | Senarai pesanan, status, tracking, bayaran, selepas jualan | Bayar, batal, sahkan terima, mohon selepas jualan | Pengguna melihat kemajuan pesanan dan mengendalikan bayaran atau selepas jualan. |
| Backend operasi pusat beli-belah | Laluan masuk pentadbir | Produk, kempen, pesanan, selepas jualan, pelanggan, laporan | Senarai produk, konfigurasi kempen, kendali pengecualian, eksport laporan | Operator menyelenggara operasi perdagangan dan menjejak hasil. |

## 8. Peraturan Perniagaan dan Data

### 8.1 Peraturan / logik perniagaan

- Penghantaran pesanan mesti mengunci snapshot harga, diskaun, dan inventori.
- Hanya pesanan dibayar boleh masuk status menunggu penghantaran; pesanan tamat masa ditutup dan inventori dilepaskan.
- Promosi mesti mengesahkan skop produk, skop pengguna, masa, dan peraturan tindanan.
- Jumlah bayaran balik tidak boleh melebihi jumlah dibayar dan mesti menyimpan transaksi saluran bayaran.
- Perubahan harga, inventori, pesanan, dan selepas jualan mesti menyimpan log operasi.

### 8.2 Objek data utama

- Produk/SPU: id, nama, kategori, jenama, status, imej utama
- SKU: spesifikasi, harga, inventori, had pembelian, kawasan jualan
- Troli: pengguna, SKU, kuantiti, status dipilih, status tidak sah
- Pesanan: nombor pesanan, pengguna, butiran item, jumlah, status, alamat penghantaran
- Bayaran: nombor bayaran, saluran, jumlah, status, transaksi callback
- Kes selepas jualan: pesanan, sebab, bukti, status semakan, status bayaran balik

## 9. Keperluan Bukan Fungsi

- Prestasi: pertanyaan lazim halaman utama dan butiran produk kembali dalam 3 saat.
- Konsistensi: status pesanan, bayaran, inventori, dan bayaran balik perlu konsisten akhirnya dan boleh dijejak.
- Keselamatan: callback bayaran, alamat pengguna, dan jumlah pesanan memerlukan tandatangan dan semakan kebenaran.
- Kebolehgunaan: aliran pesanan, bayaran, dan bayaran balik memerlukan cuba semula dan petunjuk jelas.
- Audit: perubahan harga, inventori, pesanan, dan selepas jualan mesti merekod operator dan masa.

## 10. Integrasi dan Kebergantungan

- Gerbang bayaran
- Perkhidmatan tracking logistik
- Sistem inventori / gudang
- SMS atau notifikasi mesej
- Perkhidmatan invois / cukai
- Gudang data perusahaan / BI

## 11. Risiko dan Soalan Terbuka

### 11.1 Risiko

- Tindanan promosi kompleks boleh menyebabkan ralat harga.
- Ketidakselarasan bayaran dan inventori boleh menjejaskan pemenuhan dan khidmat pelanggan.
- Kempen puncak boleh menyebabkan tekanan tempahan inventori dan prestasi pesanan.
- Polisi selepas jualan tidak jelas boleh menyebabkan pertikaian khidmat pelanggan.

### 11.2 Soalan terbuka

- Adakah inventori berbilang gudang dan penghantaran pecah perlu disokong?
- Bolehkah kupon, potongan penuh, dan harga ahli ditindankan?
- Bagaimana masa tutup pesanan tamat masa dan pelepasan inventori dikonfigurasi?
- Adakah bayaran balik memerlukan laluan asal dan semakan manual?
- Adakah invois, mata, tahap ahli, dan ulasan diperlukan?

## 12. Pencapaian dan Penerimaan

| Pencapaian | Tarikh sasaran | Kriteria penerimaan |
| --- | --- | --- |
| Pengesahan keperluan | T+1 minggu | Sahkan gelung transaksi, peraturan promosi, inventori, dan polisi selepas jualan |
| Semakan prototaip | T+3 minggu | Lengkapkan prototaip halaman utama, butiran, checkout, pesanan, dan backend |
| Pembangunan dan integrasi | T+8 minggu | Lengkapkan integrasi bayaran, inventori, logistik, dan notifikasi |
| Pelancaran rintis | T+10 minggu | Lancarkan produk dan pengguna terpilih secara gray |
| Pelancaran produksi | T+12 minggu | Lengkapkan pelancaran penuh, konfigurasi operasi, dan penerimaan |
