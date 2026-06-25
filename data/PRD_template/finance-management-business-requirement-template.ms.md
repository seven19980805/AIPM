# Templat Keperluan Perniagaan Pengurusan Kewangan
> Kegunaan templat: untuk senario pengurusan kewangan seperti bayaran balik perbelanjaan, kawalan bajet, permohonan bayaran, pengurusan invois, akaun belum terima/belum bayar, dan analitik kewangan.  
> Cara guna: gantikan petunjuk dalam `[]` dengan kandungan perniagaan sebenar; buang item yang tidak berkaitan.

## 1. Maklumat Asas

| Medan | Kandungan |
| --- | --- |
| Nama templat | Templat Keperluan Perniagaan Pengurusan Kewangan |
| Nama keperluan | [Contoh: Pengoptimuman pengurusan bayaran balik perbelanjaan] |
| Projek | [Masukkan nama projek] |
| Jenis keperluan | Binaan baharu / Pengoptimuman / Refaktor |
| Keutamaan | Tinggi / Sederhana / Rendah |
| Jabatan pencadang | [Masukkan jabatan] |
| Pemohon | [Masukkan nama] |
| Tarikh permohonan | [YYYY-MM-DD] |
| Versi | V1.0 |

## 2. Latar Belakang Perniagaan

### 2.1 Ringkasan Latar Belakang

[Terangkan latar operasi pengurusan kewangan semasa, skala perniagaan, proses sedia ada, dan sebab pembinaan keupayaan ini.]

Contoh: Aliran kewangan semasa tersebar di Excel, e-mel, ERP, dan kelulusan manual. Saluran data tidak seragam, kecekapan kelulusan rendah, dan kawalan bajet berlaku lewat. Apabila skala perniagaan meningkat, proses sedia ada tidak lagi mencukupi untuk pengurusan terperinci dan pematuhan audit.

### 2.2 Titik Masalah Semasa

- [Contoh: Permohonan bayaran balik masih bergantung pada aliran luar talian dan kitaran kelulusan panjang]
- [Contoh: Pelaksanaan bajet tiada semakan masa nyata dan mudah melebihi bajet]
- [Contoh: Status bayaran sukar dijejak, invois dan kontrak tersebar]
- [Contoh: Statistik kewangan tidak seragam dan penyesuaian hujung bulan mengambil masa panjang]

## 3. Objektif

### 3.1 Objektif Perniagaan

- [Contoh: Wujudkan titik masuk tunggal untuk pemprosesan perniagaan kewangan]
- [Contoh: Tingkatkan kecekapan kelulusan, semakan, dan pemprosesan bayaran]
- [Contoh: Laksanakan kawalan bajet hujung ke hujung sebelum, semasa, dan selepas perbelanjaan]
- [Contoh: Tingkatkan kebolehjejakan data dan penuhi keperluan audit]

### 3.2 Metrik Terukur

- [Contoh: Kurangkan purata masa kelulusan bayaran balik sebanyak 50%]
- [Contoh: Kurangkan kadar lebihan bajet sebanyak 80%]
- [Contoh: Pendekkan masa penyesuaian kewangan bulanan sebanyak 30%]
- [Contoh: Tingkatkan kecekapan pemprosesan permohonan bayaran sebanyak 40%]

## 4. Skop Perniagaan

### 4.1 Dalam Skop

- Permohonan perbelanjaan
- Kelulusan bayaran balik
- Muat naik dan pengesahan invois
- Penempahan dan kawalan bajet
- Permohonan dan penjejakan bayaran
- Lejar kewangan dan pelaporan

### 4.2 Di Luar Skop

- Perakaunan lejar am
- Pemfailan cukai
- Integrasi terus dengan bank
- Pelaporan konsolidasi

## 5. Peranan dan Senario Teras

### 5.1 Peranan Sasaran

- Pekerja: menyerahkan permohonan perbelanjaan, bayaran balik, dan bayaran serta menyemak kemajuan
- Ketua jabatan: menjalankan kelulusan perniagaan dan pengesahan bajet
- Pakar kewangan: menyemak dokumen, memproses bayaran, dan menyelenggara rekod lejar
- Pengurus kewangan: menjalankan semakan, pengurusan bajet, dan analisis kewangan
- Pengurusan: melihat ringkasan operasi dan kewangan
- Pentadbir sistem: menyelenggara aliran kerja, kebenaran, dan konfigurasi asas

### 5.2 Senario Perniagaan Teras

1. Pekerja memulakan permohonan perbelanjaan atau bayaran; sistem mengesahkan maklumat wajib dan baki bajet secara automatik.
2. Ketua jabatan melengkapkan kelulusan perniagaan dan menambah ulasan atau menolak apabila perlu.
3. Kewangan menyemak dokumen, invois, dan lampiran kontrak untuk memastikan pematuhan peraturan kewangan.
4. Permohonan yang diluluskan masuk ke proses bayaran, dan kewangan menjejak keputusan bayaran serta mengarkibkan rekod.
5. Dokumen lengkap diringkaskan secara automatik ke dalam lejar dan laporan untuk analisis serta audit.

## 6. Keperluan Fungsi

### 6.1 Gambaran Fungsi

[Ringkaskan keupayaan teras yang perlu dibina untuk keperluan pengurusan kewangan ini.]

Contoh: Keperluan ini menumpukan enam keupayaan: permohonan, kelulusan, kawalan bajet, pengurusan invois/dokumen, pengurusan bayaran, dan analitik pelaporan. Matlamatnya ialah menyambungkan rantaian pemprosesan kewangan serta meningkatkan standardisasi dan kecekapan.

### 6.2 Butiran Fungsi

#### Fungsi 1: Pengurusan Permohonan

- Penerangan: Menyokong pekerja memulakan permohonan perbelanjaan, bayaran balik, atau bayaran.
- Cara dicetuskan: Pengguna menekan "Permohonan Baharu" dalam sistem.
- Logik pemprosesan:
  - Menyokong simpan draf, hantar, tarik balik, dan salin permohonan
  - Mengesahkan medan wajib, format amaun, dan kelengkapan lampiran
  - Menjana nombor permohonan secara automatik
- Input:
  - Jenis permohonan
  - Jabatan
  - Kategori perbelanjaan
  - Amaun
  - Maklumat projek / kontrak / pembekal
  - Lampiran
- Output:
  - Borang permohonan
  - Status permohonan
  - Rekod operasi
- Kes pengecualian:
  - Medan wajib tiada
  - Format amaun tidak sah
  - Lampiran tiada

#### Fungsi 2: Pengurusan Kelulusan

- Penerangan: Menyokong konfigurasi aliran kelulusan mengikut struktur organisasi dan peraturan perniagaan.
- Cara dicetuskan: Permohonan yang dihantar masuk secara automatik ke aliran kelulusan.
- Logik pemprosesan:
  - Menyokong kelulusan berperingkat, kelulusan bersama, penandatangan tambahan, dan penolakan
  - Keputusan kelulusan memacu perubahan status dan laluan dokumen
  - Mencetuskan peringatan untuk kelulusan lewat
- Input:
  - Konfigurasi nod kelulusan
  - Ulasan kelulusan
  - Keputusan kelulusan
- Output:
  - Rekod kelulusan
  - Status aliran kerja
  - Pemberitahuan
- Kes pengecualian:
  - Pelulus tiada
  - Kelulusan lewat
  - Konfigurasi aliran kerja tidak sah

#### Fungsi 3: Kawalan Bajet

- Penerangan: Melaksanakan pengesahan dan penempahan bajet semasa peringkat permohonan dan semakan kewangan.
- Cara dicetuskan: Dicetuskan apabila permohonan dihantar atau disemak oleh kewangan.
- Logik pemprosesan:
  - Mengesahkan bajet mengikut jabatan, projek, dan kategori perbelanjaan
  - Menyokong penempahan, pelepasan, dan statistik pelaksanaan bajet
  - Mengarahkan item melebihi bajet ke kelulusan khas atau aliran amaran
- Input:
  - Dimensi bajet
  - Amaun bajet
  - Amaun permohonan semasa
- Output:
  - Keputusan pengesahan bajet
  - Rekod penempahan bajet
  - Amaran bajet
- Kes pengecualian:
  - Bajet belum dikonfigurasi
  - Baki bajet tidak mencukupi
  - Dimensi bajet tidak sepadan

#### Fungsi 4: Pengurusan Invois dan Dokumen

- Penerangan: Menyokong pengurusan invois, kontrak, baucar bayaran, dan lampiran lain.
- Cara dicetuskan: Dicetuskan apabila pengguna memuat naik dokumen atau kewangan menyemak dokumen.
- Logik pemprosesan:
  - Menyokong kemasukan maklumat invois, muat naik lampiran, dan pautan dokumen
  - Menyokong semakan invois pendua dan pengesahan kelengkapan
  - Menyokong penyelenggaraan status dokumen
- Input:
  - Nombor invois
  - Amaun invois
  - Tarikh terbitan
  - Fail lampiran
  - Nombor kontrak berkaitan
- Output:
  - Rekod dokumen
  - Keputusan semakan pendua
  - Status semakan
- Kes pengecualian:
  - Invois pendua
  - Maklumat invois tidak konsisten dengan amaun permohonan
  - Lampiran dokumen rosak atau tiada

#### Fungsi 5: Pengurusan Bayaran

- Penerangan: Menyokong semakan bayaran, pelaksanaan bayaran, dan penjejakan keputusan.
- Cara dicetuskan: Bermula selepas semakan kewangan diluluskan.
- Logik pemprosesan:
  - Mengesahkan maklumat penerima dan syarat bayaran
  - Merekod status bayaran dan baucar
  - Menyokong tulis balik dan arkib selepas bayaran selesai
- Input:
  - Maklumat penerima
  - Amaun bayaran
  - Akaun bayaran
  - Nota bayaran
- Output:
  - Arahan bayaran
  - Status bayaran
  - Baucar bayaran
- Kes pengecualian:
  - Maklumat penerima tiada
  - Bayaran gagal
  - Risiko bayaran pendua

#### Fungsi 6: Pelaporan dan Analitik

- Penerangan: Menyediakan analisis statistik mengikut dimensi perbelanjaan, bajet, bayaran, dan lain-lain.
- Cara dicetuskan: Dicetuskan apabila pengguna menyoal laporan atau sistem menjalankan ringkasan berjadual.
- Logik pemprosesan:
  - Menyokong penapisan mengikut masa, jabatan, projek, dan kategori perbelanjaan
  - Menyokong eksport Excel
  - Menyokong paparan ringkasan untuk pengurusan
- Input:
  - Syarat carian
  - Dimensi statistik
  - Julat masa
- Output:
  - Laporan ringkasan perbelanjaan
  - Laporan pelaksanaan bajet
  - Laporan kemajuan bayaran
- Kes pengecualian:
  - Data tiada
  - Definisi data tidak konsisten
  - Eksport gagal

## 7. Peraturan Perniagaan

- Setiap permohonan mesti dikaitkan dengan kategori perbelanjaan, jabatan, tarikh berlaku, dan maklumat asas lain.
- Permohonan melebihi bajet tidak boleh diluluskan terus dan mesti masuk ke kelulusan khas atau aliran peringatan kuat.
- Invois, kontrak, baucar bayaran, dan lampiran lain mesti dikaitkan dengan borang permohonan dan diarkibkan.
- Semakan kewangan hanya bermula selepas kelulusan; bayaran hanya bermula selepas semakan kewangan diluluskan.
- Penolakan oleh kewangan mesti menyatakan sebab dan menyimpan rekod pemprosesan.
- Permohonan perniagaan yang sama tidak boleh dihantar untuk bayaran berulang kali.
- Selepas bayaran selesai, status permohonan mesti dikemas kini secara automatik kepada Dibayar atau status setara.

## 8. Cadangan Halaman dan Interaksi

#### Halaman 1: Senarai Permohonan

- Titik masuk: Laman Utama Pengurusan Kewangan / Permohonan Saya
- Elemen halaman: kawasan penapis, senarai permohonan, label status, butang eksport
- Tindakan butang: cipta permohonan, lihat butiran, tarik balik, eksport

#### Halaman 2: Butiran Permohonan

- Titik masuk: klik daripada senarai permohonan
- Elemen halaman: maklumat asas, butiran perbelanjaan, kawasan lampiran, rekod kelulusan, keputusan pengesahan bajet
- Tindakan butang: hantar, simpan draf, edit, muat naik lampiran

#### Halaman 3: Halaman Pemprosesan Kelulusan

- Titik masuk: Pusat tugasan / Tugasan kelulusan
- Elemen halaman: maklumat permohonan, maklumat lampiran, kotak ulasan kelulusan, peringatan bajet, nod aliran kerja
- Tindakan butang: lulus, tolak, pindah, tambah penandatangan

#### Halaman 4: Halaman Pemprosesan Bayaran

- Titik masuk: Meja kerja kewangan / Bayaran menunggu
- Elemen halaman: maklumat bayaran, maklumat penerima, kawasan muat naik baucar, status bayaran
- Tindakan butang: sahkan bayaran, muat naik baucar, tanda gagal

#### Halaman 5: Halaman Laporan Kewangan

- Titik masuk: Analitik Kewangan / Pusat Laporan
- Elemen halaman: penapis, kad metrik, carta, jadual butiran
- Tindakan butang: cari, eksport, tukar dimensi statistik

### 8.1 Aliran Interaksi

1. Pengguna mencipta dan menghantar permohonan.
2. Sistem mengesahkan medan wajib, bajet, dan kelengkapan lampiran.
3. Pelulus melengkapkan kelulusan, kemudian kewangan menjalankan semakan.
4. Selepas semakan lulus, permohonan masuk ke pemprosesan bayaran dan keputusan akhir ditulis balik.
5. Data disegerakkan ke dalam laporan dan lejar.

## 9. Data dan Kebergantungan

### 9.1 Item Data Utama

- Nombor permohonan
- Pemohon
- Jabatan
- Kategori perbelanjaan
- Nama projek
- Amaun
- Maklumat invois
- Nombor kontrak
- Amaun bajet dan baki
- Status kelulusan
- Status bayaran
- Masa cipta, masa kemas kini, pengendali

### 9.2 Kebergantungan Luaran

- Data struktur organisasi
- Data maklumat pekerja
- Data induk bajet
- Data induk pembekal dan penerima bayaran
- Sistem luaran ERP / OA / HR

## 10. Keperluan Kebenaran dan Kawalan Risiko

- Pekerja hanya boleh melihat dan memproses data permohonan sendiri.
- Ketua jabatan boleh melihat data menunggu dan diluluskan yang berkaitan dengan jabatan mereka.
- Kakitangan kewangan boleh melihat dan memproses semua dokumen kewangan.
- Pengurusan boleh melihat laporan ringkasan tetapi tidak boleh mengubah dokumen perniagaan.
- Semua operasi penting mesti direkodkan untuk memenuhi keperluan audit.
- Senario risiko tinggi seperti bajet tidak mencukupi, invois pendua, dan bayaran pendua mesti mencetuskan peringatan kuat atau sekatan.

## 11. Keperluan Bukan Fungsi

- Masa respons halaman tidak boleh melebihi 3 saat.
- Menyokong sekurang-kurangnya [masukkan bilangan] pengguna serentak dalam talian.
- Penghantaran dan penyimpanan data utama mesti disulitkan.
- Menyokong sasaran ketersediaan 99.9%.
- Menyokong kelulusan di PC dan peranti mudah alih.

## 12. Kriteria Penerimaan

- Proses permohonan, kelulusan, semakan, bayaran, dan arkib boleh berjalan hujung ke hujung.
- Logik pengesahan bajet memenuhi jangkaan perniagaan.
- Peraturan semakan invois pendua dan pengesahan lampiran berfungsi.
- Data laporan konsisten dengan data dokumen perniagaan.
- Pengasingan kebenaran betul dan akses tanpa kebenaran disekat.
- Semua nod penting mempunyai log audit.

## 13. Risiko dan Soalan Terbuka

### 13.1 Risiko

- Data kewangan sejarah yang tidak konsisten boleh menjejaskan migrasi dan penyesuaian.
- Peraturan kelulusan yang kompleks boleh menjejaskan pelancaran jika tidak dijelaskan awal.
- Antara muka sistem luaran yang tidak stabil boleh menjejaskan penyegerakan bajet atau keputusan bayaran.

### 13.2 Soalan Terbuka

- Adakah penyegerakan dua hala masa nyata dengan ERP diperlukan?
- Patutkah senario melebihi bajet disekat atau melalui kelulusan khas?
- Adakah pengesahan invois perlu disambungkan kepada keupayaan pengesahan luaran?
- Patutkah statistik laporan mengikut definisi kewangan atau definisi perniagaan?

## 14. Pelan Pencapaian

| Fasa | Tarikh |
| --- | --- |
| Pengesahan keperluan | [YYYY-MM-DD] |
| Semakan prototaip | [YYYY-MM-DD] |
| Pembangunan selesai | [YYYY-MM-DD] |
| Ujian selesai | [YYYY-MM-DD] |
| Penerimaan UAT | [YYYY-MM-DD] |
| Pelancaran produksi | [YYYY-MM-DD] |
