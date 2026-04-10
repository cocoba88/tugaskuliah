📘 README – Tugas Praktikum Reverse Engineering APK
👨‍🏫 Mata Kuliah: Keamanan Aplikasi Mobile
📌 Dosen Pengampu: (Budi Doremi)
🧪 Deskripsi Tugas

Pada praktikum ini, mahasiswa akan melakukan analisis dan modifikasi terbatas terhadap sebuah file APK yang telah disediakan oleh dosen.

APK yang digunakan dalam tugas ini adalah:

⚠️ APK Dummy (Simulasi)
Aplikasi ini dibuat khusus untuk keperluan pembelajaran, bukan aplikasi komersial.
Seluruh mekanisme di dalamnya (termasuk sistem “premium”) hanyalah simulasi.

🎯 Tujuan Pembelajaran

Mahasiswa diharapkan mampu:

Memahami struktur internal file APK
Melakukan proses decompile dan rebuild aplikasi
Menganalisis alur logika dalam kode (smali)
Mengidentifikasi mekanisme pembatasan fitur dalam aplikasi
Melakukan modifikasi sederhana sebagai simulasi analisis keamanan
🛠️ Tools yang Digunakan

Silakan gunakan tools berikut:

Apktool
https://github.com/iBotPeaches/Apktool/releases/download/v3.0.1/apktool_3.0.1.jar
Uber APK Signer
https://github.com/patrickfav/uber-apk-signer/releases/download/v1.3.0/uber-apk-signer-1.3.0.jar
Java (JDK 8+)
🔧 Tools Tambahan (Opsional)
JADX (Decompiler GUI) → untuk melihat kode Java
VSCode / Notepad++ → untuk edit file smali
Android Studio → untuk analisis tambahan
ADB (Android Debug Bridge) → untuk install & testing
📂 Alur Pengerjaan
1. Decompile APK
java -jar apktool_3.0.1.jar d app.apk
2. Analisis Struktur

Perhatikan bagian berikut:

AndroidManifest.xml
Folder smali/
Folder res/
3. Analisis Logika Aplikasi

Mahasiswa diminta untuk:

Mengidentifikasi bagian yang mengatur fitur aplikasi
Memahami bagaimana aplikasi membedakan fitur biasa dan fitur “premium” (simulasi)
Menjelaskan alur logika tersebut dalam laporan
4. Modifikasi (Simulasi)

Lakukan modifikasi sederhana pada APK untuk:

Menguji pemahaman terhadap alur logika aplikasi
Membuktikan bahwa mahasiswa memahami struktur kode

⚠️ Catatan:
Modifikasi dilakukan hanya pada APK dummy ini dan tidak boleh diterapkan pada aplikasi nyata

5. Rebuild APK
java -jar apktool_3.0.1.jar b app
6. Sign APK
java -jar uber-apk-signer-1.3.0.jar --apks app/dist/
📊 Output yang Harus Dikumpulkan

Mahasiswa wajib mengumpulkan:

Laporan (PDF) berisi:
Penjelasan struktur APK
Hasil analisis logika aplikasi
Penjelasan perubahan yang dilakukan
Screenshot proses:
Decompile
Editing
Rebuild & install
APK hasil modifikasi (opsional)
⚠️ Aturan & Etika
APK yang digunakan adalah khusus untuk pembelajaran
Dilarang keras:
Menggunakan teknik ini pada aplikasi berbayar nyata
Menyebarkan hasil modifikasi ke publik
Melanggar lisensi software

Pelanggaran terhadap aturan ini akan dikenakan sanksi akademik.

🧠 Kriteria Penilaian
Aspek	Bobot
Pemahaman struktur APK	30%
Analisis logika	30%
Implementasi modifikasi	20%
Kerapihan laporan	20%
⏰ Deadline



📌 Catatan Tambahan
APK ini sengaja dirancang memiliki struktur yang dapat dianalisis
Tidak semua bagian perlu dimodifikasi
Fokus utama adalah pemahaman keamanan
