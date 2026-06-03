from django.db import models
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from abc import ABC, abstractmethod
from datetime import timedelta
from django.utils import timezone
import random
import string

STATUS =(
    (0,"Draft"),
    (1,"Publish")
)


class Pengunjung(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nik = models.CharField(max_length=30, unique=True, blank=True, null=True)
    no_hp = models.CharField(max_length=20)
    foto = models.ImageField(upload_to ='images/')
    _jumlahKunjungan = models.IntegerField(default=0)
    instansi = models.CharField(max_length=100)
    alamat = models.CharField(max_length=100)
    kode_qr = models.CharField(max_length=100, unique=True, null=True)
    def __str__(self):
        return f"Pengunjung : {self.user.first_name} {self.user.last_name}"
    def get_labelId(self):
        return "NIP"
    def get_labelInstansi(self):
        return "Kampus"
    def get_labelAlamat(self):
        return "Asal Provinsi"
    @property
    def jumlahKunjungan(self):
        return self._jumlahKunjungan
    def tambah_hadir(self):
        self._jumlahKunjungan += 1
        self.save()
    def get_status(self):
        if hasattr(self, 'petugas'):
            return "Petugas"
        return "Penghuni"

class PengunjungIstimewa(Pengunjung):
    jabatan = models.CharField(max_length=50)
    tujuan = models.CharField(max_length=100)
    def __str__(self):
        return f"Tamu : {self.user.first_name} {self.user.last_name}"
    def get_labelId(self):
        return "NIP"
    def get_labelInstansi(self):
        return "Instansi"
    def get_labelAlamat(self):
        return "Asal Daerah"
    def get_status(self):
        return "Tamu"
    @classmethod
    def register(cls, username, password, first_name, last_name, nik, no_hp, instansi, alamat, jabatan, tujuan, foto=None):
        if User.objects.filter(username=username).exists():
            raise ValueError(f"Username {username} sudah digunakan")
        if cls.objects.filter(nik=nik).exists():
            raise ValueError(f"NIK {nik} sudah terdaftar")
        user = User.objects.create_user(
            username=username,
            password=password,
            first_name=first_name,
            last_name=last_name,
            email=f"{username}@tamu.amnsurabaya.id"
        )
        if not foto:
           foto = 'pejabat.jpg'
        from django.conf import settings
        kode_qr = f"{settings.QR_SCANNER_SECRET}|{nik}"
        tamu = cls.objects.create(
            user=user,
            nik=nik,
            no_hp=no_hp,
            foto=foto,
            instansi=instansi,
            alamat=alamat,
            kode_qr=kode_qr,
            jabatan=jabatan,
            tujuan=tujuan
        )
        # user.tambah_hadir()
        return tamu
 
class Petugas(models.Model):
    pengunjung = models.OneToOneField(Pengunjung, on_delete=models.CASCADE)
    jabatan = models.CharField(max_length=100)
    jumlahHadir = models.IntegerField(default=0)
    posisi = models.BooleanField(default=False)
    def __str__(self):
        return f"Petugas : {self.pengunjung.user.first_name} {self.pengunjung.user.last_name}"
    def tambah_hadir(self):
        self.jumlahHadir += 1
        self.save()
    def get_status(self):
        return "Petugas"

class Jadwal(models.Model):
    petugas = models.ForeignKey(Petugas, on_delete=models.CASCADE)
    HARI = (
        ("Monday", "Senin"),
        ("Tuesday", "Selasa"),
        ("Wednesday", "Rabu"),
        ("Thursday", "Kamis"),
        ("Friday", "Jumat"),
        ("Saturday", "Sabtu"),
        ("Sunday", "Minggu"),
    )
    hari = models.CharField(max_length=20,choices=HARI)    
    mulai = models.TimeField()
    selesai = models.TimeField()
    def __str__(self):
        return f"{self.hari} [{self.mulai}-{self.selesai}] : {self.petugas.pengunjung.user.first_name} {self.petugas.pengunjung.user.last_name}"

class Aktivitas(models.Model):
    masuk = models.DateTimeField(auto_now_add=True)
    keluar = models.DateTimeField(null=True, blank=True)
    class Meta:
        abstract = True
    def selesai(self):
        return self.keluar is not None

class Absensi(Aktivitas):
    petugas = models.ForeignKey(Petugas, on_delete=models.CASCADE, related_name='jadwal_petugas')
    jadwal = models.ForeignKey(Jadwal, on_delete=models.CASCADE, null=True,blank=True)
    STATUS = (
        ("HADIR","Hadir"),
        ("TERLAMBAT","Terlambat"),
        ("IZIN","Izin"),
        ("ALPA","Alpa")
    )
    status = models.CharField(max_length=10, choices=STATUS)
    def __str__(self):
        return f"Absensi {self.petugas} berhasil"

class Kunjungan(Aktivitas):
    pengunjung = models.ForeignKey(Pengunjung, on_delete=models.CASCADE)
    tujuan = models.TextField(null=True, blank=True)
    def __str__(self):
        return f"Kunjungan {self.pengunjung}"

class Penulis(models.Model):
    kode = models.CharField(max_length=10, null=True, blank=True)
    nama = models.CharField(max_length=200)

    def __str__(self):
        return self.nama
    
class Jenis(models.Model):
    nama = models.CharField(max_length=100)

    def __str__(self):
        return self.nama
    
    
class JenisBuku(models.Model):
    judul = models.TextField()
    nomor_katalog = models.CharField(max_length=100, null=True, blank=True)
    nomor_klasifikasi = models.CharField(max_length=100, null=True, blank=True)
    isbn_issn = models.CharField(max_length=100, null=True, blank=True)
    nomor_panggil_setempat = models.CharField(max_length=100,null=True,blank=True)
    foto = models.ImageField(upload_to ='images/Cover/')
    bahasa = models.CharField(max_length=100, null=True, blank=True)
    pengarang = models.ForeignKey(Penulis,on_delete=models.SET_NULL,null=True,blank=True,related_name='buku_pengarang')
    penerjemah = models.CharField(max_length=200, null=True, blank=True)
    editor = models.TextField(null=True, blank=True)
    seri = models.CharField(max_length=100, null=True, blank=True)
    edisi = models.CharField(max_length=100, null=True, blank=True)
    negara = models.CharField(max_length=100, null=True, blank=True)
    provinsi = models.CharField(max_length=100, null=True, blank=True)
    kota = models.CharField(max_length=100, null=True, blank=True)
    penerbit = models.CharField(max_length=200, null=True, blank=True)
    tahun = models.IntegerField(null=True, blank=True)
    subjek = models.TextField(null=True, blank=True)
    nama_pertemuan = models.TextField(null=True, blank=True)
    tempat_pertemuan = models.CharField(max_length=200,null=True,blank=True)
    tanggal_pertemuan = models.CharField(max_length=100,null=True,blank=True)
    harga = models.BigIntegerField(default=0)
    jenis = models.ForeignKey(Jenis,on_delete=models.SET_NULL,null=True,blank=True)
    def __str__(self):
        return self.judul
    @property
    def stok(self):
        return Buku.objects.filter(
            jenis_buku=self,
            status='TERSEDIA',
        ).count()

class Buku(models.Model):
    jenis_buku = models.ForeignKey(JenisBuku,on_delete=models.CASCADE)
    nomor_induk_buku = models.CharField(max_length=100,unique=True)
    nomor_inventaris = models.CharField(max_length=100,unique=True)
    tanggal_masuk = models.DateField(null=True,blank=True)
    tanggal_inventaris = models.DateField(null=True,blank=True)
    STATUS = (
        ("TERSEDIA", "Tersedia"),
        ("DIPINJAM", "Dipinjam"),
        ("RUSAK", "Rusak"),
        ("HILANG", "Hilang"),
    )
    status = models.CharField(max_length=20,choices=STATUS,default="TERSEDIA")
    def __str__(self):
        return self.nomor_induk_buku


class Peminjaman(Aktivitas):
    peminjam = models.ForeignKey(Pengunjung, on_delete=models.CASCADE)
    buku = models.ForeignKey(Buku, on_delete=models.CASCADE)
    batas_pengembalian = models.DateTimeField()
    STATUS = (
        ("DIPINJAM", "Dipinjam"),
        ("SELESAI", "Selesai"),
    )
    status = models.CharField(max_length=20, choices=STATUS, default="DIPINJAM")

    def __str__(self):
        return f"{self.peminjam} - {self.buku}"

class Pengembalian(models.Model):
    peminjaman = models.ForeignKey(Peminjaman,on_delete=models.CASCADE)
    tanggal_pengembalian = models.DateTimeField(auto_now_add=True)
    STATUS = (
        ("TEPAT_WAKTU", "Tepat Waktu"),
        ("TERLAMBAT", "Terlambat"),
    )
    status = models.CharField(max_length=20,choices=STATUS)
    denda = models.IntegerField(default=0)

    def __str__(self):
        return f"Pengembalian {self.peminjaman}"
    def __tentukan_status(self):
        if self.tanggal_pengembalian > self.peminjaman.batas_pengembalian:
            return "TERLAMBAT"
        return "TEPAT_WAKTU"
    def __hitung_denda(self):
        if self.tanggal_pengembalian > self.peminjaman.batas_pengembalian:
            terlambat = (self.tanggal_pengembalian - self.peminjaman.batas_pengembalian).days
            return terlambat * 1000
        return 0
    def save(self, *args, **kwargs):
        self.status = self.__tentukan_status()
        self.denda = self.__hitung_denda()
        super().save(*args, **kwargs)


# nanti lanjut siniiiiiii
####################### HUAAHUAAUAAAAHAHA ini cuma bekas tutorial ajaaa ;P
class Post(models.Model):
    title = models.CharField(max_length=300, unique=True)
    slug = models.SlugField(max_length=300,unique=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blog_posts')
    content = models.TextField()
    status = models.IntegerField(choices=STATUS, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ['-created_at']
    def __str__(self):
        return self.title

class MyModel(models.Model):
    image = models.ImageField(upload_to='images/')
    video = models.FileField(upload_to='videos/')
    audio = models.FileField(upload_to='audio/')
