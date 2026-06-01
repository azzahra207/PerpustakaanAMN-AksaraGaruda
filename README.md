Sistem Informasi Perpustakaan Aksara Garuda
---------------------------------------
Sistem Informasi Perpustakaan Aksara Garuda Asrama Mahasiswa Nusantara Surabaya merupakan sebuah solusi yang dirancang secara spesifik untuk mengelola data peminjaman buku sebagai acuan minat pengunjung untuk memudahkan analisis kualitas dan evaluasi. Hal 
ini diimplementasikan pada fitur presensi kunjungan melalui kode QR unik yang hanya 
dimiliki masing-masing penghuni. Begitupun absensi petugas perpustakaan 
disesuaikan dengan jadwal harian. Sistem ini juga mencatat aktivitas peminjaman buku secara digital, serta menampilkan profil singkat untuk lebih dekat mengenal perpustakaan Aksara Garuda AMN Surabaya
-----------------------------------------------
Anggota Kelompok: 
1. Sidqiana Azzahra (25051204037) 
2. Amira Nahda Zafirah Baay (25051204111)       
3. Aldi Abdurrahman Nafis (25051204108)  
4. Muhammad Rizqy Yusuf (25051204182) 
-------------------------------------------------
Fitur Utama:
1. Sistem Presensi
2. Aktivitas Peminjaman Buku
3. Lihat Profil dan Rekap Data
 -------------------------------------------------
 Cara menjalankan Projek:
 1. Download seluruh file project dari repository PerpustakaanAMN-AksaraGaruda
 2. Pastikan sebelumnya sudah install mysql, laragon, visual studio code, django, python, dan hal lain yang dibutuhkan.
 3. Buka aplikasi laragon, kemudian klik "Start All" untuk menjalankan database
 4. Buka VS Code -> new Terminal -> cd menuju nama folder project
 5. aktifkan environment dengan menjalankan perintah env\Scripts\activate
 6. Jalankan program dengan perintah python manage.py runserver -> Enter.
 7. Buka browser dengan tautan http://127.0.0.1:8000 untuk melihat hasil project
 8. Halaman http://127.0.0.1:8000/admin untuk manajemen tabel di database
----------------------------------------------------
Pemrograman berorientasi objek (object oriented programming – OOP) merupakan pemrograman yang berorientasikan kepada objek, dimana semua data dan fungsi dibungkus dalam class-class atau object-object. Setiap objek dapat menerima pesan, memproses data, mengirim, menyimpan dan memanipulasi data.
•	Enkapsulasi (Encapsulation)
Proses membungkus data (atribut) dan metode dalam satu class untuk melindungi data serta mengatur aksesnya. Dalam project ini, konsep encapsulasi digunakan pada property jumlah kunjungan dan penentuan status keterlambatan pengembalian buku. Property tersebut bersifat private, sehingga tidak dapat diakses di luar classnya. Pada saat rekap kunjungan, pengembalian, dan penambahan data diperlukan method getter dan setter untuk memodifikasi property.
•	Abstraksi (Abstraction)
Menampilkan fungsi yang penting kepada pengguna dan menyembunyikan detail implementasi yang tidak diperlukan. Dalam project Django, pembuatan class abstract di dalam file models.py tidak akan dihasilkan tabel sebagaimana class pada umumnya. Sesuai fungsi dari abstraksi (pedoman dari class lainnya), class abstrak Aktivitas hanya menyimpan method kosong yang akan diisi sesuai kebutuhan class masing masing.
•	Inheritance (Pewarisan)
Mekanisme yang memungkinkan suatu kelas mewarisi atribut dan metode dari kelas lain sehingga kode dapat digunakan kembali. Dalam project ini, inheritance diterapkan pada fitur presensi kunjungan. Class Pengunjung sebagai parent dan Class Pengunjungistimewa sebagai child. Keduanya memiliki beberapa property identitas yang sama. Namun PengunjungIstimewa memiliki tambahan property jabatan serta tambahan method register yang dijalankan setiap kali melakukan kunjungan ke perpustakaan.
•	Polimorfisme (Polymorphism)
Kemampuan suatu metode atau antarmuka untuk memiliki banyak bentuk atau perilaku yang berbeda sesuai dengan objek yang menggunakannya. Contohnya operasi "membuka" dapat berarti membuka berkas, jendela, koran, atau percakapan.  Sama halnya dengan konsep dashboard yang diterapkan dalam project ini. Setiap objek class dari package user memiliki status beserta label identitas yang berbeda, namun ketiganya ditampilkan dalam dashboard yang sama. Konten akan menampilkan masing masing label status identitas dengan satu variabel yang sama, namun blok kode di dalamnya disesuaikan dengan status user yang bersangkutan.
--------------------------------------------------------------
Screenshoot Hasil tampilan dapat diakses melalui tautan gdrive berikut ini:
https://drive.google.com/drive/folders/19dCQoS_-4PisZ7PDqjNJz5NXmyhxXeyd?usp=sharing
