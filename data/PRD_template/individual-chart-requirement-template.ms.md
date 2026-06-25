# Templat Keperluan Carta Individu
> Gunakan templat ini untuk mentakrifkan keperluan perniagaan, kontrak data, tingkah laku carta, skop pembangunan dan kriteria penerimaan untuk satu carta atau komponen dashboard.  
> Gantikan kandungan dalam `[]` dengan maklumat projek yang disahkan.

## 1. Maklumat Dokumen Asas

| Medan | Nilai / penerangan |
| --- | --- |
| Nama templat | Templat Keperluan Carta Individu |
| Nama dokumen | [D.CHQ.QDM Keperluan Carta Tunggal] |
| Nama carta / halaman | [Masukkan nama carta atau halaman] |
| Domain perniagaan | [CHQ / QDM / KMS / lain-lain] |
| Pemohon | [Nama / pasukan] |
| Pemilik perniagaan | [Nama / pasukan yang meluluskan] |
| Pemilik produk / BA | [Nama] |
| Pemilik teknikal | [Nama] |
| Penulis | [Nama] |
| Versi | v0.1 Draf |
| Status | Draf / Dalam Semakan / Diluluskan / Dalam Pembangunan / Dikeluarkan |
| Keutamaan | Tinggi / Sederhana / Rendah |
| Sasaran keluaran / tarikh akhir | [YYYY-MM-DD] |
| Sistem / modul berkaitan | [Aplikasi, modul atau laluan menu] |

## 2. Latar Belakang dan Objektif

### 2.1 Latar Belakang

[Terangkan konteks perniagaan, masalah semasa, senario keputusan dan sebab carta ini diperlukan. Sertakan kumpulan pengguna dan proses operasi yang disokong.]

### 2.2 Objektif

- Berikan ringkasan visual yang jelas untuk [metrik utama] mengikut [dimensi / tempoh].
- Membantu pengguna mengenal pasti trend, pengecualian dan jurang perbandingan dengan cepat.
- Menyokong drill-down atau semakan butiran rekod di sebalik carta jika berkaitan.
- Menyeragamkan logik carta, sumber data dan tingkah laku UI untuk pembangunan dan UAT.

### 2.3 Kriteria Kejayaan

- Pengguna memahami maksud carta tanpa penyelarasan data manual.
- Nilai dipaparkan sepadan dengan sumber data dan peraturan pengiraan yang dipersetujui.
- Penapis, susunan, eksport dan butiran berfungsi konsisten pada lebar skrin yang disokong.

## 3. Skop

| Kawasan | Penerangan |
| --- | --- |
| Dalam skop | [Visualisasi carta, penapis, jadual butiran, eksport, kebenaran dan validasi UAT.] |
| Di luar skop | [Fungsi dikecualikan seperti tangkapan data upstream baharu, backfill sejarah atau kelulusan workflow kompleks.] |
| Andaian | [Ketersediaan jadual sumber, masa segar semula, peranan pengguna, sokongan pelayar.] |
| Kebergantungan | [API, kerja ETL, pemilik data, aset UI, komponen platform.] |
| Kekangan | [Prestasi, keselamatan, pematuhan, susun atur atau had teknikal.] |

## 4. Pihak Bertanggungjawab dan Berkepentingan

| Peranan | Nama / pasukan | Tanggungjawab |
| --- | --- | --- |
| Pemilik perniagaan | [TBD] | Definisi perniagaan, keutamaan dan kelulusan akhir. |
| Pemilik data | [TBD] | Sumber data, medan, kekerapan segar semula dan peraturan kualiti. |
| Pemilik produk / BA | [TBD] | Skop, kriteria penerimaan dan kawalan perubahan. |
| UI / UX | [TBD] | Susun atur, responsif, kebolehbacaan carta dan interaksi. |
| Pembangun front-end | [TBD] | Susun atur, rendering carta, interaksi dan tingkah laku pelayar. |
| Jurutera back-end / data | [TBD] | API, logik agregasi, keselamatan data dan prestasi. |
| Pemilik QA / UAT | [TBD] | Kes ujian, validasi hasil dan rekod kecacatan. |

## 5. Penerangan Data

### 5.1 Sumber Data

| Sumber / jadual / API | Pemilik | Kekerapan segar semula | Butiran data | Nota |
| --- | --- | --- | --- | --- |
| XXX_Table | [Pemilik data] | Masa nyata / Harian / Mingguan / Bulanan | [Satu baris bagi ...] | [Ketersediaan, SLA, had diketahui] |
| [Sumber tambahan] | [Pemilik] | [Kekerapan] | [Butiran] | [Kunci gabungan / kebergantungan] |

### 5.2 Medan Utama dan Definisi Perniagaan

| Nama medan | Definisi perniagaan | Jenis data | Wajib | Pemetaan sumber / logik |
| --- | --- | --- | --- | --- |
| XXX_Field_1 | [Definisi makna perniagaan] | String / Nombor / Tarikh | Y / N | [Lajur sumber atau formula] |
| XXX_Field_2 | [Definisi makna perniagaan] | String / Nombor / Tarikh | Y / N | [Lajur sumber atau formula] |
| Medan dimensi | [Medan kumpulan untuk paksi, legenda atau penapis] | String / Tarikh | Y / N | [Pemetaan / hierarki] |
| Medan metrik | [Nilai ukuran dalam carta] | Nombor | Y | [Agregasi, pembundaran, null handling] |
| Medan status | [Digunakan untuk warna, pecahan status atau tanda pengecualian] | String | N | [Nilai sah dan pemetaan] |

### 5.3 Peraturan Pengiraan dan Logik

- Formula metrik: [Takrifkan numerator, denominator, agregasi, pembundaran dan unit].
- Logik penapisan: [Takrifkan rekod yang disertakan/dikecualikan sebelum agregasi].
- Logik tarikh: [Takrifkan medan tarikh, zon waktu, kalendar fiskal dan sempadan tempoh].
- Pengendalian null/kosong: [Dikecualikan, dikumpul sebagai Unknown atau dianggap 0].
- Peraturan deduplikasi: [Takrifkan kunci unik dan pengendalian pendua jika berkaitan].

## 6. Persembahan Halaman dan Carta

### 6.1 Susun Atur Halaman

| Kawasan | Kandungan / tingkah laku |
| --- | --- |
| Atas: kawasan syarat carian | Penapis, carian, butang reset/apply dan peraturan lalai. |
| Tengah: kawasan carta | Satu carta dengan tajuk, legenda, label paksi, tooltip, keadaan kosong/memuat/ralat. |
| Bawah: data butiran | Jadual butiran di sebalik carta, termasuk pagination dan eksport jika perlu. |

### 6.2 Spesifikasi Carta

| Medan | Nilai / penerangan |
| --- | --- |
| Jenis carta | Garis / Bar / Pai / Donut / Gabungan / KPI / Lain-lain |
| Metrik utama | [Nama metrik dan unit] |
| Paksi X / kategori | [Dimensi, tempoh atau kategori] |
| Paksi Y / nilai | [Metrik dan unit] |
| Legenda / siri | [Medan kumpulan siri jika ada] |
| Susunan | Menaik / Menurun / Susunan perniagaan khusus |
| Julat masa lalai | [Bulan semasa / 12 bulan terakhir / lain-lain] |
| Kandungan tooltip | [Nilai, peratus, dimensi, tempoh, nota sumber] |
| Drill-down | Tiada / Buka jadual butiran / Navigasi / Modal |
| Keadaan kosong | [Mesej apabila tiada data] |
| Keadaan memuat / ralat | [Spinner, mesej cuba semula, teks fallback] |

### 6.3 Penapis dan Syarat Carian

| Medan penapis | Jenis kawalan | Nilai lalai | Wajib | Kebergantungan / nota |
| --- | --- | --- | --- | --- |
| Julat tarikh | Pemilih tarikh | Tempoh semasa | Y / N | Zon waktu, julat maksimum, peraturan fiskal |
| Organisasi / wilayah | Pilihan tunggal / berbilang | Skop pengguna / Semua | Y / N | Pilihan berdasarkan kebenaran |
| Status | Dropdown / kumpulan checkbox | Semua | N | Senarai status sah |
| Kata kunci | Kotak carian | Kosong | N | Medan boleh dicari dan peraturan padanan |

## 7. Interaksi, Kebenaran dan Eksport

| Keperluan | Tingkah laku dijangka |
| --- | --- |
| Susun atur responsif | Tiada label terpotong atau kawalan bertindih pada breakpoint dipersetujui. |
| Hover / klik | Tooltip muncul pada hover; klik mengikut peraturan drill-down. |
| Eksport | Tiada / imej carta / CSV atau Excel butiran; eksport ikut penapis aktif. |
| Kebenaran | Pengguna hanya melihat data dalam skop organisasi, peranan atau data yang dibenarkan. |
| Audit / log | [Tentukan sama ada akses, eksport atau drill-down perlu direkodkan.] |
| Kebolehcapaian | Warna bukan satu-satunya penunjuk status; label, kontras dan akses papan kekunci dipertimbangkan. |

## 8. Keperluan Pembangunan

- Bangunkan dengan HTML, Bootstrap, JavaScript dan jQuery melainkan platform sasaran memerlukan stack lain yang diluluskan.
- Gunakan kod bersih, berstruktur dan mudah disenggara dengan komen untuk logik tidak jelas.
- Pastikan pelaksanaan responsif, ringan dan sesuai untuk pembangunan susulan.
- Sahkan kontrak API, parameter permintaan, skema respons, kod ralat dan pagination sebelum pembangunan.

### 8.1 Prestasi dan Keselamatan

| Kategori | Keperluan |
| --- | --- |
| Prestasi | [Takrifkan masa muat, baris maksimum, agregasi, cache dan timeout.] |
| Keselamatan | [Takrifkan pengesahan, kebenaran, masking, sekatan eksport dan medan sensitif.] |
| Keserasian | [Takrifkan pelayar, lebar skrin dan kekangan platform.] |
| Pengendalian ralat | [Takrifkan mesej ralat pengguna dan fallback untuk API/data gagal.] |

## 9. Sistem Warna

| Token | Nilai diluluskan |
| --- | --- |
| Background | #f6f8fb / #f3f5f7 |
| Panel | #ffffff |
| Hover Surface | #eef2f4 |
| Soft Blue Panel | #f0f6ff |
| Primary Text | #111315 |
| KMS Text | #17202a |
| Secondary Text | #424a55 / #647280 |
| Border | #d9e1e7 / rgba(17,19,21,0.17) |
| Primary Blue | #2563eb |
| Danger / Error / Warning | #c2413b / #b43636 / #a56313 |

## 10. Kriteria Penerimaan dan Senarai Semak UAT

| ID | Kriteria penerimaan | Pemilik | Status |
| --- | --- | --- | --- |
| AC-01 | Nilai carta sepadan dengan data sumber dan peraturan pengiraan. | QA / Pemilik data | Pending |
| AC-02 | Semua penapis berfungsi dan reset kepada nilai lalai didokumenkan. | QA | Pending |
| AC-03 | Tooltip, legenda, label paksi dan keadaan kosong/memuat/ralat dipaparkan betul. | QA / UI | Pending |
| AC-04 | Jadual butiran sepadan dengan segmen carta dan penapis aktif. | QA / Pemilik data | Pending |
| AC-05 | Eksport mengikut penapis aktif dan skop kebenaran. | QA / Keselamatan | Pending |
| AC-06 | Halaman responsif tanpa clipping, pertindihan atau label tidak boleh dibaca. | QA / UI | Pending |

## 11. Soalan Terbuka dan Log Perubahan

| No. | Soalan | Pemilik | Tarikh akhir | Resolusi |
| --- | --- | --- | --- | --- |
| 1 | Sahkan jadual sumber dan pemetaan medan akhir. | TBD | YYYY-MM-DD | Open |
| 2 | Sahkan jenis carta dan tingkah laku drill-down. | TBD | YYYY-MM-DD | Open |
| 3 | Sahkan skop kebenaran dan polisi eksport. | TBD | YYYY-MM-DD | Open |
