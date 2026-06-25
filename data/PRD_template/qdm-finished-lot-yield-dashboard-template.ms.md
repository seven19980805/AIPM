# Templat Keperluan Dashboard Yield Finished Lot QDM

> Templat ini diadaptasi daripada `D.CHQ.QDM Yield Dashboard Requirement .docx`.  
> Imej asal telah digantikan dengan penerangan teks supaya templat boleh digunakan untuk discovery keperluan berstruktur dan penjanaan Markdown.

## 1. Maklumat Asas Dokumen

| Medan | Nilai |
| --- | --- |
| Nama templat | Templat Keperluan Dashboard Yield Finished Lot QDM |
| Nama dokumen | D.CHQ.QDM Finish Yield Dashboard Requirement |
| Sistem / Modul | FinishedLot |
| Jabatan pemula | QDM |
| Penulis / pemohon | Ely Yi |
| Versi | V1.0 |
| Tarikh ciptaan | 2026-05-21 |
| Domain bisnes | Manufacturing quality / finished lot yield / QDM dashboard |
| Status | Draft / Dalam semakan / Diluluskan / Dalam pembangunan / Released |
| Target release | [YYYY-MM-DD] |

## 2. Latar Belakang dan Objektif

### 2.1 Latar Belakang

Dashboard ini bertujuan memberi pandangan tahap tinggi terhadap metrik yield utama semasa untuk produk berbeza di kilang. Data patut dikemas kini melalui skrip automatik berjadual, secara lalai harian kecuali data owner mengesahkan cadence lain.

Dashboard mesti menyokong:

- Trend yield keseluruhan dan drill-down mengikut segment atau product.
- Trend main bins secara hierarki dan cumulative bins.
- Analisis Pareto berdasarkan loss code dan loss operation.
- Loss attribution mengikut root cause atau jabatan bertanggungjawab.

### 2.2 Objektif

- Melihat lengkung peningkatan yield yang lebih curam.
- Menurunkan kos pengeluaran dengan cepat.
- Meningkatkan output pengeluaran tanpa kos tambahan yang besar.
- Mendapatkan pulangan pelaburan lebih awal.

### 2.3 Kriteria Kejayaan

- Business owner dan data owner mengesahkan definisi metrik, penapis, jadual sumber, refresh cadence dan peraturan penerimaan.
- Pengguna boleh mengenal pasti yield finished lot terkini, output, loss dan penyumbang defect utama pada skrin pertama.
- Pengguna boleh drill dari trend yield kepada loss defect code dan perincian jabatan bertanggungjawab.
- Data dashboard sepadan dengan query sumber yang diluluskan di bawah penapis wakil.

## 3. Persembahan Halaman / Fungsi

### 3.1 Finished Lot Performance Overview Trend

| Item | Keperluan |
| --- | --- |
| Nama halaman | Finished Lot Performance Overview Trend |
| Tujuan halaman | Papar finished yield mengikut julat masa dan papar output, yield dan NSQM loss untuk minggu terkini. |
| Kawasan atas | Gunakan kriteria carian bersatu dalam Seksyen 4. |
| Kawasan data paksi Y | Carta utama secara lalai memaparkan finished product yield rate bagi setiap minggu. Bahagian kanan secara lalai memaparkan data perincian minggu terkini. Pengguna boleh klik data point/bar sebelah kiri untuk menukar paparan perincian. |
| Kawasan paksi X | Carta utama memaparkan maklumat week secara lalai; carta perincian memaparkan penerangan data terpilih. |

Penerangan teks menggantikan screenshot asal:

- Header halaman ialah `QUALITY OPERATION CENTER - Weekly Finished Lot Performance Overview`.
- Kawalan kanan atas mengandungi pemilih minggu, contohnya `W 202621`, dan tindakan export/download.
- Kawasan utama mengandungi carta besar bertajuk `Weekly Finished Lot Performance Overview Trend`.
- Carta membandingkan prestasi finished lot mingguan merentas tempoh seperti `202612` hingga `202621`.
- Carta menggabungkan bar dan line: nilai mingguan dipaparkan sebagai bar, manakala line menunjukkan konteks target/output/yield.
- Minggu terpilih perlu diserlahkan secara visual, dan hint carta menerangkan bahawa klik pada weekly yield bar akan mengemas kini defect analysis di bawah.
- Kad KPI di kanan menunjukkan perincian minggu terpilih, termasuk Yield / Target, Finished Count, NSQM atau NSOM Output, dan NSQM atau NSOM Loss.
- Nilai contoh dalam visual sumber termasuk Yield / Target `96.83%`, target `94.81%`, Finished Count `159 Lots`, output `1,335.57`, dan loss `63.55`.
- Sahkan sama ada label akhir ialah `NSQM` atau `NSOM`, kerana sumber kelihatan tidak konsisten.

### 3.2 Loss Ratio By Defect Code

| Item | Keperluan |
| --- | --- |
| Nama halaman | Loss Ratio By Defect Code |
| Tujuan halaman | Papar top 10 hingga 20 defect loss ratio mengikut defect code dan trend defect code. |
| Kawasan atas | Gunakan kriteria carian bersatu dalam Seksyen 4. |
| Kawasan data paksi Y | Carta utama memaparkan top 10 hingga 20 defect loss ratio. Bahagian kanan memaparkan trend defect code terpilih dan perincian jabatan punca. |
| Kawasan paksi X | Carta utama memaparkan maklumat defect code. Carta pie/donut perincian memaparkan maklumat department. |

Penerangan teks menggantikan screenshot asal:

- Header kekal `QUALITY OPERATION CENTER - Weekly Finished Lot Performance Overview`.
- Pemilih tempoh mendatar menunjukkan minggu seperti `202612` hingga `202621`.
- Seksyen defect analysis bertajuk `Loss Ratio By Defect Code`.
- Toggle membolehkan pengguna menunjukkan atau menyembunyikan `Loss Ratio` dan `Core Loss Ratio`.
- Carta utama ialah carta bar mendatar berperingkat untuk tempoh terpilih, contohnya `202621 Top 10 Loss Ratio By Defect Code`.
- Bar merah mewakili total loss ratio dan bar biru mewakili core loss ratio.
- Contoh defect code yang kelihatan termasuk `ED25 - Short in inner layer`, `ED21 - High resistance short`, `AP09 - Component tilting`, `BM31 - Base material dent`, `GE01 - Scratches`, `SM94 - Solder mask thickness`, `SM41 - Soldermask discoloration`, `ED55 - Short bridge die region`, dan `HO31 - Via not completely filled`.
- Defect code terpilih memacu kad perincian di kanan.
- Carta trend kanan, contohnya `ED25 Weekly Overview Trend`, membandingkan core defect loss dan defect loss ratio mengikut masa.
- Carta donut kanan menunjukkan attribution jabatan. Contoh segmen: `Etching + AOI 59%`, `Assembly 23%`, `Final Check 11%`, `Material 7%`, dengan nilai tengah `26.26%`.

## 4. Syarat Query dan Interaksi Pengguna

### 4.1 Penapis

Penerangan teks menggantikan screenshot penapis:

- Kawasan penapis menggunakan layout dua baris dan tiga lajur.
- Baris 1 mengandungi `Customer`, `Plant`, dan `Date Type`.
- Baris 2 mengandungi `Lot Type`, `Unit Type`, dan `Project Type`.
- Semua kawalan ialah dropdown dengan indikator anak panah jelas.
- Nilai lalai dalam visual sumber ialah `Customer = All selected`, `Plant = All selected`, `Date Type = Weekly`, `Lot Type = HVM`, `Unit Type = NSQM`, dan `Project Type = Overall`.

| Penapis | Jenis kawalan | Nilai lalai | Digunakan pada |
| --- | --- | --- | --- |
| Customer | Dropdown | All selected | Semua carta berkaitan |
| Plant | Dropdown | All selected | Semua carta berkaitan |
| Date Type | Dropdown | Weekly | Semua carta berkaitan |
| Lot Type | Dropdown | HVM | Semua carta berkaitan |
| Unit Type | Dropdown | NSQM | Semua carta berkaitan |
| Project Type | Dropdown | Overall | Semua carta berkaitan |

### 4.2 Peraturan Interaksi

- Perubahan penapis hendaklah mengemas kini semua carta terjejas tanpa reload seluruh halaman jika boleh secara teknikal.
- Segmen carta terpilih perlu menunjukkan active state secara visual dan menjadikan filter aktif jelas kepada pengguna.
- Tooltip perlu mudah dibaca pada desktop dan digantikan dengan tingkah laku perincian mesra sentuhan pada peranti touch jika perlu.
- Legend carta mesti boleh dicapai melalui papan kekunci jika ia interaktif.
- Tindakan eksport mesti mengikuti peraturan kebenaran data dan memasukkan konteks penapis yang digunakan jika praktikal.

## 5. Penerangan Data dan Kontrak Data

### 5.1 Sumber Data

| Source ID | Jadual / View / API | Penerangan bisnes | Grain data | Refresh cadence | Owner |
| --- | --- | --- | --- | --- | --- |
| DS-01 | `[QDMProductionDB].[IDA].[Yield_Dashboard_FinishedLotSummaryData_Internal]` | Sumber data utama untuk yield finished lot yang dikira. | Weekly / Quarterly / Monthly | Weekly atau cadence disahkan | QDM |
| DS-02 | `[QDMProductionDB].[IDA].[Yield_Dashboard_FinishedLotSummaryDefectData_Internal]` | Dataset sokongan untuk perbandingan defect code dan carta perincian. | Weekly / Quarterly / Monthly | Weekly atau cadence disahkan | QDM |

### 5.2 Medan Data Diperlukan

| Nama medan | Sumber | Jenis | Wajib | Definisi / logik bisnes |
| --- | --- | --- | --- | --- |
| `ATSDate` | DS-01 | Date / period | Ya | Diperlukan untuk trend, perbandingan period dan penapis tarikh. |
| `DateType` | DS-01 | Date / period | Ya | Menentukan sama ada dashboard menggunakan grain weekly, monthly atau quarterly. |
| `LotType` | DS-01 | String / code | Ya | Digunakan apabila pengguna menapis atau membandingkan mengikut lot type. |
| `Project Type` | DS-01 | String / code | Ya | Digunakan apabila pengguna menapis atau membandingkan mengikut project type. |
| `Yield` | DS-01 | Number / percent | Ya | Metrik finished yield utama. |
| `Output_NSQM` | DS-01 | Number | Ya | Metrik output utama. |
| `DefectCode` | DS-02 | String / code | Ya | Diperlukan untuk ranking defect code dan drill-down. |
| `DefectQty` | DS-02 | Number | Ya | Kuantiti defect atau nilai loss utama. |
| `Department` | DS-02 | String / code | Ya | Diperlukan untuk attribution loss mengikut jabatan. |

### 5.3 Peraturan Data Untuk Disahkan

- Sahkan sama ada refresh dashboard ialah weekly, daily atau kedua-duanya. Dokumen sumber menyebut daily automation tetapi jadual sumber menyatakan weekly cadence.
- Sahkan grain period dan nilai `DateType` yang dibenarkan.
- Sahkan sama ada `Customer`, `Plant`, `LotType`, `UnitType`, dan `ProjectType` disimpan terus dalam DS-01/DS-02 atau perlu join dengan jadual rujukan.
- Sahkan sama ada metrik output dan loss menggunakan NSQM, lots, units atau mod unit berganda.
- Takrifkan pengendalian null, denominator sifar, precision rounding dan format peratus.
- Takrifkan skop kebenaran untuk customer, plant, product dan data perincian yang boleh dieksport.

## 6. Logik Pengiraan Yield

### 6.1 Definisi Finished Yield

Finished Yield, juga dipanggil Product Yield, ialah peratusan unit yang berjaya melalui keseluruhan proses pembuatan dan dihantar sebagai finished goods untuk lot atau minggu tertentu. Ia menggambarkan prestasi yield menyeluruh bagi production line.

Logik utama: pengiraan berdasarkan pendaraban nisbah Output/Input merentas semua proses utama, iaitu hasil darab yield setiap proses.

### 6.2 Teks Formula Menggantikan Imej Formula

| Formula | Versi teks |
| --- | --- |
| Lot Product Yield | `Lot Product Yield = (PAOI Output / PAOI Input) x (E-test Output / E-test Input) x (CCAOI Output / CCAOI Input) x (Bump AOI Output / Bump AOI Input) x (FVI Output / FVI Input)` |
| Weekly Product Yield | `Weekly Product Yield = hasil darab setiap nisbah weekly shipped output/input proses`, contohnya `(Total Weekly Shipped PAOI Output / Total Weekly Shipped PAOI Input) x (Total Weekly Shipped E-test Output / Total Weekly Shipped E-test Input) x ...` |
| Peraturan lanjutan | Jika process path yang diluluskan termasuk `Inline`, `Others` atau langkah pemeriksaan tambahan, tambah nisbah yield proses tersebut dalam pendaraban. |

### 6.3 Langkah dan Contoh Pengiraan

Prinsip pengiraan: `Output / Input = Process Yield`, kemudian darabkan semua process yield secara berturutan.

| Process | Input | Output | Losses | Yield |
| --- | ---: | ---: | ---: | ---: |
| PAOI | 50000 | 49700 | 300 | 99.4% |
| E-test | 49700 | 49500 | 200 | 99.5% |
| CCAOI | 49250 | 48900 | 350 | 99.29% |
| Bump | 48600 | 48300 | 300 | 99.38% |
| FVI | 48300 | 47900 | 400 | 99.17% |
| Inline | 49500 | 49250 | 250 | 99.49% |
| Others | 48900 | 48600 | 300 | 99.39% |

Ungkapan GTY contoh daripada sumber:

`GTY = 99.4% x 99.5% x 99.29% x 99.38% x 99.17% x 99.49% x 99.39%`

## 7. Layout Halaman / Fungsi

Halaman perlu menggunakan pola layout berdasarkan keutamaan bisnes, kepadatan data dan saiz skrin. Lalai yang disyorkan ialah Primary-Detail / Hero Layout untuk halaman analitik, dengan Uniform Grid sebagai fallback untuk dashboard pemantauan.

| Pilihan layout | Penerangan | Kes penggunaan terbaik | Cadangan |
| --- | --- | --- | --- |
| Primary-Detail / Hero | Satu carta hero besar mengisi kawasan utama, dengan kad KPI dan carta sokongan di sisi atau bawah. | Halaman analisis dengan satu trend dominan atau soalan bisnes utama. | Disyorkan sebagai lalai melainkan business owner mengesahkan sebaliknya. |
| Nested / Drill-down | Memilih satu carta mengemas kini atau menapis carta lain. | Analisis eksploratori dan drill-down kategori. | Gunakan hanya apabila hubungan carta jelas. |
| Uniform Grid | Carta menggunakan saiz kad konsisten dan keutamaan visual hampir sama. | Dashboard pemantauan dengan banyak metrik setara. | Fallback apabila tiada carta dominan. |

## 8. Inventori dan Konfigurasi Carta

Setiap carta perlu dispesifikasikan sebelum pembangunan bermula.

| Chart ID | Nama carta | Jenis | Metrik utama | Dimensi / grouping | Sumber data | Interaksi |
| --- | --- | --- | --- | --- | --- | --- |
| CH-01 | Finished Overall Trend | Gabungan line + bar | Yield / target / output | Weekly / Quarterly / Monthly | DS-01 | Hover tooltip; klik bar atau point mingguan untuk menapis jadual perincian dan defect analysis. |
| CH-02 | Defect Loss Ratio | Bar mendatar stacked atau grouped | Defect loss ratio / core loss ratio | Top 10 hingga Top 20 defect codes | DS-02 | Legend toggle; klik defect code untuk mengemas kini trend berkaitan dan department attribution. |
| CH-03 | Carta perincian kanan | Table / line / pie atau donut | Kandungan perincian berdasarkan pilihan kiri | Period semasa, defect terpilih, penapis terpilih | DS-01 + DS-02 | Pagination, sort, tooltip, selected-state linkage, export. |

## 9. Pihak Bertanggungjawab dan Stakeholder

| Peranan | Nama / team | Tanggungjawab | Sign-off diperlukan |
| --- | --- | --- | --- |
| Business Owner | Yield team | Mengesahkan tujuan bisnes, keutamaan dan penerimaan maksud carta. | Ya |
| Product Owner / BA | QDM | Menyelenggara keperluan, menyelesaikan soalan skop, menyelaras review. | Ya |
| Data Owner | Yield team | Mengesahkan jadual sumber, definisi medan, refresh cadence dan peraturan kualiti data. | Ya |
| UI/UX Reviewer | Yield team | Menyemak konsistensi visual AITC, tingkah laku layout dan pengalaman responsif. | Disyorkan |
| Frontend Developer | QDM | Melaksanakan dashboard, komponen carta, interaksi dan responsiveness. | Tidak |
| QA Tester | Yield team | Melaksanakan ujian fungsi, data, compatibility, accessibility dan regression. | Ya |

## 10. Keperluan UI dan Reka Bentuk Visual

Implementasi perlu mengikuti gaya AITC enterprise UI: bersih, operasional, boleh dipercayai, padat tetapi mudah dibaca, dan menggunakan permukaan neutral dengan biru sebagai warna tindakan utama.

| Kawasan UI | Keperluan |
| --- | --- |
| Sistem warna | Gunakan background `#f6f8fb` / `#f3f5f7`, panel `#ffffff`, primary blue `#2563eb`, hover `#1d4ed8`, border `#d9e1e7`, dan text `#111315` / `#17202a`. Jangan jadikan hijau atau ungu sebagai warna brand utama. |
| Tipografi | Gunakan Arial Nova jika tersedia, kemudian Plus Jakarta Sans, Arial dan font fallback Cina. Elakkan weight terlalu berat dan letter spacing negatif. |
| Spacing dan radius | Gunakan ritma spacing 8px, radius umum 8px dan radius compact 6px untuk kawalan padat. |
| Kad / panel | Gunakan panel carta putih dengan tajuk jelas, padding konsisten dan soft elevation hanya apabila perlu. |
| Layout responsif | Desktop mengutamakan perbandingan; tablet mengekalkan kebolehbacaan carta; mobile menyusun carta secara menegak dengan scroll mendatar hanya untuk jadual sebenar. |
| State | Takrifkan loading, empty, error, disabled, active, hover, focus dan selected state untuk penapis dan carta. |

## 11. Spesifikasi Teknikal

| Kategori | Keperluan |
| --- | --- |
| Frontend stack | HTML + Bootstrap + JavaScript/jQuery. Kod perlu bersih, berstruktur, dikomen jika membantu dan mudah untuk pembangunan susulan. |
| Chart library | Gunakan charting library ringan yang diluluskan atau standard projek sedia ada. Elakkan plugin kompleks melainkan diluluskan oleh architecture review. |
| Responsiveness | Sokong breakpoint desktop, tablet dan mobile. Gunakan responsive grid native dan elakkan fixed width yang menyebabkan overflow. |
| Performance | Shell halaman perlu render dengan cepat; carta perlu load secara asynchronous jika boleh. Sasaran refresh carta dalam 3 saat untuk volum data normal, tertakluk kepada prestasi API. |
| Browser support | Sokong versi Chrome dan Edge semasa yang diluluskan enterprise. Keperluan browser tambahan perlu disahkan. |
| Maintainability | Pisahkan data mapping, chart configuration dan rendering logic supaya carta baharu boleh ditambah melalui konfigurasi jika praktikal. |
| Security | Patuhi role-based data access. Cegah eksport data terhad tanpa kebenaran dan elakkan mendedahkan medan mentah sensitif dalam client code. |

## 12. Keperluan Bukan Fungsian

| Jenis keperluan | Sasaran / peraturan | Kaedah validasi |
| --- | --- | --- |
| Ketepatan data | Nilai dipaparkan mesti sepadan dengan query sumber diluluskan untuk penapis sama. | QA membandingkan sample output dengan query sumber atau report tervalidasi. |
| Performance | Refresh penapis atau carta normal perlu memenuhi SLA, sasaran 3 saat di bawah volum data standard. | Browser timing dan semakan log API. |
| Accessibility | Kawalan boleh dicapai papan kekunci, fokus jelas, kontras mencukupi dan komunikasi status bukan warna sahaja. | Ujian papan kekunci manual dan semakan kontras. |
| Reliability | Kegagalan satu carta tidak boleh merosakkan seluruh halaman; tunjukkan chart-level error state. | Ujian simulasi kegagalan API. |
| Compatibility | Layout kekal boleh dibaca merentas lebar desktop, tablet dan mobile yang diluluskan. | Pengesahan browser responsif. |
| Auditability | Masa refresh terakhir dan konteks penapis digunakan perlu kelihatan atau tersedia dalam metadata eksport jika praktikal. | Ujian fungsi dan pemeriksaan eksport. |

## 13. Kriteria Penerimaan

1. Business owner mengesahkan senarai carta, definisi metrik, senarai penapis, paparan lalai dan pola layout.
2. Data owner mengesahkan jadual/view/API sumber, pemetaan medan, refresh cadence, join logic dan peraturan pengiraan.
3. Semua carta render dengan betul untuk penapis lalai dan sekurang-kurangnya tiga kombinasi penapis wakil.
4. Loading, empty, error, active, hover, focus dan disabled state dilaksanakan dan konsisten secara visual.
5. Halaman responsif pada desktop, tablet dan mobile tanpa teks terpotong, kawalan bertindih atau label carta tidak boleh dibaca.
6. Tingkah laku eksport mengikuti peraturan kebenaran data yang diluluskan dan memasukkan konteks penapis apabila sesuai.
7. QA mengesahkan ketepatan data terhadap query sumber atau report rujukan yang diluluskan.
8. Halaman akhir mengikuti sistem warna yang diluluskan dan tidak memperkenalkan warna utama atau dekorasi berat yang tidak diluluskan.

## 14. Soalan Terbuka dan Keputusan Diperlukan

| ID | Soalan / keputusan | Owner | Tarikh sasaran | Status |
| --- | --- | --- | --- | --- |
| Q-01 | Pilihan layout lalai manakah diluluskan: Primary-Detail / Hero, Uniform Grid, Tabbed atau pola lain? | Business Owner / Product Owner | Perlu disahkan | Open |
| Q-02 | Apakah jadual/view/API sumber akhir dan join key? | Data Owner | Perlu disahkan | Open |
| Q-03 | Carta manakah wajib untuk release pertama dan manakah optional? | Business Owner | Perlu disahkan | Open |
| Q-04 | Peranan manakah boleh mengeksport imej carta atau underlying data? | Security / Business Owner | Perlu disahkan | Open |
| Q-05 | Apakah refresh cadence dan SLA ketersediaan data yang diluluskan? | Data Owner | Perlu disahkan | Open |
| Q-06 | Label akhir untuk kad KPI Output / Loss patut menggunakan NSQM atau NSOM? | Business Owner / Data Owner | Perlu disahkan | Open |
| Q-07 | Formula Product Yield perlu memasukkan Inline dan Others selain PAOI, E-test, CCAOI, Bump AOI dan FVI? | Data Owner | Perlu disahkan | Open |

## 15. Appendix A. Sistem Warna

| Token | Nilai / peraturan |
| --- | --- |
| Background | `#f6f8fb` / `#f3f5f7` |
| Panel | `#ffffff` |
| Hover Surface | `#eef2f4` |
| Soft Blue Panel | `#f0f6ff` |
| Primary Text | `#111315` |
| KMS Text | `#17202a` |
| Secondary Text | `#424a55` / `#647280` |
| Border | `#d9e1e7` / `rgba(17,19,21,0.17)` |
| Active Border | `rgba(17,19,21,0.28)` |
| Primary Blue | `#2563eb` |
| Primary Hover | `#1d4ed8` |
| Primary Soft Background | `#e8f1ff` |
| Accent Blue | `#60a5fa` |
| Accent Soft Background | `rgba(96,165,250,0.17)` |
| Danger / Error / Warning | `#c2413b` / `#b43636` / `#a56313` |
| Shadow | `0 14px 34px rgba(38, 55, 70, 0.1)`, soft elevation sahaja |
