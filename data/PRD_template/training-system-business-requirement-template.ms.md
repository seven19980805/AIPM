# Templat Keperluan Perniagaan Sistem Latihan
> Untuk senario sistem latihan seperti pengurusan kursus, pelan latihan, kelulusan pendaftaran, pembelajaran dalam talian, peperiksaan, sijil, profil pembelajaran, dan analitik.  
> Gantikan petunjuk dalam `[]` dengan kandungan perniagaan sebenar; buang item yang tidak berkaitan.

## 1. Maklumat Asas

| Medan | Kandungan |
| --- | --- |
| Nama templat | Templat Keperluan Perniagaan Sistem Latihan |
| Nama keperluan | [Pembinaan platform latihan perusahaan] |
| Projek | [Masukkan nama projek] |
| Jenis keperluan | Binaan baharu / Pengoptimuman / Refaktor |
| Keutamaan | Tinggi / Sederhana / Rendah |
| Jabatan pemohon | [Masukkan jabatan pemohon] |
| Pemohon | [Masukkan pemohon] |
| Tarikh permintaan | [YYYY-MM-DD] |
| Versi | V1.0 |

## 2. Latar Belakang Perniagaan

### 2.1 Ringkasan latar belakang

[Huraikan latar belakang latihan, proses sedia ada, dan sebab pembinaan sistem]

Penerangan: Pelan latihan, pendaftaran kursus, rekod pembelajaran, keputusan peperiksaan, dan sijil kini tersebar di e-mel, hamparan, dan beberapa platform. Pentadbir latihan sukar menjejak pelaksanaan, pelajar tiada satu laluan masuk pembelajaran, dan pengurusan kekurangan data keberkesanan latihan yang boleh dianalisis.

### 2.2 Masalah semasa

- [Penerbitan pelan latihan dan pendaftaran bergantung pada notifikasi manual]
- [Sumber kursus tersebar dan kemajuan pembelajaran sukar dijejak secara seragam]
- [Keputusan peperiksaan, sijil, dan profil pembelajaran tidak diarkibkan secara automatik]
- [Definisi data latihan tidak seragam dan laporan mengambil banyak kerja manual]

## 3. Objektif Perniagaan

### 3.1 Objektif perniagaan

- [Wujudkan satu laluan masuk untuk pelan latihan, kursus, dan pembelajaran]
- [Sokong pengurusan tertutup pendaftaran, pembelajaran, peperiksaan, dan sijil]
- [Tingkatkan kecekapan pelaksanaan latihan dan ketepatan rekod pembelajaran]
- [Bina data latihan yang boleh dianalisis untuk keputusan pembangunan bakat]

### 3.2 Metrik kuantitatif

- [Kurangkan masa pemprosesan pendaftaran kursus sebanyak 50%]
- [Capai ketepatan statistik tamat pembelajaran sebanyak 98%]
- [Jana dan arkibkan 90% sijil secara automatik]
- [Kurangkan kerja penyediaan laporan latihan manual sebanyak 60%]

## 4. Skop Perniagaan

### 4.1 Dalam skop

- Pengurusan kursus dan kandungan
- Penerbitan pelan latihan
- Pendaftaran dan kelulusan pelajar
- Pembelajaran dalam talian dan jejak kemajuan
- Peperiksaan, penilaian, dan pengurusan markah
- Sijil dan profil pembelajaran
- Laporan dan analitik latihan

### 4.2 Di luar skop

- Membangunkan enjin kelas langsung asas dari awal
- Transaksi pasaran LMS yang kompleks
- Perolehan kandungan mendalam daripada platform universiti luar
- Cadangan laluan pembelajaran peribadi berasaskan AI

## 5. Peranan dan Senario Teras

### 5.1 Peranan sasaran

- Pelajar: semak kursus, daftar latihan, belajar kandungan, ambil peperiksaan, dan lihat sijil
- Pengajar: selenggara bahan pengajaran, lihat senarai pelajar, dan semak maklum balas
- Pentadbir latihan: cipta pelan, urus pendaftaran, konfigurasi peperiksaan dan sijil
- Ketua jabatan: luluskan pendaftaran pasukan dan lihat kemajuan pembelajaran pasukan
- Pengurusan: lihat liputan, kadar tamat, kadar lulus, dan metrik keberkesanan latihan
- Pentadbir sistem: selenggara kebenaran, kategori, kamus, dan konfigurasi asas

### 5.2 Senario perniagaan teras

1. Pentadbir latihan menerbitkan pelan latihan dan membuka pendaftaran kepada kumpulan sasaran.
2. Pelajar memilih kursus dalam portal latihan, menghantar pendaftaran, dan menerima notifikasi.
3. Ketua jabatan meluluskan pendaftaran ahli pasukan, dan sistem mengemas kini status pendaftaran.
4. Pelajar melengkapkan pembelajaran dalam talian dan mengambil penilaian.
5. Sistem menjana sijil berdasarkan peraturan tamat dan menyimpan profil pembelajaran.
6. Pengurusan menyemak kadar tamat, kadar lulus peperiksaan, dan maklum balas kursus.

## 6. Keperluan Fungsi

### 6.1 Gambaran fungsi

[Ringkaskan keupayaan teras yang perlu dibina untuk sistem latihan]

Penerangan: Keperluan ini merangkumi tujuh kumpulan keupayaan: sumber kursus, pelan latihan, kelulusan pendaftaran, kemajuan pembelajaran, peperiksaan dan penilaian, sijil dan profil pembelajaran, serta analitik.

### 6.2 Butiran fungsi

#### 6.2.1 Pengurusan kursus dan kandungan

- Penerangan: Menyelenggara kategori kursus, maklumat kursus, bahan kandungan, pengajar, dan kumpulan sasaran.
- Pencetus: Pentadbir latihan mencipta atau mengemas kini kursus.
- Peraturan / logik perniagaan:
-   Sokong penerbitan, penarikan balik, kategori, tag, dan penyelenggaraan peranan sasaran
-   Sokong video, dokumen, tugasan, dan lampiran kandungan lain
-   Sokong versi kursus dan sejarah kemas kini
- Input: Nama kursus, kategori, pengajar, kandungan, kumpulan sasaran
- Output: Butiran kursus, katalog, senarai kandungan
- Pengendalian pengecualian: Kursus berulang, kandungan hilang, sekatan padam apabila dirujuk oleh pelan

#### 6.2.2 Pelan latihan dan kelulusan pendaftaran

- Penerangan: Menerbitkan pelan latihan dan mengurus pendaftaran, kelulusan, kuota, dan notifikasi.
- Pencetus: Pelan dicipta atau pendaftaran dihantar.
- Peraturan / logik perniagaan:
-   Sokong pendaftaran mengikut organisasi, peranan, atau individu tertentu
-   Sokong kawalan kuota, senarai menunggu, pembatalan, dan aliran kelulusan
-   Sokong notifikasi pendaftaran, kelulusan, dan mula kelas
- Input: Nama pelan, kursus, jadual, kuota, kumpulan sasaran, pelulus
- Output: Pelan latihan, senarai pendaftaran, keputusan kelulusan
- Pengendalian pengecualian: Kuota penuh, tarikh tutup tamat, pendaftaran berulang, kelulusan lewat

#### 6.2.3 Pembelajaran dalam talian dan jejak kemajuan

- Penerangan: Menyediakan satu laluan masuk pembelajaran dan merekod kemajuan.
- Pencetus: Pelajar memulakan pembelajaran kursus.
- Peraturan / logik perniagaan:
-   Sokong katalog kursus, kemajuan pembelajaran, tempoh, dan status tamat
-   Sokong sambung belajar, penanda wajib/opsyen, dan peringatan
-   Sokong peringatan pembelajaran tertunggak
- Input: Pelajar, kursus, kandungan, tempoh, status tamat
- Output: Rekod pembelajaran, statistik kemajuan, bukti tamat
- Pengendalian pengecualian: Kegagalan main kandungan, kegagalan laporan kemajuan, gabungan rekod berulang

#### 6.2.4 Peperiksaan, penilaian, dan pengurusan markah

- Penerangan: Mengkonfigurasi bank soalan, kertas, sesi peperiksaan, pemarkahan, dan statistik markah.
- Pencetus: Pelan memerlukan peperiksaan atau pentadbir menerbitkannya.
- Peraturan / logik perniagaan:
-   Sokong tetapan bank soalan, kertas, masa peperiksaan, dan markah lulus
-   Sokong pemarkahan automatik, pemarkahan manual, dan peperiksaan ulangan
-   Sokong semakan markah, statistik kadar lulus, dan eksport
- Input: Soalan, kertas, tetapan peperiksaan, rekod jawapan
- Output: Slip markah, status lulus, statistik peperiksaan
- Pengendalian pengecualian: Masa tamat, penghantaran berulang, tanda penipuan, kelayakan ulangan tidak mencukupi

#### 6.2.5 Sijil dan profil pembelajaran

- Penerangan: Menjana sijil berdasarkan keputusan tamat dan peperiksaan, serta membina profil pembelajaran pekerja.
- Pencetus: Pelajar memenuhi syarat pengeluaran sijil.
- Peraturan / logik perniagaan:
-   Sokong templat sijil, peraturan nombor, dan tempoh sah
-   Sokong penjanaan, muat turun, pembatalan, dan peringatan tamat tempoh sijil
-   Gabungkan rekod pembelajaran dan sijil mengikut pekerja
- Input: Rekod tamat, markah, templat sijil, data pekerja
- Output: Sijil, profil pembelajaran, lejar sijil
- Pengendalian pengecualian: Kegagalan jana sijil, tamat tempoh, jejak audit pembatalan

#### 6.2.6 Laporan dan analitik latihan

- Penerangan: Menyediakan statistik pelaksanaan latihan, keberkesanan pembelajaran, dan penggunaan sumber.
- Pencetus: Pengurus atau pentadbir latihan melihat laporan.
- Peraturan / logik perniagaan:
-   Sokong statistik liputan dan tamat mengikut organisasi, kursus, masa, dan peranan
-   Sokong kadar lulus, penilaian kursus, dan ringkasan maklum balas
-   Sokong eksport laporan dan penghantaran berjadual
- Input: Rekod pendaftaran, rekod pembelajaran, markah, maklum balas
- Output: Papan pemuka latihan, laporan statistik, fail eksport
- Pengendalian pengecualian: Kelewatan data, kebenaran tidak mencukupi, peringatan apabila definisi statistik berubah

## 7. Halaman dan Proses

| Halaman / laluan masuk | Laluan masuk | Elemen utama | Tindakan utama | Aliran |
| --- | --- | --- | --- | --- |
| Laman utama portal latihan | Laluan masuk pelajar | Kursus disyorkan, tugasan tertunda, sijil, notifikasi | Cari kursus, daftar, sambung belajar, lihat sijil | Pelajar log masuk, menyemak tugasan, dan memasuki kursus. |
| Pengurusan kursus | Konsol pentadbir latihan | Senarai kursus, butiran kursus, kandungan, pengajar, kumpulan sasaran | Cipta kursus, edit kandungan, terbit/tarik balik, salin kursus | Pentadbir menyelenggara kursus dan menerbitkannya kepada kumpulan yang boleh melihat. |
| Pengurusan pelan latihan | Konsol pentadbir latihan | Senarai pelan, senarai pendaftaran, status kelulusan, notifikasi | Terbit pelan, laras kuota, lihat pendaftaran, eksport senarai | Pentadbir mencipta pelan, sistem membuka pendaftaran mengikut sasaran dan menghantar notifikasi. |
| Pengurusan peperiksaan dan sijil | Konsol pentadbir latihan | Bank soalan, kertas, tetapan peperiksaan, markah, templat sijil | Konfigurasi peperiksaan, tanda markah, jana sijil, batal sijil | Selepas peperiksaan tamat, sistem merumuskan markah dan menjana sijil mengikut peraturan. |
| Papan pemuka analitik latihan | Laluan masuk pengurusan | Liputan, tamat, kadar lulus, penilaian kursus, trend | Tapis, telusuri, eksport, langgan | Pengurusan menyemak keberkesanan latihan mengikut organisasi dan masa. |

## 8. Peraturan Perniagaan dan Data

### 8.1 Peraturan / logik perniagaan

- Selepas tarikh tutup, pendaftaran ditutup secara lalai; pentadbir boleh menambah rekod dengan kebenaran.
- Seorang pelajar hanya boleh mempunyai satu rekod pendaftaran aktif untuk pelan latihan yang sama.
- Tamat kursus boleh bergantung pada kemajuan, tempoh, penghantaran tugasan, dan lulus peperiksaan.
- Nombor sijil mesti unik secara global dan tidak boleh digunakan semula selepas pembatalan.
- Perubahan pada markah dan sijil mesti menyimpan jejak audit.

### 8.2 Objek data utama

- Kursus: kod, nama, kategori, pengajar, kandungan, kumpulan sasaran, status
- Pelan latihan: kod, kursus, jadual, kuota, kumpulan sasaran, peraturan kelulusan
- Rekod pendaftaran: pelajar, pelan, status, pelulus, masa kelulusan
- Rekod pembelajaran: pelajar, kursus, kemajuan, tempoh, status tamat, masa tamat
- Markah peperiksaan: peperiksaan, pelajar, markah, status lulus, status pemarkahan
- Sijil: nombor, pelajar, kursus/pelan, masa pengeluaran, tempoh sah, status

## 9. Keperluan Bukan Fungsi

- Kawalan akses: keterlihatan dan operasi dikawal mengikut peranan, organisasi, dan skop data.
- Prestasi: pertanyaan senarai lazim kembali dalam 3 saat; laporan boleh dijana secara tak segerak.
- Kebolehgunaan: aliran pendaftaran dan pembelajaran utama memerlukan cuba semula dan mesej ralat yang jelas.
- Audit: kelulusan pendaftaran, suntingan markah, dan penjanaan/pembatalan sijil mesti direkodkan.
- Keselamatan: jawapan peperiksaan, markah, dan data sijil mesti diurus sebagai data sensitif.

## 10. Integrasi dan Kebergantungan

- Data induk organisasi dan pekerja
- Identiti bersatu / SSO
- Perkhidmatan notifikasi mesej
- Meterai elektronik atau perkhidmatan sijil
- Gudang data perusahaan / BI

## 11. Risiko dan Soalan Terbuka

### 11.1 Risiko

- Definisi data latihan sejarah yang tidak seragam boleh menjejaskan kualiti migrasi.
- Format kandungan dan keupayaan main balik yang berbeza boleh menjejaskan pengalaman belajar.
- Keperluan anti-penipuan peperiksaan dan pematuhan sijil perlu disahkan awal.
- Sempadan kebenaran berbilang organisasi yang tidak jelas boleh menjejaskan pengasingan data.

### 11.2 Soalan terbuka

- Adakah pelan latihan perlu menyokong pendaftaran rentas syarikat atau peserta luar?
- Adakah peraturan tamat kursus perlu berbeza mengikut kursus, pelan, atau peranan?
- Adakah sijil memerlukan meterai elektronik, pengesahan QR, atau tempoh sah?
- Adakah peperiksaan memerlukan had masa, kertas rawak, anti-penipuan, dan peraturan ulangan?
- Modul latihan manakah yang perlu menjadi halaman bebas dalam produk akhir?

## 12. Pencapaian dan Penerimaan

| Pencapaian | Tarikh sasaran | Kriteria penerimaan |
| --- | --- | --- |
| Pengesahan keperluan | T+1 minggu | Sahkan skop, peranan, aliran teras, dan definisi laporan |
| Semakan prototaip | T+3 minggu | Lengkapkan prototaip halaman utama dan semakan proses |
| Pembangunan dan integrasi | T+8 minggu | Lengkapkan pembangunan fungsi teras dan integrasi luaran |
| Pelancaran rintis | T+10 minggu | Lancarkan organisasi rintis dan tutup isu rintis |
| Pelancaran produksi | T+12 minggu | Lengkapkan pelancaran penuh, latihan, dan penerimaan |
