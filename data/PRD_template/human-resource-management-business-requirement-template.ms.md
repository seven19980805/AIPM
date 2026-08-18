# Templat Keperluan Perniagaan Pengurusan Sumber Manusia
> Kegunaan templat: untuk senario HR seperti profil pekerja, pengambilan dan onboarding, kehadiran dan jadual, gaji dan prestasi, latihan dan pembangunan, serta organisasi dan kebenaran.  
> Cara guna: gantikan petunjuk dalam `[]` dengan kandungan perniagaan sebenar; buang item yang tidak berkaitan.

## 1. Maklumat Asas

| Medan | Kandungan |
| --- | --- |
| Nama templat | Templat Keperluan Perniagaan Pengurusan Sumber Manusia |
| Nama keperluan | [Contoh: Pengoptimuman kitar hayat pekerja] |
| Projek | [Masukkan nama projek] |
| Jenis keperluan | Binaan baharu / Pengoptimuman / Refaktor |
| Keutamaan | Tinggi / Sederhana / Rendah |
| Jabatan pencadang | [Masukkan jabatan] |
| Pemohon | [Masukkan nama] |
| Tarikh permohonan | [YYYY-MM-DD] |
| Versi | V1.0 |

## 2. Latar Belakang Perniagaan

### 2.1 Ringkasan Latar Belakang

[Terangkan latar operasi HR semasa, skala tenaga kerja, proses sedia ada, dan sebab pembinaan keupayaan ini.]

Contoh: Proses HR semasa tersebar di hamparan, e-mel, kelulusan luar talian, dan beberapa sistem. Definisi data pekerja tidak seragam, kecekapan pengambilan dan onboarding rendah, dan data kehadiran, gaji, serta prestasi sukar dihubungkan.

### 2.2 Titik Masalah Semasa

- [Contoh: Profil pekerja diselenggara di beberapa tempat dan kemas kini lewat]
- [Contoh: Tugas daripada tawaran kerja hingga onboarding tiada penjejakan bersepadu]
- [Contoh: Peraturan kehadiran, cuti, dan kerja lebih masa bergantung pada semakan manual]
- [Contoh: Kebenaran data gaji dan prestasi yang sensitif tidak jelas]

## 3. Objektif

### 3.1 Objektif Perniagaan

- [Contoh: Wujudkan titik masuk tunggal untuk proses HR]
- [Contoh: Tingkatkan kecekapan pengambilan, onboarding, kelulusan, dan perkhidmatan pekerja]
- [Contoh: Bina data induk kitar hayat pekerja]
- [Contoh: Tingkatkan analitik tenaga kerja dan sokongan keputusan]

### 3.2 Metrik Terukur

- [Contoh: Kurangkan purata masa onboarding sebanyak 50%]
- [Contoh: Tingkatkan kelengkapan profil pekerja kepada lebih 95%]
- [Contoh: Pendekkan masa pengendalian pengecualian kehadiran sebanyak 40%]
- [Contoh: Kurangkan kemasukan data HR berulang sebanyak 60%]

## 4. Skop Perniagaan

### 4.1 Dalam Skop

- Pengurusan profil pekerja
- Aliran pengambilan dan onboarding
- Pengurusan kehadiran, cuti, dan kerja lebih masa
- Kerjasama data gaji dan prestasi
- Rekod latihan dan pembangunan
- Pengurusan organisasi, jawatan, dan kebenaran
- Laporan dan analitik HR

### 4.2 Di Luar Skop

- Enjin pengiraan gaji yang kompleks
- Pemfailan insurans sosial atau manfaat
- Integrasi mendalam dengan platform pemburu bakat luaran
- Ramalan kos tenaga kerja peringkat kumpulan

## 5. Peranan dan Senario Teras

### 5.1 Peranan Sasaran

- Pekerja: melihat maklumat peribadi dan menghantar permohonan cuti, kerja lebih masa, pembetulan, dan kemas kini profil
- Pakar HR: menyelenggara profil pekerja dan mengurus proses kitar hayat pekerja
- Perekrut: mengurus calon, tawaran, dan tugas onboarding
- Ketua jabatan: meluluskan urusan HR pasukan dan melihat status tenaga kerja pasukan
- Pakar gaji dan prestasi: menyelenggara data gaji dan prestasi
- Pengurusan: melihat metrik tenaga kerja dan indikator utama
- Pentadbir sistem: menyelenggara organisasi, jawatan, kebenaran, dan konfigurasi asas

### 5.2 Senario Perniagaan Teras

1. HR mencipta dan menyelenggara profil pekerja, manakala pekerja mengemas kini maklumat yang dibenarkan melalui self-service.
2. Selepas calon menerima tawaran, sistem memulakan tugas onboarding untuk dokumen, akaun, dan latihan.
3. Pekerja menghantar permohonan cuti, kerja lebih masa, atau pembetulan kehadiran; sistem mengesahkan peraturan kehadiran.
4. Ketua jabatan meluluskan permohonan pasukan dan melihat status tenaga kerja, kehadiran, serta prestasi.
5. Pengurusan menyemak jumlah pekerja, kadar keluar masuk, kemajuan pengambilan, taburan prestasi, dan trend kos tenaga kerja.

## 6. Keperluan Fungsi

### 6.1 Gambaran Fungsi

[Ringkaskan keupayaan teras yang perlu dibina untuk keperluan pengurusan HR ini.]

Contoh: Keperluan ini menumpukan profil pekerja, pengambilan dan onboarding, kehadiran dan cuti, gaji dan prestasi, latihan dan pembangunan, serta analitik HR. Matlamatnya ialah menghubungkan aliran kerja HR utama dengan data induk pekerja.

### 6.2 Butiran Fungsi

#### Fungsi 1: Pengurusan Profil Pekerja

- Penerangan: Menyokong penyelenggaraan maklumat asas pekerja, maklumat pekerjaan, kontrak, dan lampiran.
- Cara dicetuskan: HR mencipta pekerja atau pekerja menghantar permohonan kemas kini profil.
- Logik pemprosesan:
  - Menjana dan mengesahkan nombor pekerja unik secara automatik
  - Menyokong perubahan status: menunggu onboarding, aktif, berhenti, dinyahaktifkan
  - Menyimpan sejarah audit untuk perubahan medan penting dan kelulusan
- Input: nama pekerja, organisasi, tahap jawatan, tarikh onboarding, maklumat kontrak, lampiran
- Output: profil pekerja, rekod perubahan, rekod status
- Kes pengecualian: nombor pekerja pendua, data wajib tiada, format lampiran tidak sah

#### Fungsi 2: Pengambilan dan Onboarding

- Penerangan: Menyokong pengurusan proses daripada pengesahan tawaran hingga tugas onboarding selesai.
- Cara dicetuskan: Perekrut mengesahkan penerimaan tawaran calon.
- Logik pemprosesan:
  - Menjana senarai semak onboarding dan nod tugas secara automatik
  - Menyokong kutipan dokumen, pembukaan akaun, penyediaan peranti, dan susunan latihan
  - Menukar rekod onboarding kepada profil pekerja rasmi selepas selesai
- Input: maklumat calon, tarikh onboarding, maklumat jawatan, dokumen onboarding
- Output: tugas onboarding, status onboarding, profil pekerja
- Kes pengecualian: dokumen tiada, tarikh onboarding berubah, tugas lewat

#### Fungsi 3: Pengurusan Kehadiran dan Cuti

- Penerangan: Menyokong cuti, kerja lebih masa, pembetulan kehadiran, perjalanan kerja, dan permohonan berkaitan kehadiran.
- Cara dicetuskan: Pekerja menghantar permohonan kehadiran atau sistem menyegerakkan pengecualian kehadiran.
- Logik pemprosesan:
  - Mengesahkan mengikut organisasi, syif, baki cuti, dan peraturan kelulusan
  - Menyokong peringatan pengecualian kehadiran dan pengendalian tertutup
  - Menyegerakkan keputusan ke statistik kehadiran
- Input: jenis permohonan, julat masa, sebab, lampiran, ulasan kelulusan
- Output: borang permohonan, rekod kelulusan, keputusan kehadiran
- Kes pengecualian: baki cuti tidak mencukupi, konflik masa, pelulus tiada

#### Fungsi 4: Kerjasama Gaji dan Prestasi

- Penerangan: Menyokong paparan dan pengesahan keputusan gaji dan prestasi yang dibenarkan serta dipautkan kepada data induk pekerja.
- Cara dicetuskan: Pakar gaji atau prestasi mengimport atau mengemas kini data berkaitan.
- Logik pemprosesan:
  - Menyelenggara keputusan gaji dan prestasi mengikut tempoh
  - Memberi kebenaran medan sensitif mengikut peranan dan skop data
  - Menyokong pekerja melihat keputusan sendiri dan rekod pengesahan
- Input: tempoh gaji, tempoh prestasi, data keputusan, status pengesahan
- Output: rekod gaji/prestasi, rekod pengesahan, statistik
- Kes pengecualian: definisi data tidak konsisten, kebenaran tidak mencukupi, import gagal

#### Fungsi 5: Latihan dan Pembangunan

- Penerangan: Menyokong pelan latihan, pendaftaran, rekod selesai, dan profil pembangunan pekerja.
- Cara dicetuskan: HR menerbitkan pelan latihan atau pekerja mendaftar.
- Logik pemprosesan:
  - Menyokong penerbitan latihan, semakan pendaftaran, dan rekod kehadiran
  - Menyimpan rekod selesai ke profil pembangunan pekerja
  - Menyokong statistik keberkesanan latihan
- Input: topik latihan, kumpulan sasaran, masa dan lokasi, maklumat pendaftaran, keputusan selesai
- Output: pelan latihan, senarai pendaftaran, rekod selesai
- Kes pengecualian: kuota tidak mencukupi, syarat pendaftaran tidak dipenuhi, rekod tiada

#### Fungsi 6: Laporan dan Analitik HR

- Penerangan: Menyediakan analitik jumlah pekerja, struktur organisasi, kadar keluar masuk, kemajuan pengambilan, pengecualian kehadiran, dan metrik berkaitan.
- Cara dicetuskan: Pengguna menyoal laporan atau sistem menjalankan ringkasan berjadual.
- Logik pemprosesan:
  - Menyokong penapisan mengikut organisasi, jawatan, status pekerja, dan tempoh masa
  - Menyokong kad metrik, carta trend, dan jadual butiran
  - Menyokong eksport Excel
- Input: syarat carian, dimensi statistik, julat masa
- Output: laporan HR, carta trend, fail eksport
- Kes pengecualian: data tiada, definisi tidak konsisten, eksport gagal

## 7. Peraturan Perniagaan

- Data induk pekerja mesti mempunyai nombor pekerja unik dan dikaitkan dengan organisasi, jawatan, tahap, dan status pekerjaan.
- Onboarding tidak boleh ditanda selesai sehingga semua dokumen dan tugas wajib selesai.
- Permohonan cuti, kerja lebih masa, dan pembetulan kehadiran mesti mengikuti peraturan kelulusan organisasi.
- Medan sensitif seperti gaji, prestasi, dan kontrak mesti diberi kebenaran mengikut peranan dan skop data.
- Selepas proses berhenti selesai, kebenaran sistem perlu ditarik balik secara automatik dan rekod audit dikekalkan.
- Perubahan organisasi, jawatan, dan hubungan pelaporan mesti menyimpan sejarah.

## 8. Cadangan Halaman dan Interaksi

#### Halaman 1: Senarai Profil Pekerja

- Titik masuk: Pengurusan HR / Profil Pekerja
- Elemen halaman: penapis, senarai pekerja, label status, butang import/eksport
- Tindakan butang: tambah pekerja, lihat butiran, edit, import, eksport

#### Halaman 2: Butiran Profil Pekerja

- Titik masuk: klik daripada senarai profil pekerja
- Elemen halaman: maklumat asas, maklumat pekerjaan, maklumat kontrak, lampiran, sejarah perubahan
- Tindakan butang: edit, hantar perubahan, muat naik lampiran, lihat log

#### Halaman 3: Papan Pengambilan dan Onboarding

- Titik masuk: Pengambilan / Onboarding
- Elemen halaman: senarai calon, tugas onboarding, status nod, pemilik
- Tindakan butang: sahkan tawaran, cipta tugas onboarding, ingatkan, tanda selesai

#### Halaman 4: Meja Kerja Kehadiran dan Cuti

- Titik masuk: Perkhidmatan Pekerja / Kehadiran dan Cuti
- Elemen halaman: borang permohonan, baki cuti, rekod kelulusan, senarai pengecualian
- Tindakan butang: hantar permohonan, tarik balik, luluskan, eksport

#### Halaman 5: Halaman Laporan HR

- Titik masuk: Analitik Tenaga Kerja / Pusat Laporan
- Elemen halaman: kad metrik, penapis, carta trend, jadual butiran
- Tindakan butang: cari, eksport, tukar dimensi

### 8.1 Aliran Interaksi

1. Pengguna memulakan permohonan HR atau HR mencipta tugas berkaitan pekerja.
2. Sistem mengesahkan maklumat asas, lampiran, dan syarat peraturan.
3. Pihak bertanggungjawab melengkapkan kelulusan atau tugas pemprosesan.
4. Selepas proses selesai, data induk pekerja, status, dan rekod dikemas kini.
5. Data disegerakkan ke laporan dan sistem kebergantungan luaran.

## 9. Data dan Kebergantungan

### 9.1 Item Data Utama

- Nombor pekerja
- Nama pekerja
- Organisasi dan jabatan
- Jawatan dan tahap
- Tarikh onboarding dan tarikh berhenti
- Status pekerja
- Maklumat kontrak
- Kehadiran dan baki cuti
- Data tempoh gaji dan prestasi
- Pengendali, masa cipta, masa kemas kini

### 9.2 Kebergantungan Luaran

- Data struktur organisasi
- Sistem pengurusan identiti dan akses
- Sistem kelulusan OA
- Peranti kehadiran atau sistem kehadiran
- Sistem gaji
- Sistem e-mel atau notifikasi

## 10. Keperluan Kebenaran dan Kawalan Risiko

- Pekerja hanya boleh melihat maklumat dan rekod permohonan sendiri.
- Ketua jabatan boleh melihat ahli pasukan dan urusan kelulusan.
- HR boleh melihat dan menyelenggara data pekerja dalam skop tanggungjawab.
- Data gaji dan prestasi memerlukan kawalan kebenaran peringkat medan yang lebih ketat.
- Semua operasi penting mesti direkodkan untuk audit dan pematuhan.
- Senario risiko tinggi seperti berhenti, pertukaran jawatan, dan perubahan gaji perlu mencetuskan semakan atau peringatan kuat.

## 11. Keperluan Bukan Fungsi

- Masa respons halaman tidak boleh melebihi 3 saat.
- Menyokong sekurang-kurangnya [masukkan bilangan] pengguna serentak dalam talian.
- Penghantaran dan penyimpanan data HR sensitif mesti disulitkan.
- Menyokong sasaran ketersediaan 99.9%.
- Menyokong kelulusan dan self-service pekerja pada PC dan peranti mudah alih.

## 12. Kriteria Penerimaan

- Aliran profil pekerja, onboarding, kehadiran, kelulusan, dan laporan boleh berjalan hujung ke hujung.
- Data induk pekerja konsisten dengan maklumat organisasi dan jawatan.
- Kebenaran medan sensitif diasingkan dengan betul dan akses tanpa kebenaran disekat.
- Pengesahan peraturan kehadiran dan cuti memenuhi jangkaan perniagaan.
- Definisi laporan konsisten dengan data perniagaan.
- Semua nod aliran kerja penting mempunyai log operasi.

## 13. Risiko dan Soalan Terbuka

### 13.1 Risiko

- Data sejarah pekerja yang tidak lengkap atau tidak konsisten boleh menjejaskan migrasi dan ketepatan laporan.
- Sempadan kebenaran yang tidak jelas boleh menyebabkan risiko kebocoran data HR sensitif.
- Peraturan kehadiran, gaji, dan prestasi yang kompleks boleh menjejaskan kualiti pelancaran jika tidak dijelaskan awal.

### 13.2 Soalan Terbuka

- Adakah sistem OA, IAM, Payroll atau peranti kehadiran sedia ada perlu diintegrasikan?
- Patutkah data gaji dan prestasi hanya memaparkan keputusan, atau menyokong aliran pengiraan?
- Medan self-service pekerja manakah yang boleh diedit oleh pekerja?
- Adakah migrasi sekali sahaja bagi profil pekerja sejarah diperlukan?

## 14. Pelan Pencapaian

| Fasa | Tarikh |
| --- | --- |
| Pengesahan keperluan | [YYYY-MM-DD] |
| Semakan prototaip | [YYYY-MM-DD] |
| Pembangunan selesai | [YYYY-MM-DD] |
| Ujian selesai | [YYYY-MM-DD] |
| Penerimaan UAT | [YYYY-MM-DD] |
| Pelancaran produksi | [YYYY-MM-DD] |
