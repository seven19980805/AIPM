# Templat Keperluan Perniagaan Logistik dan Gudang
> Untuk kerjasama WMS/TMS, inbound dan putaway, operasi gudang, pengurusan inventori, penghantaran outbound, penghantaran akhir, pengecualian, dan analitik operasi.  
> Gantikan petunjuk dalam `[]` dengan kandungan perniagaan sebenar; buang item yang tidak berkaitan.

## 1. Maklumat Asas

| Medan | Kandungan |
| --- | --- |
| Nama templat | Templat Keperluan Perniagaan Logistik dan Gudang |
| Nama keperluan | [Pembinaan sistem logistik dan gudang bersepadu] |
| Projek | [Masukkan nama projek] |
| Jenis keperluan | Binaan baharu / Pengoptimuman / Refaktor |
| Keutamaan | Tinggi / Sederhana / Rendah |
| Jabatan pemohon | [Masukkan jabatan pemohon] |
| Pemohon | [Masukkan pemohon] |
| Tarikh permintaan | [YYYY-MM-DD] |
| Versi | V1.0 |

## 2. Latar Belakang Perniagaan

### 2.1 Ringkasan latar belakang

[Huraikan latar belakang logistik gudang, proses semasa, dan sebab pembinaan sistem]

Penerangan: Inbound, putaway, inventori, picking, semakan, penghantaran, dan delivery kini bergantung pada beberapa sistem dan hamparan manual. Ketepatan inventori, kecekapan operasi, dan keterlihatan logistik tidak mencukupi. Sistem logistik gudang bersatu diperlukan untuk menyokong operasi gudang, kerjasama gudang-penghantaran, pengendalian pengecualian, dan analitik.

### 2.2 Masalah semasa

- [Janji temu inbound, penerimaan, dan putaway tiada panduan kerja bersatu]
- [Perbezaan inventori sukar dikesan dan dijejak tepat pada masa]
- [Picking, semakan, pembungkusan, dan penghantaran bergantung pada komunikasi manual]
- [Tracking penghantaran, pengecualian, dan bukti terima tidak boleh dijejak secara seragam]

## 3. Objektif Perniagaan

### 3.1 Objektif perniagaan

- [Bina pengurusan bersatu untuk gudang, zon, lokasi, inventori, dan batch]
- [Tingkatkan kecekapan dan ketepatan operasi inbound, gudang, outbound, dan penghantaran]
- [Sambungkan aliran maklumat antara pesanan, gudang, carrier, dan pelanggan]
- [Kumpul data pusingan inventori, kecekapan operasi, ketepatan masa penghantaran, dan pengecualian]

### 3.2 Metrik kuantitatif

- [Capai ketepatan inventori 99%]
- [Capai ketepatan outbound 99.5%]
- [Tingkatkan kecekapan picking purata sebanyak 30%]
- [Kurangkan masa pengendalian pengecualian penghantaran sebanyak 40%]

## 4. Skop Perniagaan

### 4.1 Dalam skop

- Janji temu inbound, penerimaan, pemeriksaan kualiti, dan putaway
- Zon gudang, lokasi, inventori, batch, beku, dan kiraan
- Wave, picking, semakan, pembungkusan, dan serahan outbound
- Carrier, waybill, tracking penghantaran, dan bukti terima
- Pulangan inbound, pengecualian, rosak/hilang, dan tuntutan
- Papan pemuka logistik gudang dan laporan operasi

### 4.2 Di luar skop

- Membangunkan sendiri sistem kawalan peralatan gudang automatik
- Pembelian terminal perkakasan tracking kenderaan
- Kastam rentas sempadan dan pengangkutan antarabangsa
- Pembinaan semula sistem penyelesaian kewangan yang kompleks

## 5. Peranan dan Senario Teras

### 5.1 Peranan sasaran

- Kerani gudang: penerimaan, putaway, pindah lokasi, kiraan, dan pelarasan inventori
- Picker: lengkapkan tugasan picking mengikut wave atau pesanan
- Penyemak: semak produk, kuantiti, batch, dan kendali perbezaan
- Packer: bungkus, timbang, cetak label, dan serah outbound
- Dispatcher: tetapkan carrier, jejak pengangkutan, dan kendali pengecualian
- Pemandu/carrier: terima waybill, ambil barang, hantar, dan pulangkan bukti terima
- Penyelia operasi: lihat inventori, kecekapan, ketepatan masa, dan data pengecualian

### 5.2 Senario perniagaan teras

1. Pembekal atau sistem huluan mencipta janji temu inbound, dan gudang menerima mengikut janji temu.
2. Kerani gudang melengkapkan pemeriksaan, mencipta tugasan putaway, dan meletakkan barang ke lokasi sasaran.
3. Sistem mencipta wave dan tugasan picking daripada pesanan; picker memilih mengikut laluan.
4. Penyemak menyemak barang dan kuantiti; perbezaan masuk ke aliran pengecualian.
5. Packer menimbang, mencetak label, menyerahkan kepada carrier, dan sistem menyegerakkan waybill/tracking.
6. Penyelia melihat ketepatan inventori, kecekapan outbound, ketepatan masa penghantaran, dan pengecualian.

## 6. Keperluan Fungsi

### 6.1 Gambaran fungsi

[Ringkaskan keupayaan teras yang perlu dibina untuk sistem logistik gudang]

Penerangan: Keperluan ini merangkumi tujuh kumpulan keupayaan: inbound, inventori gudang, picking dan semakan, penghantaran outbound, pengangkutan, pengecualian songsang, dan analitik.

### 6.2 Butiran fungsi

#### 6.2.1 Janji temu inbound dan putaway

- Penerangan: Mengurus janji temu, ketibaan, penerimaan, pemeriksaan kualiti, dan tugasan putaway.
- Pencetus: Sistem huluan mencipta pesanan inbound atau pembekal menjadualkan ketibaan.
- Peraturan / logik perniagaan:
-   Sokong masa janji temu, pembekal, jumlah kotak, SKU, dan batch
-   Sokong perbezaan penerimaan, keputusan pemeriksaan, dan pendaftaran pengecualian
-   Jana tugasan putaway mengikut strategi lokasi
- Input: Pesanan inbound, pembekal, SKU, batch, kuantiti, keputusan pemeriksaan
- Output: Rekod penerimaan, tugasan putaway, rekod tambah inventori
- Pengendalian pengecualian: Ketibaan melebihi janji temu, kurang/lebih barang, pemeriksaan gagal, lokasi tidak cukup

#### 6.2.2 Inventori dan operasi gudang

- Penerangan: Menyelenggara gudang, zon, lokasi, inventori, batch, beku, dan kiraan.
- Pencetus: Pergerakan inventori, pelan kiraan, atau pindah lokasi.
- Peraturan / logik perniagaan:
-   Sokong inventori tersedia, beku, dalam transit, dan mengikut batch
-   Sokong pindah lokasi, replenishment, pelarasan, beku/nyahbeku, dan lejar inventori
-   Sokong kiraan penuh, kiraan bergerak, kiraan kitaran, dan rawatan perbezaan
- Input: Gudang, lokasi, SKU, batch, status inventori, dokumen kiraan
- Output: Lejar inventori, aliran inventori, perbezaan kiraan
- Pengendalian pengecualian: Akaun tidak sepadan fizikal, inventori beku, batch luput, kapasiti lokasi tidak cukup

#### 6.2.3 Wave picking dan semakan

- Penerangan: Menjana wave, tugasan picking, tugasan semakan, dan pengendalian perbezaan berdasarkan pesanan.
- Pencetus: Pesanan masuk status perlu keluar atau operator mencipta wave.
- Peraturan / logik perniagaan:
-   Sokong wave mengikut gudang, carrier, SLA, dan atribut produk
-   Sokong laluan picking, kotak penuh/pecahan, kekurangan stok, dan penggantian
-   Sokong semakan imbasan, pendaftaran perbezaan, dan semakan kedua
- Input: Pesanan, SKU, lokasi, peraturan wave, tugasan picking
- Output: Senarai picking, keputusan semakan, rekod perbezaan
- Pengendalian pengecualian: Kekurangan stok, salah pilih, batch tidak sepadan, semakan gagal

#### 6.2.4 Pembungkusan outbound dan serahan

- Penerangan: Melengkapkan pembungkusan, timbang, label, pengesahan outbound, dan serahan carrier.
- Pencetus: Selepas semakan lulus, masuk proses pembungkusan outbound.
- Peraturan / logik perniagaan:
-   Sokong pecah/gabung bungkusan, timbang, rekod bahan, dan cetak label
-   Sokong serahan outbound, pengesahan ambil, dan potongan inventori
-   Sokong catatan pesanan, pembungkusan khas, dan petunjuk barang berbahaya
- Input: Keputusan semakan, bungkusan, berat, label, carrier
- Output: Pesanan outbound, nombor bungkusan, nombor waybill, rekod serahan
- Pengendalian pengecualian: Cetak label gagal, berat abnormal, carrier menolak, outbound dibatalkan

#### 6.2.5 Pengangkutan dan tracking

- Penerangan: Mengurus carrier, waybill, nod tracking, bukti terima, dan pengecualian penghantaran.
- Pencetus: Selepas outbound, waybill dicipta dan diserahkan kepada carrier.
- Peraturan / logik perniagaan:
-   Sokong laluan carrier, templat caj penghantaran, dan peraturan masa
-   Sokong langganan tracking, callback nod, gambar bukti terima, dan resit elektronik
-   Sokong kelewatan, ditolak, hilang, rosak, dan pengecualian lain
- Input: Waybill, carrier, bungkusan, nod tracking, maklumat bukti terima
- Output: Tracking logistik, keputusan terima, rekod pengecualian
- Pengendalian pengecualian: Tracking lewat, terima gagal, hilang, rosak, alamat tidak dapat dicapai

#### 6.2.6 Logistik songsang dan pengecualian

- Penerangan: Mengendalikan pulangan, penolakan, pertukaran, item pengecualian, tuntutan, dan tulis balik inventori.
- Pencetus: Pelanggan memulangkan barang, carrier menolak, atau gudang menemui pengecualian.
- Peraturan / logik perniagaan:
-   Sokong janji temu pulangan, penerimaan, pemeriksaan, putaway semula, atau lupus
-   Sokong pendaftaran pengecualian, atribusi tanggungjawab, tuntutan, dan had masa
-   Sokong kaitan selepas jualan, waybill, inventori, dan status kewangan
- Input: Pesanan pulangan, sebab pengecualian, keputusan pemeriksaan, pihak bertanggungjawab, hasil
- Output: Pulangan inbound, lejar pengecualian, rekod tuntutan
- Pengendalian pengecualian: Pulangan tanpa pesanan asal, barang rosak, tanggungjawab tidak jelas, lewat diproses

## 7. Halaman dan Proses

| Halaman / laluan masuk | Laluan masuk | Elemen utama | Tindakan utama | Aliran |
| --- | --- | --- | --- | --- |
| Meja kerja gudang | Laluan masuk operasi gudang | Menunggu terima, putaway, picking, semakan, amaran pengecualian | Ambil tugasan, imbas, hantar keputusan, lihat pengecualian | Staf operasi masuk meja kerja untuk mengambil dan menyelesaikan tugasan gudang. |
| Pengurusan inbound | Backend gudang | Janji temu, pesanan inbound, rekod penerimaan, keputusan pemeriksaan, tugasan putaway | Cipta janji temu, terima, semak, jana putaway, tutup inbound | Kerani gudang menerima mengikut janji temu dan melakukan putaway. |
| Pengurusan inventori | Backend gudang | Lejar inventori, lokasi, batch, beku, dokumen kiraan | Cari, pindah lokasi, beku, kira, laras | Penyelia melihat inventori dan mengendalikan perbezaan. |
| Operasi outbound | Laluan masuk operasi gudang | Wave, senarai picking, tugasan semakan, bungkusan, label | Jana wave, picking, semak, bungkus, serah | Sistem menjana tugasan mengikut pesanan dan menyelesaikan serahan outbound. |
| Tracking pengangkutan | Backend logistik | Waybill, tracking, bukti terima, pengecualian, carrier | Tetapkan carrier, semak tracking, kendali pengecualian, eksport laporan | Dispatcher menjejak penghantaran dan mengendalikan pengecualian. |
| Papan pemuka gudang-penghantaran | Laluan masuk pengurusan | Ketepatan inventori, kecekapan outbound, masa penghantaran, kadar pengecualian | Tapis, telusuri, eksport, langgan | Pengurusan melihat kualiti operasi gudang dan penghantaran. |

## 8. Peraturan Perniagaan dan Data

### 8.1 Peraturan / logik perniagaan

- Setiap pergerakan inventori mesti menjana rekod lejar inventori dan dikaitkan dengan dokumen sumber.
- Inventori tersedia hanya boleh ditolak dan bungkusan dijana selepas semakan outbound lulus.
- Batch yang sama perlu dipilih mengikut FIFO atau peraturan batch tertentu.
- Pengecualian mesti merekod pihak bertanggungjawab, kesimpulan, dan tarikh akhir pengendalian.
- Tracking waybill dan bukti terima perlu menyokong cuba semula dan pengisian manual apabila callback gagal.

### 8.2 Objek data utama

- Gudang: kod, nama, zon, lokasi, kapasiti, status
- Inventori: SKU, batch, lokasi, tersedia, beku, dalam transit, dikhaskan
- Pesanan inbound: pembekal, SKU, kuantiti, masa janji temu, keputusan pemeriksaan
- Pesanan outbound: pesanan, wave, picking, semakan, bungkusan, waybill
- Waybill: carrier, bungkusan, tracking, bukti terima, status pengecualian
- Kes pengecualian: jenis, sebab, pihak bertanggungjawab, pengendali, keputusan

## 9. Keperluan Bukan Fungsi

- Prestasi: operasi imbasan dan pertanyaan inventori perlu respons pantas; tindakan lazim selesai dalam 2 saat.
- Ketepatan: status inventori, inbound, outbound, dan waybill perlu boleh dijejak dan konsisten akhirnya.
- Operasi mudah alih: halaman handheld perlu menyokong imbasan, rangkaian lemah, dan hantar semula luar talian.
- Audit: pelarasan inventori, pengendalian pengecualian, dan pengisian waybill manual mesti direkodkan.
- Keselamatan: data gudang, pemilik barang, dan carrier mesti diasingkan mengikut kebenaran.

## 10. Integrasi dan Kebergantungan

- Sistem pesanan / ERP
- Pusat beli-belah atau saluran jualan
- API carrier
- Perkhidmatan cetakan kod bar / label
- Terminal handheld / PDA
- Gudang data perusahaan / BI

## 11. Risiko dan Soalan Terbuka

### 11.1 Risiko

- Perbezaan inventori menjejaskan janji jualan dan pemenuhan.
- Callback tracking carrier yang tidak stabil menjejaskan pengalaman pertanyaan pelanggan.
- Aliran kerja gudang terlalu kompleks mengurangkan kecekapan barisan hadapan.
- Peraturan batch, tarikh luput, dan beku yang tidak jelas boleh menyebabkan salah hantar atau risiko luput.

### 11.2 Soalan terbuka

- Adakah perlu menyokong berbilang gudang, berbilang pemilik barang, dan zon suhu?
- Adakah potongan inventori berlaku semasa pesanan, bayaran, atau outbound?
- Adakah strategi picking mengutamakan wave, pesanan, zon, atau batch?
- Adakah tracking carrier melalui langganan API atau import manual?
- Adakah imbasan PDA, operasi luar talian, dan bukti terima elektronik diperlukan?

## 12. Pencapaian dan Penerimaan

| Pencapaian | Tarikh sasaran | Kriteria penerimaan |
| --- | --- | --- |
| Pengesahan keperluan | T+1 minggu | Sahkan skop gudang-penghantaran, peraturan inventori, aliran kerja, dan API carrier |
| Semakan prototaip | T+3 minggu | Lengkapkan prototaip inbound, inventori, outbound, pengangkutan, dan papan pemuka |
| Pembangunan dan integrasi | T+8 minggu | Lengkapkan integrasi pesanan, gudang, carrier, dan cetakan |
| Pelancaran rintis | T+10 minggu | Rintiskan satu gudang atau barisan perniagaan |
| Pelancaran produksi | T+12 minggu | Lengkapkan rollout berbilang gudang, latihan, dan penerimaan |
