# Templat Keperluan Pelbagai Carta
> Gunakan templat ini untuk mentakrifkan halaman dashboard pelbagai carta responsif dengan satu atau lebih sumber data QDM yang diselaraskan.  
> Gantikan kandungan dalam `[]` dengan maklumat projek yang disahkan.

## 1. Maklumat Dokumen Asas

| Medan | Nilai |
| --- | --- |
| Nama templat | Templat Keperluan Pelbagai Carta |
| Nama dokumen | D.CHQ.QDM Keperluan Pelbagai Carta |
| Sistem / modul | D.CHQ.QDM / Dashboard dan persembahan carta |
| Pemilik perniagaan | [Untuk disahkan] |
| Pemilik produk | [Untuk disahkan] |
| Penulis | [Untuk disahkan] |
| Versi | V1.0 draf dipertingkat |
| Status | Draf untuk semakan |
| Tarikh penciptaan | [YYYY-MM-DD] |
| Kemas kini terakhir | [YYYY-MM-DD] |
| Sasaran keluaran / sprint | [Untuk disahkan] |
| Pelulus | [Untuk disahkan] |

### 1.1 Sejarah Versi

| Versi | Tarikh | Pemilik | Penerangan perubahan |
| --- | --- | --- | --- |
| V0.1 | [Tarikh] | Penulis asal | Rangka awal dengan seksyen asas halaman pelbagai carta. |
| V1.0 | [Tarikh] | [Penulis] | Struktur dipertingkat, medan cadangan, kriteria penerimaan dan panduan pelaksanaan. |

## 2. Latar Belakang dan Objektif

### 2.1 Latar Belakang

[Terangkan keperluan halaman pelbagai carta, sumber data terlibat, soalan perniagaan dan sebab satu paparan dashboard terselaras diperlukan.]

Penerangan: Halaman ini menyediakan satu paparan terselaras untuk beberapa carta daripada satu atau lebih sumber data QDM. Pengguna mesti boleh menapis, membandingkan, drill-down dan mengeksport insight carta, sementara pelaksanaan kekal ringan, responsif dan konsisten dengan gaya UI enterprise AITC.

### 2.2 Objektif

- Sediakan satu halaman dashboard responsif yang memaparkan beberapa carta berkaitan dengan penapis dan gaya visual konsisten.
- Membolehkan pengguna membandingkan metrik merentas masa, kategori, status, organisasi atau dimensi yang diluluskan.
- Menyokong drill-down dan cross-filter apabila hubungan carta ditentukan oleh pemilik perniagaan.
- Menyeragamkan medan konfigurasi carta supaya penambahan carta masa depan memerlukan kurang pembangunan semula.
- Menentukan kriteria penerimaan untuk susun atur, prestasi, kebolehcapaian, ketepatan data dan keserasian pelayar.

## 3. Skop

| Kawasan | Dalam skop | Di luar skop / nota |
| --- | --- | --- |
| Susun atur halaman | Bekas dashboard, kawasan syarat carian, kawasan pelbagai carta, kawasan butiran/penerangan paksi. | Navigasi global dan reka bentuk semula halaman tidak berkaitan dikecualikan. |
| Carta | Garis, bar, bar bertindan, pai/donut, kad KPI, heatmap dan paparan butiran berasaskan jadual. | Visualisasi tersuai maju perlu kelulusan. |
| Interaksi | Penapis, reset, refresh, drill-down, tab, tooltip, toggle legenda, eksport, keadaan kosong/ralat. | Kolaborasi masa nyata dan penciptaan carta oleh pengguna tidak termasuk. |
| Data | Jadual/view/API QDM yang diluluskan dan peraturan pemetaan medan. | Pembangunan pipeline upstream baharu di luar skop melainkan diperlukan. |
| Penghantaran | HTML + Bootstrap + JavaScript/jQuery responsif dengan struktur mudah disenggara. | Plugin kompleks atau dependensi carta berat memerlukan semakan arkitektur. |

## 4. Pihak Bertanggungjawab dan Berkepentingan

| Peranan | Nama | Tanggungjawab | Perlu sign-off |
| --- | --- | --- | --- |
| Pemilik perniagaan | [Untuk disahkan] | Mengesahkan tujuan, keutamaan, KPI dan makna carta. | Ya |
| Pemilik produk / BA | [Untuk disahkan] | Menjaga keperluan, menyelesaikan soalan skop dan menyelaras semakan. | Ya |
| Pemilik data | [Untuk disahkan] | Mengesahkan jadual, medan, kadar segar semula dan peraturan kualiti data. | Ya |
| Penyemak UI/UX | [Untuk disahkan] | Menyemak konsistensi AITC, susun atur dan pengalaman responsif. | Disyorkan |
| Pembangun frontend | [Untuk disahkan] | Melaksanakan dashboard, komponen carta dan interaksi. | Tidak |
| Penguji QA | [Untuk disahkan] | Menguji fungsi, data, keserasian, kebolehcapaian dan regresi. | Ya |
| Keselamatan / pematuhan | [Untuk disahkan] | Menyemak kawalan akses, sekatan eksport dan pendedahan data sensitif. | Jika perlu |

## 5. Penerangan Data dan Kontrak Data

### 5.1 Sumber Data

| Source ID | Jadual / view / API | Penerangan perniagaan | Butiran data | Kadar segar semula | Pemilik |
| --- | --- | --- | --- | --- | --- |
| DS-01 | XXX_Table | Dataset utama untuk kumpulan carta utama. | [Untuk disahkan] | [Untuk disahkan] | [Untuk disahkan] |
| DS-02 | XXX_Table2 | Dataset sokongan untuk perbandingan atau carta butiran. | [Untuk disahkan] | [Untuk disahkan] | [Untuk disahkan] |
| DS-03 | Sumber tambahan pilihan | Digunakan hanya jika metrik wajib tidak boleh diperoleh daripada DS-01 atau DS-02. | [Untuk disahkan] | [Untuk disahkan] | [Untuk disahkan] |

### 5.2 Medan Data Diperlukan

| Nama medan | Sumber | Jenis | Wajib | Definisi / logik perniagaan |
| --- | --- | --- | --- | --- |
| XXX_Field | XXX_Table | [Untuk disahkan] | Ya | Ukuran atau dimensi utama untuk satu atau lebih carta. |
| XXX_Field2 | XXX_Table2 | [Untuk disahkan] | Ya | Medan sokongan untuk perbandingan, segmentasi atau butiran tooltip. |
| Tarikh / tempoh | Semua sumber berkaitan | Tarikh / tempoh | Disyorkan | Diperlukan untuk trend, perbandingan tempoh atau penapis tarikh. |
| Organisasi / entiti | Semua sumber berkaitan | String / kod | Disyorkan | Diperlukan untuk penapis atau perbandingan mengikut unit, jabatan, tapak atau pelanggan. |
| Status / kategori | Semua sumber berkaitan | String / kod | Disyorkan | Untuk carta berkumpulan, bar bertindan, legenda dan kiraan status. |
| Nilai ukuran | Dikira atau medan sumber | Nombor | Disyorkan | Nilai untuk KPI, paksi, tooltip dan agregasi. |

### 5.3 Logik Medan dan Peraturan Data

- Takrifkan kunci gabungan dan hubungan antara sumber data sebelum pembangunan bermula.
- Nyatakan sama ada setiap carta menggunakan rekod mentah, rekod agregat atau metrik pra-kira.
- Dokumentasikan formula, penapis, pengecualian, null handling dan pembundaran dalam inventori carta.
- Jika dua carta menggunakan metrik sama, gunakan logik pengiraan sama melainkan pengecualian didokumenkan.
- Semua label, unit dan legenda yang kelihatan mesti sepadan dengan istilah perniagaan diluluskan.

## 6. Susun Atur Halaman / Fungsi

Susun atur dipilih berdasarkan keutamaan perniagaan, kepadatan data dan saiz skrin. Default disyorkan ialah Primary-Detail / Hero untuk halaman analitik, dengan Uniform Grid sebagai fallback untuk dashboard pemantauan.

| Pilihan susun atur | Penerangan | Kegunaan terbaik | Cadangan |
| --- | --- | --- | --- |
| Uniform Grid | Semua bekas carta saiz sama dan sejajar dalam grid konsisten. | Dashboard pemantauan dan perbandingan KPI setara. | Gunakan apabila semua carta sama penting. |
| Primary-Detail / Hero | Satu carta utama menggunakan kawasan utama, carta sokongan di sisi atau bawah. | Halaman analisis dengan trend atau soalan utama. | Default disyorkan melainkan disahkan sebaliknya. |
| Nested / Drill-down | Memilih satu carta mengemas kini atau menapis carta lain. | Analisis penerokaan dan drill-down kategori. | Gunakan hanya apabila hubungan carta jelas. |
| Tabbed | Beberapa carta berkaitan berkongsi satu bekas dan ditukar melalui tab. | Data homogen seperti Hari / Minggu / Bulan. | Menjimatkan ruang, tetapi jangan sembunyikan carta kritikal. |
| Masonry / Waterfall | Kad berkongsi lebar tetapi tinggi berubah mengikut kandungan. | Laporan media campuran atau feed mobile-first. | Tidak disyorkan untuk dashboard operasi utama. |

## 7. Persembahan Halaman / Fungsi

| Medan | Keperluan |
| --- | --- |
| Nama halaman | Dashboard Pelbagai Carta - label menu tepat perlu disahkan |
| Tujuan halaman | Memaparkan beberapa metrik QDM dalam satu paparan terselaras, boleh ditapis dan dieksport. |
| Kawasan atas | Syarat carian: julat tarikh, organisasi/entiti, kategori/status, sumber data dan penapis khusus peranan. |
| Kawasan tengah | Kawasan carta dengan susun atur dipilih, tajuk, legenda, tooltip dan keadaan memuat/kosong/ralat. |
| Kawasan bawah | Data butiran, penerangan paksi, definisi metrik, masa segar semula terakhir dan nota sumber. |
| Rajah / ilustrasi | Masukkan wireframe atau screenshot akhir selepas semakan UX. |

## 8. Inventori dan Konfigurasi Carta

### 8.1 Inventori Carta

| ID carta | Nama carta | Jenis | Metrik utama | Dimensi / kumpulan | Sumber data | Interaksi |
| --- | --- | --- | --- | --- | --- | --- |
| CH-01 | Trend keseluruhan | Garis / area | [Untuk disahkan] | Tarikh / tempoh | DS-01 | Tooltip; klik menapis jadual butiran |
| CH-02 | Komposisi | Pai / donut | [Untuk disahkan] | Status / kategori | DS-01 atau DS-02 | Toggle legenda; klik menapis carta berkaitan |
| CH-03 | Perbandingan mengikut entiti | Bar / bar bertindan | [Untuk disahkan] | Organisasi / entiti | DS-01 | Susun; tooltip; eksport data |
| CH-04 | Jadual butiran | Jadual | Rekod asas atau butiran agregat | Penapis dipilih | DS-01 + DS-02 | Pagination; susun; eksport |

### 8.2 Medan Konfigurasi Carta

| Medan konfigurasi | Wajib? | Panduan |
| --- | --- | --- |
| Tajuk carta | Ya | Gunakan istilah perniagaan ringkas, elakkan nama jadual teknikal. |
| Paksi X / Y | Ya untuk carta paksi | Takrifkan label, unit, susunan, granulariti tarikh dan min/maks. |
| Legenda | Jika perlu | Takrifkan susunan, pemetaan warna dan tingkah laku apabila siri disembunyikan. |
| Tooltip | Ya | Tunjukkan nilai, unit, tempoh/kategori dan nota pengiraan jika berguna. |
| Keadaan kosong | Ya | Papar mesej jelas apabila tiada data; jangan papar carta rosak. |
| Keadaan memuat | Ya | Papar indikator ringan atau skeleton ketika data diambil. |
| Keadaan ralat | Ya | Papar mesej mesra pengguna dan log butiran teknikal. |
| Eksport | Disyorkan | Takrifkan sama ada imej, CSV atau jadual butiran boleh dieksport mengikut peranan. |

## 9. Syarat Carian dan Interaksi Pengguna

| Penapis | Jenis kawalan | Nilai lalai | Digunakan untuk | Nota |
| --- | --- | --- | --- | --- |
| Julat tarikh / tempoh | Pemilih tarikh atau pilihan tempoh | Tempoh tersedia terkini | Semua carta melainkan dikecualikan | Diperlukan untuk trend dan perbandingan. |
| Organisasi / entiti | Dropdown / carian | Skop lalai pengguna | Carta berkaitan | Hormati skop kebenaran pengguna. |
| Kategori / status | Dropdown / multi-select | Semua | Carta kategori, status, komposisi | Gunakan label perniagaan diluluskan. |
| Sumber data | Dropdown / parameter tersembunyi | Sumber utama | Carta khusus sumber | Papar hanya jika pengguna perlu menukar sumber. |
| Reset | Butang | N/A | Seluruh halaman | Pulihkan penapis lalai diluluskan. |

### 9.1 Peraturan Interaksi

- Perubahan penapis mengemas kini semua carta terkesan tanpa muat semula penuh jika boleh.
- Segmen carta dipilih perlu menunjukkan keadaan aktif dan penapis aktif kepada pengguna.
- Tooltip perlu boleh dibaca di desktop dan diganti dengan tingkah laku tap-friendly pada peranti sentuh jika perlu.
- Legenda interaktif mesti boleh dicapai melalui papan kekunci.
- Eksport mesti mengikut peraturan kebenaran data dan menyertakan konteks penapis jika praktikal.

## 10. Keperluan UI dan Reka Bentuk Visual

| Kawasan UI | Keperluan |
| --- | --- |
| Sistem warna | Gunakan latar #f6f8fb / #f3f5f7, panel #ffffff, biru utama #2563eb, hover #1d4ed8, border #d9e1e7 dan teks #111315 / #17202a. Jangan jadikan hijau atau ungu warna utama. |
| Tipografi | Gunakan Arial Nova jika ada, kemudian Plus Jakarta Sans, Arial dan fallback sesuai. Elakkan letter spacing negatif. |
| Spacing / radius | Gunakan ritma 8px, radius 8px dan radius 6px untuk kawalan padat. |
| Kad / panel | Panel carta putih dengan tajuk jelas, padding konsisten dan elevation lembut jika perlu. |
| Responsif | Desktop mengutamakan perbandingan; tablet mengekalkan kebolehbacaan; mobile menyusun carta menegak. |
| Keadaan | Takrifkan memuat, kosong, ralat, disabled, aktif, hover, fokus dan terpilih. |

## 11. Spesifikasi Teknikal

| Kategori | Keperluan |
| --- | --- |
| Stack frontend | HTML + Bootstrap + JavaScript/jQuery; kod bersih, berstruktur, dikomen dan mudah dikembangkan. |
| Pustaka carta | Gunakan pustaka carta ringan diluluskan atau standard projek. |
| Responsif | Sokong breakpoint desktop, tablet dan mobile; elakkan lebar tetap yang menyebabkan limpahan. |
| Prestasi | Shell halaman dirender cepat; carta dimuat secara asynchronous jika boleh; sasaran refresh 3 saat untuk volum biasa. |
| Sokongan pelayar | Sokong Chrome dan Edge versi enterprise diluluskan. |
| Kebolehselenggaraan | Pisahkan pemetaan data, konfigurasi carta dan logik rendering. |
| Keselamatan | Hormati akses data berasaskan peranan dan cegah eksport tidak dibenarkan. |

## 12. Keperluan Bukan Fungsi

| Jenis | Sasaran / peraturan | Validasi |
| --- | --- | --- |
| Ketepatan data | Nilai paparan mesti sepadan dengan hasil query sumber untuk penapis sama. | QA banding dengan query sumber atau laporan rujukan. |
| Prestasi | Refresh penapis/carta selesai dalam SLA, sasaran 3 saat. | Masa pelayar dan log API. |
| Kebolehcapaian | Kawalan boleh dicapai papan kekunci, fokus jelas, kontras cukup dan bukan warna sahaja. | Ujian papan kekunci dan semakan kontras. |
| Kebolehpercayaan | Gagal satu carta tidak merosakkan seluruh halaman; papar ralat per carta. | Ujian kegagalan API simulasi. |
| Keserasian | Susun atur kekal boleh dibaca pada lebar desktop, tablet dan mobile diluluskan. | Pengesahan responsif. |
| Kebolehaudit | Masa segar semula dan konteks penapis kelihatan atau ada dalam metadata eksport jika praktikal. | Ujian fungsi dan semakan eksport. |

## 13. Kriteria Penerimaan

- Pemilik perniagaan mengesahkan senarai carta, definisi metrik, senarai penapis, paparan lalai dan susun atur.
- Pemilik data mengesahkan sumber, pemetaan medan, refresh cadence, join logic dan formula.
- Semua carta render betul untuk penapis lalai dan sekurang-kurangnya tiga kombinasi penapis wakil.
- Keadaan memuat, kosong, ralat, aktif, hover, fokus dan disabled dilaksanakan konsisten.
- Halaman responsif pada desktop, tablet dan mobile tanpa clipping, pertindihan atau label tidak boleh dibaca.
- Eksport mengikut kebenaran data dan menyertakan konteks penapis jika berkaitan.
- QA mengesahkan ketepatan data terhadap query sumber atau laporan rujukan diluluskan.

## 14. Soalan Terbuka dan Keputusan

| ID | Soalan / keputusan | Pemilik | Tarikh sasaran | Status |
| --- | --- | --- | --- | --- |
| Q-01 | Susun atur lalai mana diluluskan: Primary-Detail / Hero, Uniform Grid, Tabbed atau lain-lain? | Pemilik perniagaan / produk | [Untuk disahkan] | Open |
| Q-02 | Apakah jadual/view/API dan join key akhir? | Pemilik data | [Untuk disahkan] | Open |
| Q-03 | Carta mana wajib untuk keluaran pertama dan mana pilihan? | Pemilik perniagaan | [Untuk disahkan] | Open |
| Q-04 | Peranan mana boleh eksport imej carta atau data asas? | Keselamatan / pemilik perniagaan | [Untuk disahkan] | Open |
| Q-05 | Apakah refresh cadence dan SLA data diluluskan? | Pemilik data | [Untuk disahkan] | Open |

## 15. Medan Keperluan Tambahan Dicadangkan

| Kumpulan medan | Medan dicadangkan | Kepentingan |
| --- | --- | --- |
| Tadbir urus dokumen | Pemilik, pelulus, sejarah versi, status, sasaran keluaran, log perubahan | Menjelaskan akauntabiliti dan mencegah perubahan tidak terkawal. |
| Definisi perniagaan | Persona, matlamat, KPI, metrik kejayaan, keutamaan | Memastikan carta menjawab soalan perniagaan sebenar. |
| Kontrak data | Sumber, jenis medan, grain, refresh cadence, join key, null handling, formula | Mencegah nombor tidak sepadan dan kerja semula QA. |
| Konfigurasi carta | Jenis, metrik, dimensi, label paksi, legenda, tooltip, susunan, penapis lalai | Memastikan pelaksanaan konsisten dan mudah dikembangkan. |
| Reka bentuk interaksi | Drill-down, cross-filtering, tab, eksport, reset, active state, error state | Menentukan cara pengguna mengendalikan dashboard. |
| Kualiti dan keluaran | Kriteria penerimaan, kes ujian, pelayar, accessibility, prestasi, sign-off | Menjadikan keluaran boleh diukur dan disemak. |
