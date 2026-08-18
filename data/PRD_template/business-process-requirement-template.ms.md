# Templat Keperluan Proses Perniagaan
> Gunakan templat ini untuk mengesahkan proses perniagaan, data yang diperlukan, tingkah laku halaman, kebenaran, integrasi, keperluan bukan fungsi dan kriteria penerimaan sebelum pembangunan bermula.  
> Gantikan kandungan dalam `[]` dengan maklumat projek sebenar dan buang perkara yang tidak berkaitan.

## 1. Maklumat Dokumen Asas

| Medan | Kandungan |
| --- | --- |
| Nama templat | Templat Keperluan Proses Perniagaan |
| Nama dokumen | [D.CHQ.QDM Keperluan Proses Perniagaan] |
| ID dokumen | [Cadangan: BRD-QDM-001] |
| Nama proses perniagaan | [Untuk dilengkapkan] |
| Pemilik perniagaan | [Untuk dilengkapkan] |
| Pemilik proses / pemilik produk | [Untuk dilengkapkan] |
| Penulis | [Untuk dilengkapkan] |
| Tarikh penciptaan | [YYYY-MM-DD] |
| Versi semasa | v0.1 Draf |
| Status dokumen | Draf / Dalam Semakan / Diluluskan |
| Sasaran keluaran / milestone | [Untuk dilengkapkan] |
| Sistem berkaitan | [Sistem upstream, downstream, workflow, pelaporan dan pengesahan] |
| Tahap kerahsiaan | Dalaman |

### 1.1 Sejarah Versi

| Versi | Tarikh | Penulis | Ringkasan perubahan | Pelulus |
| --- | --- | --- | --- | --- |
| v0.1 | [Tarikh] | [Penulis] | Struktur awal keperluan disediakan. | [Pelulus] |
| v0.2 | [Tarikh] | [Penulis] | [Kemas kini selepas semakan perniagaan] | [Pelulus] |

## 2. Latar Belakang dan Objektif

### 2.1 Latar Belakang

[Terangkan latar belakang proses semasa, masalah perniagaan, isu operasi dan sebab proses ini perlu diseragamkan atau disokong oleh sistem.]

Penerangan: Proses perniagaan memerlukan workflow yang jelas dan boleh diaudit merangkumi input data, pengesahan, kelulusan, pelaksanaan, penjejakan dan konfigurasi. Dokumen ini perlu dilengkapkan oleh pihak berkepentingan perniagaan dan teknikal.

### 2.2 Objektif

- Takrifkan proses hujung-ke-hujung dan pemilikan setiap langkah.
- Kenal pasti sumber data, medan utama, logik validasi dan jangkaan kualiti data.
- Nyatakan halaman, fungsi, kebenaran dan konfigurasi yang diperlukan oleh pengguna.
- Dokumentasikan keperluan teknikal, integrasi, bukan fungsi dan penerimaan untuk pembangunan dan ujian.
- Rekod soalan terbuka dan titik kelulusan sebelum pelaksanaan.

## 3. Skop

| Kawasan skop | Termasuk | Tidak termasuk | Nota |
| --- | --- | --- | --- |
| Workflow perniagaan | [Untuk dilengkapkan] | [Untuk dilengkapkan] | Sahkan langkah permulaan, semakan, kelulusan, penolakan, pengecualian dan penutupan. |
| Pengurusan data | [Untuk dilengkapkan] | [Untuk dilengkapkan] | Termasuk pemilikan data, jadual sumber, peraturan penyegaran dan jangkaan pengekalan. |
| Antara muka pengguna | [Untuk dilengkapkan] | [Untuk dilengkapkan] | Termasuk senarai halaman, akses peranan, penapis, tindakan dan sejarah audit. |
| Pelaporan / analitik | [Untuk dilengkapkan] | [Untuk dilengkapkan] | Sahkan dashboard, eksport dan laporan operasi. |

## 4. Pihak Bertanggungjawab dan Berkepentingan

| Peranan | Nama / pasukan | Tanggungjawab | Kuasa keputusan | Hubungan |
| --- | --- | --- | --- | --- |
| Penaja perniagaan | [Untuk dilengkapkan] | Memiliki hasil perniagaan, pembiayaan dan keutamaan. | Ya / Tidak | [E-mel/IM] |
| Pemilik perniagaan | [Untuk dilengkapkan] | Menetapkan polisi proses dan mengesahkan kelengkapan keperluan. | Ya / Tidak | [E-mel/IM] |
| Operator proses | [Untuk dilengkapkan] | Melaksanakan aktiviti harian dan melaporkan isu operasi. | Tidak | [E-mel/IM] |
| Pemilik IT | [Untuk dilengkapkan] | Memiliki reka bentuk teknikal, penghantaran pembangunan dan kesediaan deployment. | Ya / Tidak | [E-mel/IM] |
| Pemilik data | [Untuk dilengkapkan] | Mengesahkan jadual sumber, medan, kualiti data dan pengekalan. | Ya / Tidak | [E-mel/IM] |
| QA / penguji | [Untuk dilengkapkan] | Menyediakan kes ujian dan mengesahkan kriteria penerimaan. | Tidak | [E-mel/IM] |
| Keselamatan / pematuhan | [Untuk dilengkapkan] | Menyemak kebenaran, audit, perlindungan data dan pematuhan. | Ya / Tidak | [E-mel/IM] |

## 5. Penerangan Data

### 5.1 Sumber Data

| Nama sumber | Jenis | Pemilik | Kekerapan segar semula | Penggunaan dalam proses | Nota |
| --- | --- | --- | --- | --- | --- |
| XXX_Table | Jadual pangkalan data | [Pemilik data] | Masa nyata / Harian / Manual | Sumber utama data proses. | Sahkan nama jadual dan persekitaran sebenar. |
| [Sumber cadangan] | API / Fail / Input manual | [Pemilik] | [Kekerapan] | [Penggunaan] | [Nota] |

### 5.2 Medan Utama dan Kamus Data

| Nama medan | Definisi perniagaan | Jenis data | Wajib | Validasi / logik | Contoh |
| --- | --- | --- | --- | --- | --- |
| XXX_Fields | [Terangkan maksud perniagaan medan ini] | Teks / Nombor / Tarikh | Ya / Tidak | [Peraturan validasi] | [Nilai contoh] |
| Request ID | Pengenal unik untuk setiap contoh proses. | Teks | Ya | Dijana sistem dan mesti unik. | QDM-2026-0001 |
| Pemohon | Pengguna yang memulakan proses. | Pengguna | Ya | Mesti pengguna aktif yang dibenarkan. | [Nama pengguna] |
| Status | Keadaan workflow semasa. | Teks | Ya | Dikawal oleh senarai status workflow. | Draft / Submitted / Approved / Rejected / Closed |
| Masa dicipta | Masa contoh proses dicipta. | DateTime | Ya | Dijana sistem. | 2026-05-20 09:30 |
| Masa kemas kini terakhir | Masa kemas kini terkini. | DateTime | Ya | Dijana selepas setiap simpan/tindakan. | 2026-05-20 10:15 |

### 5.3 Logik Data dan Peraturan Kualiti

| ID peraturan | Penerangan | Pencetus | Tingkah laku sistem | Mesej ralat / amaran |
| --- | --- | --- | --- | --- |
| DQ-01 | Medan wajib mesti lengkap sebelum penghantaran. | Hantar | Sekat penghantaran dan sorot medan yang hilang. | Sila lengkapkan semua medan wajib sebelum menghantar. |
| DQ-02 | Hanya peralihan status yang sah dibenarkan. | Tindakan workflow | Benarkan tindakan hanya apabila peranan dan status sepadan. | Tindakan ini tidak tersedia untuk status semasa. |
| DQ-03 | [Peraturan cadangan] | [Pencetus] | [Tingkah laku] | [Mesej] |

## 6. Penerangan Proses

### 6.1 Carta Alir

[Masukkan carta alir akhir selepas workflow disahkan.]

Notasi dicadangkan: Mula, tindakan pengguna, validasi sistem, keputusan kelulusan, gelung penolakan, selesai dan laluan pengecualian.

### 6.2 Matriks Langkah Workflow

| Langkah | Aktor / peranan | Input | Aktiviti | Output sistem | Status seterusnya |
| --- | --- | --- | --- | --- | --- |
| 1 | Pemohon | Data perniagaan dan lampiran | Cipta permintaan proses dan simpan draf. | Rekod draf dicipta. | Draft |
| 2 | Pemohon | Permintaan lengkap | Hantar permintaan untuk semakan. | Keputusan validasi dan tugasan workflow. | Submitted |
| 3 | Pelulus / penyemak | Permintaan dihantar | Semak butiran, komen dan data sokongan. | Keputusan kelulusan direkodkan. | Approved / Rejected |
| 4 | Sistem | Permintaan diluluskan | Kemas kini status, tulis sejarah audit dan maklumkan pengguna berkaitan. | Rekod proses selesai. | Closed / Completed |
| 5 | Pemohon | Permintaan ditolak | Baiki dan hantar semula atau batalkan. | Permintaan dan sejarah dikemas kini. | Draft / Cancelled |
| 6 | [Peranan cadangan] | [Input] | [Pengendalian pengecualian / eskalasi] | [Output] | [Status] |

## 7. Peraturan Perniagaan

| ID peraturan | Peraturan perniagaan | Pemilik | Keutamaan | Catatan |
| --- | --- | --- | --- | --- |
| BR-01 | Proses mesti mengekalkan jejak audit lengkap untuk penciptaan, penghantaran, kelulusan, penolakan, penyerahan semula dan penutupan. | Perniagaan / IT | Tinggi | Sejarah audit perlu kelihatan pada halaman butiran. |
| BR-02 | Hanya pengguna dibenarkan boleh memulakan, menyemak, meluluskan, mengkonfigurasi atau mengurus kebenaran. | Perniagaan / Keselamatan | Tinggi | Peta kepada matriks kebenaran. |
| BR-03 | Permintaan ditolak mesti menyimpan komen penyemak dan membenarkan pembetulan. | Perniagaan | Sederhana | Sahkan sama ada penghantaran semula menggunakan Request ID sama. |
| BR-04 | [Peraturan cadangan] | [Pemilik] | Tinggi / Sederhana / Rendah | [Catatan] |

## 8. Persembahan Halaman / Fungsi

| Halaman / fungsi | Tujuan | Komponen utama | Tindakan utama | Peranan akses |
| --- | --- | --- | --- | --- |
| Halaman permulaan proses | Membolehkan pengguna dibenarkan mencipta dan menghantar permintaan. | Borang, medan wajib, lampiran, simpan draf, hantar. | Simpan, Hantar, Batal | Pemohon |
| Senarai tugasan proses | Menunjukkan tugasan yang memerlukan tindakan pengguna. | Senarai tugasan, penapis, status, tarikh akhir, pemilik, pintasan tindakan. | Buka, Lulus, Tolak, Serah semula | Penyemak / Pelulus |
| Butiran dan sejarah proses | Menunjukkan butiran proses dan jejak audit. | Ringkasan, medan data, komen, garis masa sejarah, lampiran. | Komen, Eksport, Cetak | Peranan dibenarkan |
| Konfigurasi | Menyelenggara nilai boleh konfigurasi. | Senarai status, peraturan routing, ambang, templat notifikasi. | Tambah, Edit, Nyahaktif | Admin |
| Pengurusan kebenaran | Mengurus akses berasaskan peranan. | Pemetaan pengguna-peranan, akses fungsi, skop data. | Beri, Tarik balik, Audit | Keselamatan / Admin |
| [Halaman laporan] | Memberi keterlihatan operasi dan eksport. | Penapis, ringkasan KPI, jadual, eksport. | Cari, Eksport | [Peranan] |

### 8.1 Tingkah Laku UI dan Keperluan Susun Atur

| Kawasan | Keperluan | Keutamaan |
| --- | --- | --- |
| Responsif | Halaman mesti menyokong desktop dan tablet biasa tanpa limpahan mendatar. | Tinggi |
| Validasi borang | Mesej wajib, format dan peraturan perniagaan muncul berhampiran medan berkaitan. | Tinggi |
| Carian dan penapis | Senarai perlu menyokong carian kata kunci, status, pemilik dan julat tarikh jika berkaitan. | Sederhana |
| Keterlihatan audit | Halaman butiran mesti menunjukkan masa, aktor, tindakan, komen dan status hasil. | Tinggi |
| Keadaan kosong / ralat | Halaman mesti menyediakan keadaan kosong, memuat dan ralat yang jelas. | Sederhana |

## 9. Kebenaran dan Kawalan

| Fungsi | Pemohon | Penyemak | Pelulus | Admin | Keselamatan |
| --- | --- | --- | --- | --- | --- |
| Cipta permintaan | Cipta | Lihat | Lihat | Lihat | Lihat |
| Hantar permintaan | Hantar sendiri | Tidak | Tidak | Tidak | Tidak |
| Semak permintaan | Lihat sendiri | Semak | Lulus / Tolak | Lihat | Lihat |
| Edit konfigurasi | Tidak | Tidak | Tidak | Edit | Lihat |
| Urus kebenaran | Tidak | Tidak | Tidak | Lihat | Edit |
| Eksport data | [Sahkan] | [Sahkan] | [Sahkan] | [Sahkan] | [Sahkan] |

## 10. Keperluan Audit dan Pematuhan

- Rekod setiap tindakan workflow dengan aktor, cap masa, status asal, status baharu, komen dan halaman sumber.
- Hadkan data sensitif mengikut peranan dan skop data.
- Takrifkan tempoh pengekalan dan pendekatan arkib sebelum go-live.
- Sahkan sama ada eksport data memerlukan kelulusan, masking atau watermark.

## 11. Keperluan Pembangunan

### 11.1 Spesifikasi Teknikal

[Jika stack lalai templat digunakan, bangunkan dengan HTML, Bootstrap, JavaScript dan jQuery. Kod perlu bersih, berstruktur, dikomen jika berguna, responsif dan mudah untuk pembangunan susulan.]

Jika projek menetapkan stack lain, ikut stack yang disahkan sambil mengekalkan keperluan fungsi, UI, kebenaran, audit dan penerimaan.

### 11.2 Sistem Warna

| Token | Nilai | Penggunaan |
| --- | --- | --- |
| Background | #f6f8fb / #f3f5f7 | Permukaan latar aplikasi. |
| Panel | #ffffff | Kad, panel dan borang. |
| Hover surface | #eef2f4 | Keadaan hover dan interaksi sekunder. |
| Soft blue panel | #f0f6ff | Panel maklumat lembut. |
| Primary text | #111315 | Teks utama dan label. |
| KMS text | #17202a | Penekanan teks gaya KMS. |
| Secondary text | #424a55 / #647280 | Teks bantuan dan metadata. |
| Border | #d9e1e7 / rgba(17,19,21,0.17) | Sempadan dan pemisah lalai. |
| Active border | rgba(17,19,21,0.28) | Fokus dan terpilih. |
| Primary blue | #2563eb | Tindakan utama dan indikator aktif. |
| Danger / error / warning | #c2413b / #b43636 / #a56313 | Ralat, amaran dan risiko. |

## 12. Keperluan Integrasi dan Antara Muka

| Antara muka | Arah | Data / payload | Kekerapan | Pengendalian gagal | Pemilik |
| --- | --- | --- | --- | --- | --- |
| [API / jadual] | Masuk / Keluar | [Payload] | [Kekerapan] | Cuba semula / amaran / pembetulan manual | [Pemilik] |
| Pengesahan / SSO | Masuk | Identiti pengguna dan atribut peranan | Semasa log masuk | Tolak akses dan papar mesej kebenaran. | IT / Keselamatan |
| Perkhidmatan notifikasi | Keluar | Tugasan, keputusan kelulusan, komen penolakan | Berdasarkan peristiwa | Log kegagalan dan benarkan hantar semula. | IT |

## 13. Keperluan Bukan Fungsi

| Kategori | Keperluan | Sasaran / ukuran | Keutamaan |
| --- | --- | --- | --- |
| Prestasi | Senarai dan butiran perlu dimuat dalam masa dipersetujui di bawah volum biasa. | [cth. <= 3 saat] | Tinggi |
| Ketersediaan | Sistem tersedia semasa waktu perniagaan dan tetingkap penyelenggaraan. | [Untuk dilengkapkan] | Tinggi |
| Keselamatan | Akses berasaskan peranan dan sejajar dengan matriks kebenaran. | Tiada akses tidak dibenarkan semasa ujian. | Tinggi |
| Kebolehgunaan | Pengguna boleh melengkapkan aliran hantar/semak tanpa input semula manual. | Disahkan dalam UAT. | Sederhana |
| Kebolehselenggaraan | Nilai konfigurasi boleh disenggara tanpa perubahan kod jika praktikal. | Boleh dikonfigurasi admin. | Sederhana |

## 14. Kriteria Penerimaan dan Ujian

| AC ID | Kriteria penerimaan | Kaedah ujian | Pemilik | Status |
| --- | --- | --- | --- | --- |
| AC-01 | Pemohon boleh mencipta, menyimpan, menghantar dan melihat permintaan dengan validasi medan wajib. | Ujian fungsi / UAT | QA / Perniagaan | Belum mula |
| AC-02 | Pelulus boleh meluluskan atau menolak dan komen disimpan dalam sejarah audit. | Ujian fungsi / UAT | QA / Perniagaan | Belum mula |
| AC-03 | Peraturan kebenaran menghalang pengguna tidak dibenarkan. | Ujian keselamatan | QA / Keselamatan | Belum mula |
| AC-04 | Medan sumber data dan logik validasi sepadan dengan kamus data diluluskan. | Ujian validasi data | QA / Pemilik data | Belum mula |

## 15. Risiko, Kebergantungan dan Soalan Terbuka

| ID | Jenis | Penerangan | Impak | Mitigasi / tindakan seterusnya | Pemilik |
| --- | --- | --- | --- | --- | --- |
| R-01 | Keperluan | Peraturan perniagaan belum lengkap sebelum pembangunan bermula. | Kerja semula dan kelewatan UAT. | Lengkapkan semakan dan sign-off stakeholder. | Pemilik perniagaan |
| D-01 | Kebergantungan | Jadual sumber dan medan sebenar belum disahkan. | Pemetaan data tidak dapat dimuktamadkan. | Sahkan pemilik sumber dan kamus medan. | Pemilik data |
| R-02 | Keselamatan | Matriks kebenaran tidak lengkap. | Kecacatan kawalan akses. | Semak peranan dengan Keselamatan sebelum binaan. | Keselamatan |

## 16. Senarai Semak Penyempurnaan

| Item | Semakan | Status |
| --- | --- | --- |
| Maklumat dokumen | Pemilik, penulis, versi, status dan pelulus lengkap. | Open |
| Skop | Item termasuk dan tidak termasuk dipersetujui. | Open |
| Data | Jadual sumber, kamus medan dan peraturan data disahkan. | Open |
| Workflow | Carta alir, matriks langkah, status dan laluan pengecualian disahkan. | Open |
| Halaman | Senarai halaman, tindakan, wireframe dan akses peranan disahkan. | Open |
| Ujian | Kriteria penerimaan dan pemilik UAT disahkan. | Open |
