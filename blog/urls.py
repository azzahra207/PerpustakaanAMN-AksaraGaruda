from .import views
from django.urls import path

urlpatterns = [
    path('',views.PostList.as_view(), name = 'home'),
    path('kunjungan/', views.Penghuni, name ='kunjungan.index'),
    path('login-options/', views.login_options, name='login.options'),
    path('scanner/', views.scanner_hardware, name='scanner.hardware'),
    path('login/', views.login_biasa, name='login'),
    path('login-send/', views.login_send, name='login.send'),
    path('scanner-auth/', views.scanner_auth, name='scanner.auth'),
    path('logout/',views.logout_user,name='logout'),
    path('dashboard/',views.dashboard,name = 'dashboard'),
    path('petugas/scanner',views.show_scanner,name = 'petugas.show_scanner'),
    path('petugas/absensi',views.scan_absensi_petugas,name = 'petugas.absensi'),
    path('rekap-absensi/',views.rekap_absensi,name='rekap_absensi'),
    path('store-visit/<str:pengunjung_nik>/', views.store_visit, name='store.visit'), 
    path('buku/',views.indexBuku, name = 'buku.index'),
    path('buku/<str:id_buku>',views.showBuku, name='buku.show'),  
    path('buku/qr/<int:id>/',views.download_qr_buku,name='buku.qr'), 
    path('buku/qr/download-all/',views.download_all_qr,name='buku.qr.download_all'),
    path('buku-show-scanner/', views.show_scan_buku, name='buku.show.scanner'),
    path('scanner-buku/', views.scanner_buku, name='buku.scanner'),
    path('about-me/',views.about_me, name = 'about.me'),
    path('struktur/',views.index_petugas, name = 'struktur'),
    path('kunjungan-hari-ini/',views.KunjunganToday, name = 'kunjungan.hari.ini'),
    path('rekap-kunjungan/',views.rekap_pdf, name = 'rekap.kunjungan.pdf'),
    path('galeri/',views.galeri, name='galeri'),
    path('rekap-absensi/',views.rekap_absensi, name='rekap.absensi'),
    path('tata-tertib',views.tatib, name = 'tata.tertib'),
    path('tamu/register/', views.register_tamu, name='register.tamu'),
    path('tamu/daftar/', views.daftar_tamu, name='daftar.tamu'),
    path('kunjungan/jadwal/', views.jadwal_kunjung, name='jadwal.kunjungan'),
    path('buku/pinjam/', views.pinjam, name='buku.pinjam'),
    
    path('<slug:slug>/', views.PostDetail.as_view(), name='post_detail'),

]