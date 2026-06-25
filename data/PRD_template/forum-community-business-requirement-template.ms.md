# Templat Keperluan Perniagaan Sistem Forum Komuniti
> Untuk senario forum dan komuniti seperti pengurusan papan, penerbitan thread, balasan, interaksi, pertumbuhan pengguna, moderasi kandungan, pengendalian laporan, carian, cadangan, dan analitik komuniti.  
> Gantikan petunjuk dalam `[]` dengan kandungan perniagaan sebenar; buang item yang tidak berkaitan.

## 1. Maklumat Asas

| Medan | Kandungan |
| --- | --- |
| Nama templat | Templat Keperluan Perniagaan Sistem Forum Komuniti |
| Nama keperluan | [Pembinaan forum komuniti minat] |
| Projek | [Masukkan nama projek] |
| Jenis keperluan | Binaan baharu / Pengoptimuman / Refaktor |
| Keutamaan | Tinggi / Sederhana / Rendah |
| Jabatan pemohon | [Masukkan jabatan pemohon] |
| Pemohon | [Masukkan pemohon] |
| Tarikh permintaan | [YYYY-MM-DD] |
| Versi | V1.0 |

## 2. Latar Belakang Perniagaan

### 2.1 Ringkasan latar belakang

[Huraikan latar belakang komuniti forum, cara komunikasi semasa, dan sebab pembinaan sistem]

Penerangan: Perbincangan pengguna, perkongsian pengalaman, dan kandungan Q&A kini tersebar di kumpulan chat, hamparan, dan dokumen sementara. Kandungan sukar disimpan, carian lemah, dan pelanggaran peraturan bergantung pada rondaan manual. Sistem forum komuniti seperti Tieba diperlukan untuk menyokong perbincangan berthread, tadbir urus papan, moderasi kandungan, dan analitik komuniti.

### 2.2 Masalah semasa

- [Kandungan perbincangan sukar distruktur, disimpan, dan dicari semula]
- [Papan, thread, balasan, dan hubungan pengguna tiada pengurusan bersatu]
- [Pelanggaran ditemui dan ditangani lewat, dan moderasi kurang jejak audit]
- [Kandungan popular, pengguna aktif, dan kualiti komuniti tiada papan pemuka]

## 3. Objektif Perniagaan

### 3.1 Objektif perniagaan

- [Bina struktur papan dan thread mengikut minat atau topik perniagaan]
- [Sokong gelung interaksi lengkap untuk siaran, balasan, suka, simpan, ikuti, dan notifikasi]
- [Bina tadbir urus kandungan untuk laporan, moderasi, sekatan, rayuan, dan audit operasi]
- [Kumpul data operasi komuniti untuk cadangan dan keputusan operasi]

### 3.2 Metrik kuantitatif

- [Purata masa daripada penerbitan hingga kelihatan dalam 3 saat]
- [Kurangkan purata masa pengendalian moderasi sebanyak 50%]
- [Tingkatkan kadar hit carian komuniti kepada 90%]
- [Jejak pengguna aktif harian dan jumlah siaran mengikut papan teras]

## 4. Skop Perniagaan

### 4.1 Dalam skop

- Pengurusan papan dan konfigurasi kebenaran
- Penerbitan, suntingan, padam, pin, dan sorotan thread
- Balasan, komen, balasan bersarang, dan interaksi
- Profil pengguna, ikutan, tahap, mata, dan lencana
- Laporan, moderasi, sembunyi, sekatan, dan rayuan
- Carian, susunan, cadangan, dan papan pemuka analitik

### 4.2 Di luar skop

- Chat kumpulan mesej segera
- Alat penciptaan video pendek yang kompleks
- Sistem penyampaian iklan luaran
- Penghakiman kandungan AI sepenuhnya automatik

## 5. Peranan dan Senario Teras

### 5.1 Peranan sasaran

- Pelawat: semak papan dan thread awam, cari kandungan
- Pengguna berdaftar: terbit thread, balas, suka, simpan, ikuti, dan lapor
- Moderator papan: urus peraturan papan, pin/sorot siaran, dan tangani pelanggaran
- Penyemak: semak siaran baharu, laporan, dan kandungan sensitif
- Operator: konfigurasi cadangan, kempen, tag, dan papan pemuka
- Pentadbir sistem: selenggara kebenaran, kamus, kata sensitif, dan parameter sistem

### 5.2 Senario perniagaan teras

1. Pengguna masuk ke halaman utama forum dan menuju ke thread menarik melalui papan, senarai panas, atau carian.
2. Pengguna berdaftar menerbitkan thread dalam papan sasaran dan memuat naik imej atau lampiran.
3. Pengguna lain membalas, suka, simpan, atau mengikuti penulis, dan sistem menghantar notifikasi interaksi.
4. Pengguna melaporkan kandungan melanggar peraturan, dan penyemak memprosesnya dalam konsol moderasi dengan sebab direkodkan.
5. Moderator mempin atau menyorot siaran berkualiti, sementara operator mengkonfigurasi slot cadangan.
6. Pengurusan melihat jumlah siaran, jumlah balasan, pengguna aktif, laporan, dan kecekapan moderasi.

## 6. Keperluan Fungsi

### 6.1 Gambaran fungsi

[Ringkaskan keupayaan teras yang perlu dibina untuk sistem forum]

Penerangan: Keperluan ini merangkumi tujuh kumpulan keupayaan: tadbir urus papan, penerbitan kandungan, interaksi, pertumbuhan pengguna, moderasi dan kawalan risiko, carian dan cadangan, serta analitik komuniti.

### 6.2 Butiran fungsi

#### 6.2.1 Pengurusan papan dan moderator

- Penerangan: Menyelenggara kategori papan, profil papan, peraturan, moderator, dan kebenaran akses.
- Pencetus: Operator mencipta atau melaras papan.
- Peraturan / logik perniagaan:
-   Sokong penciptaan, nyahaktif, gabung, susun, dan konfigurasi keterlihatan papan
-   Sokong peraturan papan, pengumuman, tag, dan kebenaran moderator
-   Sokong statistik papan dan amaran anomali
- Input: Nama papan, kategori, peraturan, moderator, skop kebenaran
- Output: Butiran papan, pengumuman, senarai moderator, statistik
- Pengendalian pengecualian: Nama papan berulang, padam disekat apabila ada siaran, konflik kebenaran

#### 6.2.2 Penerbitan thread dan suntingan kandungan

- Penerangan: Sokong penerbitan thread, draf, teks kaya, imej, lampiran, dan tag.
- Pencetus: Pengguna klik terbit atau edit.
- Peraturan / logik perniagaan:
-   Sokong tajuk, isi, imej, lampiran, tag, dan pilihan tanpa nama
-   Sokong simpan draf, sejarah suntingan, padam, dan pulih
-   Sokong pin, sorot, kunci, dan turunkan siaran
- Input: Tajuk, isi, papan, tag, lampiran, penulis
- Output: Thread, draf, rekod suntingan, status pengurusan
- Pengendalian pengecualian: Kata sensitif dikesan, had lampiran melebihi, siaran berulang, tiada kebenaran

#### 6.2.3 Balasan, komen, dan interaksi

- Penerangan: Sokong balasan, komen bersarang, suka, simpan, ikuti, dan notifikasi.
- Pencetus: Pengguna berinteraksi dengan thread atau balasan.
- Peraturan / logik perniagaan:
-   Sokong susunan, petikan, lipat, dan padam balasan
-   Sokong suka, simpan, ikuti penulis/thread, dan notifikasi interaksi
-   Sokong sekat pengguna dan maklum balas tidak berminat
- Input: Thread, balasan, pengguna, jenis interaksi
- Output: Senarai balasan, rekod interaksi, notifikasi
- Pengendalian pengecualian: Had tindakan kerap, sekatan pengguna disekat, kandungan telah dipadam

#### 6.2.4 Pertumbuhan pengguna dan aset komuniti

- Penerangan: Menyelenggara profil pengguna, tahap, mata, lencana, dan rekod sumbangan.
- Pencetus: Pengguna melengkapkan siaran, interaksi, daftar masuk, atau tugasan kempen.
- Peraturan / logik perniagaan:
-   Sokong peraturan mata, peraturan tahap, pengeluaran lencana, dan konfigurasi tugasan
-   Paparkan siaran, simpanan, ikutan, dan pengikut dalam profil pengguna
-   Sokong potongan mata pelanggaran, senyap, dan pemulihan kredit
- Input: Profil pengguna, rekod tingkah laku, peraturan mata, peraturan lencana
- Output: Profil pengguna, lejar mata, keputusan tahap, rekod lencana
- Pengendalian pengecualian: Perladangan mata, undur mata, anomali akaun

#### 6.2.5 Moderasi dan pengendalian laporan

- Penerangan: Mengendalikan kandungan sensitif, laporan, semakan manual, sekatan, dan rayuan.
- Pencetus: Kandungan diterbitkan, dilaporkan, atau terkena peraturan.
- Peraturan / logik perniagaan:
-   Sokong moderasi sebelum/selepas terbit, kata sensitif, dan semakan imej
-   Sokong penerimaan laporan, kesimpulan, tindakan hukuman, dan notifikasi
-   Sokong sekatan, senyap, sembunyi kandungan, rayuan, dan audit operasi
- Input: Kandungan, sebab laporan, peraturan moderasi, pengendali
- Output: Keputusan moderasi, rekod hukuman, rekod rayuan, log audit
- Pengendalian pengecualian: Rayuan salah nilai, laporan berulang, tamat masa moderasi, pembatalan hukuman

#### 6.2.6 Carian, cadangan, dan analitik

- Penerangan: Menyediakan carian kandungan, senarai panas, slot cadangan, dan data komuniti.
- Pencetus: Pengguna mencari kandungan atau operator melihat data.
- Peraturan / logik perniagaan:
-   Sokong carian mengikut papan, kata kunci, tag, penulis, dan masa
-   Sokong senarai thread panas, slot cadangan, kawasan sorotan, dan laluan kempen
-   Sokong papan pemuka untuk siaran, pengguna aktif, laporan, dan kecekapan moderasi
- Input: Thread, balasan, tag, tingkah laku pengguna, rekod moderasi
- Output: Hasil carian, senarai panas, senarai cadangan, laporan analitik
- Pengendalian pengecualian: Kelewatan indeks, kandungan disyorkan melanggar peraturan, penapisan kebenaran tidak lengkap

## 7. Halaman dan Proses

| Halaman / laluan masuk | Laluan masuk | Elemen utama | Tindakan utama | Aliran |
| --- | --- | --- | --- | --- |
| Laman utama forum | Laluan masuk pengguna | Papan disyorkan, senarai panas, kotak carian, laluan kempen | Cari, masuk papan, lihat thread panas, log masuk/daftar | Pengguna masuk ke laman utama dan membuka thread mengikut minat atau senarai panas. |
| Butiran papan | Laluan masuk papan | Pengumuman papan, peraturan, senarai thread, penapis dan susunan | Terbit thread, ikuti papan, tapis, lihat thread | Pengguna menyemak thread dalam papan dan memulakan perbincangan. |
| Butiran thread | Senarai thread / hasil carian | Siaran utama, balasan, balasan bersarang, interaksi, cadangan | Balas, suka, simpan, lapor, ikuti penulis | Pengguna membaca dan berinteraksi dengan thread; sistem merekod hubungan dan notifikasi. |
| Editor siaran | Butang terbit | Tajuk, isi, imej, lampiran, tag, tetapan terbit | Simpan draf, pratonton, terbit, edit | Pengguna mengedit kandungan, dan sistem mengesahkan kata sensitif serta kebenaran sebelum terbit. |
| Konsol moderasi | Backend pentadbir | Kandungan menunggu, senarai laporan, rekod pengendalian, tindakan hukuman | Semak, sembunyi, sekat, tolak, lulus, maklumkan | Penyemak mengendalikan kandungan dan meninggalkan rekod operasi. |
| Papan pemuka analitik komuniti | Backend operasi | Jumlah siaran, pengguna aktif, thread panas, jumlah laporan, kecekapan moderasi | Tapis, telusuri, eksport, konfigurasi cadangan | Operator menyemak kualiti dan pertumbuhan komuniti. |

## 8. Peraturan Perniagaan dan Data

### 8.1 Peraturan / logik perniagaan

- Had kekerapan siaran boleh dikonfigurasi mengikut tahap pengguna dalam setiap papan.
- Penerbitan memerlukan semakan kata sensitif, keselamatan imej, dan kebenaran.
- Kandungan dipadam atau disembunyikan tidak kelihatan kepada pengguna biasa, tetapi rekod audit kekal di backend pentadbir.
- Pengendalian laporan mesti merekod pengendali, masa, kesimpulan, dan tindakan hukuman.
- Pin, sorotan, dan slot cadangan mesti dibenarkan mengikut peranan.

### 8.2 Objek data utama

- Papan: id, nama, kategori, peraturan, moderator, status, skop keterlihatan
- Thread: id, papan, tajuk, isi, penulis, status, kiraan interaksi, masa terbit
- Balasan: id, thread, balasan induk, penulis, isi, status, nombor tingkat
- Hubungan pengguna: ikuti, sekat, simpan, suka, rekod lihat
- Rekod moderasi: kandungan, peraturan, item terkena, pengendali, kesimpulan, tindakan hukuman
- Konfigurasi operasi: slot cadangan, peraturan senarai panas, tag, laluan kempen

## 9. Keperluan Bukan Fungsi

- Prestasi: pertanyaan lazim halaman utama dan butiran thread kembali dalam 3 saat; senarai panas boleh dicache.
- Keselamatan: lindungi identiti, kata sensitif, kandungan imej, dan kekerapan API.
- Kebolehgunaan: aliran siaran, balasan, dan laporan memerlukan cuba semula dan petunjuk jelas.
- Audit: moderasi, sekatan, padam, pulih, dan operasi cadangan mesti direkodkan.
- Kebolehkembangan: papan, tag, mata, dan peraturan moderasi perlu boleh dikonfigurasi.

## 10. Integrasi dan Kebergantungan

- Identiti bersatu / SSO
- Storan objek atau perkhidmatan lampiran
- Perkhidmatan notifikasi mesej
- Keselamatan kandungan / semakan imej
- Perkhidmatan enjin carian
- Gudang data perusahaan / BI

## 11. Risiko dan Soalan Terbuka

### 11.1 Risiko

- Komuniti terbuka boleh menghasilkan spam, iklan, dan kandungan melanggar peraturan; strategi tadbir urus mesti jelas.
- Kata sensitif dan peraturan moderasi terlalu ketat boleh menjejaskan perbincangan biasa.
- Peraturan senarai panas dan cadangan yang tidak telus boleh mencetuskan pertikaian operasi.
- Migrasi kandungan sejarah mungkin memerlukan pembersihan data dan pemetaan kebenaran.

### 11.2 Soalan terbuka

- Adakah pelawat dibenarkan menyiarkan kandungan, atau hanya pengguna berdaftar?
- Adakah siaran perlu disemak sebelum terbit atau diperiksa selepas terbit?
- Apakah sempadan kebenaran dan proses pelantikan untuk moderator papan?
- Adakah tahap, mata, lencana, dan daftar masuk diperlukan?
- Siapa menyelenggara peraturan senarai panas, slot cadangan, dan ranking carian?

## 12. Pencapaian dan Penerimaan

| Pencapaian | Tarikh sasaran | Kriteria penerimaan |
| --- | --- | --- |
| Pengesahan keperluan | T+1 minggu | Sahkan peranan, skop, aliran teras, dan strategi moderasi |
| Semakan prototaip | T+3 minggu | Lengkapkan prototaip halaman utama, papan, thread, editor, dan konsol moderasi |
| Pembangunan dan integrasi | T+8 minggu | Lengkapkan fungsi teras serta integrasi keselamatan kandungan dan carian |
| Pelancaran rintis | T+10 minggu | Rintiskan papan terpilih dan tutup isu |
| Pelancaran produksi | T+12 minggu | Lengkapkan pelancaran penuh, konfigurasi operasi, dan penerimaan |
