# Templat Analisis Yield ABF

> Gunakan templat ini untuk menentukan dashboard atau halaman analisis yield pembuatan substrat ABF.  
> Gantikan kandungan dalam `[]` dengan maklumat projek yang disahkan dan buang item yang tidak berkaitan.

## 1. Maklumat Dokumen Asas

| Medan | Nilai |
| --- | --- |
| Nama templat | Templat Analisis Yield ABF |
| Nama dokumen | [Keperluan Analisis Yield ABF] |
| Topik analisis / nama halaman | [Contoh: Dashboard Analisis Yield ABF] |
| Domain bisnes | Kualiti pembuatan / ABF / QDM |
| Pasukan pemohon | [Jabatan / pasukan] |
| Pemilik bisnes | [Bertanggungjawab untuk definisi yield dan penerimaan] |
| Pemilik data | [Bertanggungjawab untuk jadual sumber dan definisi medan] |
| Pemilik produk / BA | [Nama] |
| Pemilik teknikal | [Nama] |
| Versi | v0.1 draf |
| Status | Draf / Dalam semakan / Diluluskan / Dalam pembangunan / Dikeluarkan |
| Sasaran keluaran / tarikh akhir | [YYYY-MM-DD] |
| Sistem / modul berkaitan | [MES / QMS / QDM / platform data / modul dashboard] |

## 2. Latar Belakang dan Objektif

### 2.1 Latar Belakang

[Huraikan keadaan pengurusan yield ABF semasa, isu, pengguna, senario keputusan dan sebab halaman analisis ini diperlukan.]

Contoh: Pembuatan ABF melibatkan banyak langkah proses dan pemeriksaan. Bisnes perlu mengenal pasti sama ada penurunan yield datang daripada produk, lot, panel, langkah proses, peralatan atau kategori kecacatan, kemudian menggunakan hasil analisis untuk mesyuarat kualiti, respons abnormal dan penjejakan penambahbaikan.

### 2.2 Objektif Analisis

- Paparkan yield ABF mengikut masa, produk, material, lot, panel, langkah proses, peralatan dan kategori kecacatan.
- Kenal pasti langkah proses, jenis kecacatan dan lot yang menyumbang kehilangan yield terbesar.
- Sokong drill-down daripada yield keseluruhan kepada perincian lot / panel / langkah / kecacatan.
- Standardkan definisi yield, sumber data, logik penapis dan kriteria penerimaan.
- Sediakan asas data untuk amaran abnormal, tugasan tanggungjawab dan penutupan penambahbaikan.

## 3. Skop Analisis

| Kawasan | Penerangan |
| --- | --- |
| Skop produk | [Keluarga produk ABF, nombor material, pelanggan, versi atau platform proses] |
| Skop proses | [Langkah proses yang diliputi seperti exposure, development, plating, AOI, testing] |
| Skop data | [Tarikh mula sejarah, kekerapan refresh, status lot, sama ada lot engineering/pilot disertakan] |
| Skop carta | KPI, trend, kehilangan langkah proses, Pareto kecacatan, perincian lot/panel, heatmap, eksport |
| Di luar skop | [Perubahan pengumpulan data upstream, model ramalan kompleks, tugasan automatik] |
| Andaian dan kebergantungan | [Ketersediaan sumber, pemetaan medan, peraturan kebenaran, konfigurasi sasaran, SLA API] |

## 4. Pihak Bertanggungjawab dan Pemegang Taruh

| Peranan | Nama / pasukan | Tanggungjawab |
| --- | --- | --- |
| Pembuatan | [TBD] | Sahkan senario pengeluaran, pemilikan langkah proses dan aliran penggunaan harian. |
| Kualiti | [TBD] | Sahkan definisi yield, taksonomi kecacatan, penutupan abnormal dan kriteria penerimaan. |
| Proses | [TBD] | Terangkan kehilangan proses, parameter dan tindakan penambahbaikan. |
| Peralatan | [TBD] | Sahkan dimensi peralatan, abnormal peralatan dan korelasi parameter. |
| Data | [TBD] | Sahkan jadual sumber, definisi medan, kekerapan refresh dan peraturan kualiti data. |
| Produk / BA | [TBD] | Kekalkan skop, keutamaan, semakan dan kawalan perubahan. |
| Pembangunan | [TBD] | Laksanakan API data, logik agregasi, halaman dan interaksi carta. |
| QA / UAT | [TBD] | Tulis kes ujian dan sahkan data, fungsi serta kebenaran. |

## 5. Definisi Yield dan Peraturan Bisnes

| Metrik | Formula / definisi | Grain | Nota |
| --- | --- | --- | --- |
| Yield keseluruhan | [Kuantiti good / kuantiti input] | Produk / lot / tempoh | Nyatakan sama ada kuantiti lulus selepas rework disertakan. |
| Yield langkah | [Kuantiti lulus langkah / kuantiti input langkah] | Langkah / peralatan / lot | Tentukan titik masuk dan keluar langkah. |
| First-pass yield | [Kuantiti lulus terus tanpa rework / kuantiti input] | Produk / langkah | Menunjukkan kos rework tersembunyi. |
| Kadar scrap | [Kuantiti scrap / kuantiti input] | Kecacatan / langkah | Pisahkan daripada rework, hold dan pending disposition. |
| Sumbangan kehilangan yield | [Kehilangan bagi kecacatan atau langkah / jumlah kehilangan] | Kecacatan / langkah | Digunakan untuk analisis Pareto. |

Peraturan:

- Definisikan pengangka, penyebut, kuantiti input, kuantiti good, kuantiti defect, kuantiti scrap dan kuantiti rework.
- Nyatakan sama ada lot engineering, lot pilot, lot hold, rekod retest, rekod rework dan lot dibatalkan disertakan.
- Tetapkan atribusi masa: masa input, masa selesai langkah, masa selesai ujian atau masa gudang.
- Metrik yang sama mesti menggunakan logik pengiraan yang sama dalam KPI, trend, jadual perincian dan eksport.
- Tetapkan ketepatan peratus, unit, pembundaran dan pengendalian nilai kosong.

## 6. Penerangan Data dan Kontrak Data

| Sumber | Jadual / view / API | Penerangan | Grain | Refresh | Pemilik |
| --- | --- | --- | --- | --- | --- |
| DS-01 | [Rekod lot/langkah MES] | Lot, langkah proses, input/output, masa langkah. | Lot + langkah | [Realtime / setiap jam / harian] | [TBD] |
| DS-02 | [QMS / rekod pemeriksaan kecacatan] | Kod kecacatan, kategori, keputusan disposition. | Panel / kecacatan | [TBD] | [TBD] |
| DS-03 | [Sistem ujian] | Keputusan ujian electrical, final atau reliability. | Panel / unit | [TBD] | [TBD] |
| DS-04 | [Work order / data induk produk] | Produk, material, pelanggan, versi, target yield. | Produk / order | [TBD] | [TBD] |
| DS-05 | [Log peralatan / parameter] | Peralatan, mesin, parameter utama, amaran. | Peralatan / masa | [TBD] | [TBD] |

| Medan | Sumber | Jenis | Wajib | Definisi bisnes |
| --- | --- | --- | --- | --- |
| lot_id | MES | String | Ya | ID lot unik. |
| panel_id | MES / QMS | String | Disyorkan | ID panel unik untuk drill-down. |
| product_code / material_no | Data induk | String | Ya | Dimensi produk atau material. |
| process_step | MES | String | Ya | Langkah proses atau operasi. |
| equipment_id | MES / log peralatan | String | Disyorkan | Dimensi peralatan atau line. |
| defect_code / defect_type | QMS | String | Disyorkan | Kod dan kategori kecacatan. |
| input_qty / pass_qty / fail_qty / scrap_qty / rework_qty | MES / QMS | Number | Ya | Kuantiti asas untuk kiraan yield dan kehilangan. |
| event_time | Semua sumber | DateTime | Ya | Digunakan untuk penapis tempoh dan semakan refresh. |

Peraturan kualiti data:

- Tetapkan kunci hubungan silang sistem: lot_id, panel_id, work_order, process_step, equipment_id.
- Kendalikan rekod duplikasi, data lewat, langkah proses hilang, kod kecacatan hilang dan rekod pending disposition.
- Tetapkan SLA refresh dan cara masa refresh terakhir dipaparkan.
- Tetapkan kaedah padanan dengan sistem sumber dan toleransi yang dibenarkan.
- Dokumentasikan impak backfill sejarah, kiraan semula dan perubahan definisi.

## 7. Dimensi Analisis dan Penapis

| Dimensi | Contoh | Tujuan |
| --- | --- | --- |
| Masa | Hari / minggu / bulan / shift | Trend, perbandingan tempoh, lokasi abnormal. |
| Produk | Keluarga produk / material / pelanggan / versi | Perbandingan yield produk dan pengurusan sasaran. |
| Proses | Langkah / line / peralatan | Cari sumber kehilangan proses. |
| Lot | Work order / lot / panel | Penjejakan perincian dan semakan lot abnormal. |
| Kecacatan | Kategori / kod / disposition | Pareto dan punca akar. |

| Penapis | Kawalan | Lalai | Wajib | Nota |
| --- | --- | --- | --- | --- |
| Julat tarikh | Date picker | 30 hari terkini / tempoh terkini | Ya | Hadkan julat pertanyaan maksimum. |
| Produk / material | Select boleh cari | Semua atau skop pengguna | Tidak | Tapis mengikut kebenaran jika perlu. |
| Lot / panel | Kotak carian | Kosong | Tidak | Sokong carian tepat. |
| Langkah proses | Multi-select | Semua | Tidak | Kaitkan carta dan perincian. |
| Kategori kecacatan | Multi-select | Semua | Tidak | Kaitkan Pareto dan jadual perincian. |
| Peralatan / line | Multi-select | Semua | Tidak | Cari abnormal berkaitan peralatan. |

## 8. Sistem Metrik

| Metrik | Penerangan | Paparan | Sasaran / ambang |
| --- | --- | --- | --- |
| Kuantiti input | Jumlah kuantiti dalam skop analisis. | KPI / perincian | [TBD] |
| Kuantiti good | Kuantiti lulus mengikut definisi diluluskan. | KPI / perincian | [TBD] |
| Kuantiti defect | Kuantiti fail, scrap atau pending disposition. | KPI / Pareto | [TBD] |
| Yield keseluruhan | Metrik yield utama. | KPI / trend | [Target yield] |
| Yield langkah | Yield mengikut langkah proses. | Matriks / bar | [Sasaran langkah] |
| Sumbangan kecacatan | Sumbangan kecacatan kepada kehilangan yield. | Pareto | Top N |
| Kiraan lot abnormal | Lot di bawah ambang atau dengan perubahan abnormal. | KPI / perincian | [Garis amaran] |

## 9. Paparan Halaman dan Carta

| Kawasan | Kandungan / tingkah laku |
| --- | --- |
| Kawasan penapis atas | Tarikh, produk, lot, langkah, kecacatan, peralatan; query, reset, eksport. |
| Kawasan KPI | Yield keseluruhan, beza sasaran, input, good, kehilangan, lot abnormal. |
| Kawasan trend | Trend yield, garis sasaran, perbandingan tempoh dan penanda abnormal. |
| Kawasan analisis | Matriks yield langkah, Pareto kecacatan, perbandingan produk/material, perbandingan peralatan. |
| Kawasan perincian | Lot, panel, langkah proses, kecacatan, peralatan, kuantiti dan status. |

| ID carta | Nama carta | Jenis | Metrik utama | Dimensi | Interaksi |
| --- | --- | --- | --- | --- | --- |
| CH-01 | Trend Yield Keseluruhan ABF | Line chart | Yield keseluruhan / target yield | Tarikh | Klik titik abnormal untuk menapis perincian. |
| CH-02 | Kehilangan Yield Langkah Proses | Bar / heatmap | Yield langkah / kuantiti kehilangan | Langkah | Klik langkah untuk drill-down ke kecacatan dan lot. |
| CH-03 | Pareto Kecacatan | Pareto | Sumbangan kecacatan / kuantiti defect | Kategori kecacatan | Klik kecacatan untuk menapis perincian. |
| CH-04 | Perbandingan Produk / Material | Bar chart | Yield / kuantiti input | Produk / material | Susun dan eksport. |
| CH-05 | Perincian Lot / Panel | Jadual | Yield, kuantiti, status | Lot / panel | Pagination, sort, drill-down. |

## 10. Drill-down dan Analisis Punca Akar

| Laluan | Penerangan | Output |
| --- | --- | --- |
| Produk -> lot | Lihat lot yield rendah di bawah produk. | Senarai lot, yield lot, beza sasaran. |
| Lot -> panel | Lihat taburan panel dalam lot. | Yield panel, kiraan kecacatan, status. |
| Panel -> langkah | Jejaki prestasi panel pada setiap langkah. | Pass/fail langkah, masa, peralatan. |
| Langkah -> kecacatan | Lihat kecacatan utama pada langkah dipilih. | Pareto kecacatan dan perincian. |
| Kecacatan -> peralatan / parameter | Semak sama ada kecacatan tertumpu pada peralatan atau julat parameter. | Perbandingan peralatan, nota parameter, rekod penambahbaikan. |

## 11. Amaran dan Penutupan Penambahbaikan

| Amaran | Syarat pencetus | Tahap | Penerima | SLA |
| --- | --- | --- | --- | --- |
| Yield keseluruhan bawah sasaran | [Overall yield < target - tolerance] | High / Medium | Kualiti / pembuatan | [TBD] |
| Yield langkah abnormal | [Yield langkah bawah ambang atau turun mengikut tempoh] | High / Medium | Proses / peralatan | [TBD] |
| Peningkatan kecacatan | [Peratus kecacatan melebihi ambang] | Medium | Kualiti / proses | [TBD] |
| Refresh abnormal | [Refresh melebihi SLA] | Medium | Pemilik data | [TBD] |

Medan penutupan: jabatan bertanggungjawab, kategori punca, tindakan sementara, tindakan jangka panjang, tarikh siap, syarat tutup, nota semakan.

## 12. Interaksi, Kebenaran dan Eksport

| Keperluan | Tingkah laku dijangka |
| --- | --- |
| Penapis berkait | Klik titik trend, langkah, kecacatan atau produk mengemas kini carta dan perincian berkaitan. |
| Tooltip | Paparkan nilai metrik, pengangka/penyebut, beza sasaran, tempoh, penapis dan nota definisi. |
| Drill-down perincian | Jadual perincian mesti sepadan dengan penapis semasa dan skop kebenaran. |
| Eksport | Eksport imej carta atau CSV/Excel perincian untuk penapis semasa; sertakan konteks penapis. |
| Kebenaran | Pengguna hanya melihat produk, line, pelanggan atau plant yang dibenarkan. |
| Audit | Rekod eksport, paparan perincian sensitif, penutupan amaran dan perubahan tindakan. |

## 13. Spesifikasi Teknikal dan Keperluan Bukan Fungsi

| Kategori | Keperluan |
| --- | --- |
| API / agregasi | Tetapkan parameter request, struktur response, pagination, sorting, tahap agregasi dan kod ralat. |
| Prestasi | Carta skrin pertama dalam penapis lalai disasar siap dalam 3 saat; query besar perlu prompt atau eksport async. |
| Ketepatan data | KPI, carta, jadual perincian dan eksport mesti konsisten di bawah penapis yang sama. |
| Kebolehpercayaan | Kegagalan satu carta tidak merosakkan halaman; paparkan ralat per carta dan retry. |
| Keselamatan | Ikut kebenaran peranan dan lindungi maklumat pelanggan, produk atau proses sensitif ketika eksport. |
| Aksesibiliti | Status tidak bergantung kepada warna sahaja; carta perlukan tajuk, unit dan label boleh dibaca. |
| Kebolehselenggaraan | Formula yield, sasaran dan konfigurasi carta sebaiknya boleh dikonfigurasi. |

## 14. Kriteria Penerimaan

| ID | Kriteria | Pemilik | Status |
| --- | --- | --- | --- |
| AC-01 | Formula yield, pengangka, penyebut, pengecualian dan peraturan rework/retest diluluskan. | Bisnes / data | Pending |
| AC-02 | KPI, trend, langkah, Pareto kecacatan dan perincian sepadan dengan query sumber dalam penapis lalai. | QA / data | Pending |
| AC-03 | Penapis tarikh, produk, lot, langkah, kecacatan dan peralatan berfungsi dan boleh di-reset. | QA | Pending |
| AC-04 | Selepas drill-down, carta, perincian dan eksport mengekalkan konteks yang sama. | QA / produk | Pending |
| AC-05 | Had kebenaran, paparan medan sensitif dan peraturan eksport memenuhi keperluan keselamatan. | Keselamatan / QA | Pending |
| AC-06 | Loading, empty, error, alert dan last-refresh dipaparkan dengan betul. | QA / UI | Pending |
| AC-07 | Halaman berfungsi dalam pelayar sasaran dan saiz skrin utama tanpa overlap, truncation atau label tidak boleh dibaca. | QA / UI | Pending |

## 15. Soalan Terbuka dan Log Perubahan

| ID | Soalan | Pemilik | Tarikh akhir | Keputusan |
| --- | --- | --- | --- | --- |
| Q-01 | Adakah definisi yield akhir memasukkan kuantiti yang lulus selepas rework? | Kualiti / pembuatan | [YYYY-MM-DD] | Open |
| Q-02 | Adakah lot engineering, pilot dan hold termasuk dalam analisis lalai? | Pemilik bisnes | [YYYY-MM-DD] | Open |
| Q-03 | Sistem mana yang menyelenggara target yield dan ambang amaran? | Data / kualiti | [YYYY-MM-DD] | Open |
| Q-04 | Adakah amaran perlu mencetuskan notifikasi automatik atau hanya dipaparkan di dashboard? | Produk / bisnes | [YYYY-MM-DD] | Open |
| Q-05 | Adakah eksport perincian perlu masking mengikut pelanggan, material atau peranan? | Keselamatan / bisnes | [YYYY-MM-DD] | Open |

| Versi | Tarikh | Pengarang | Perubahan |
| --- | --- | --- | --- |
| v0.1 | [YYYY-MM-DD] | [Nama] | Memulakan templat analisis yield ABF. |
