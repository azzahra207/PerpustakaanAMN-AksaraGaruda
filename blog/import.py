import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pbo_project.settings')

import django
django.setup()
import pandas as pd

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pbo_project.settings')
django.setup()

from blog.models import Penulis, Jenis, JenisBuku

df = pd.read_csv('jenis_buku.csv', sep=',')
df.columns = df.columns.str.strip()
for index, row in df.iterrows():

    nama_penulis = str(row['PENGARANG']).strip()
    nama_jenis = str(row['JENIS']).strip()

    penulis, created = Penulis.objects.get_or_create(
        nama=nama_penulis
    )

    jenis, created = Jenis.objects.get_or_create(
        nama=nama_jenis
    )

    JenisBuku.objects.get_or_create(
        judul=str(row['JUDUL']).strip(),
        defaults={
            'nomor_katalog': row['NOMOR KATALOG'],
            'nomor_klasifikasi': row['NOMOR KLASIFIKASI'],
            'isbn_issn': row['ISBN/ISSN'],
            'nomor_panggil_setempat': row['NOMOR PANGGIL SETEMPAT'],
            'bahasa': row['BAHASA'],
            'pengarang': penulis,
            'penerjemah': row['PENERJEMAH'],
            'editor': row['EDITOR'],
            'seri': row['SERI'],
            'edisi': row['EDISI'],
            'negara': row['NEGARA'],
            'provinsi': row['PROVINSI'],
            'kota': row['KOTA'],
            'penerbit': row['PENERBIT'],
            'tahun': None if pd.isna(row['TAHUN']) else int(row['TAHUN']),
            'subjek': row['SUBJEK'],
            'nama_pertemuan': row['NAMA PERTEMUAN'],
            'tempat_pertemuan': row['TEMPAT PERTEMUAN'],
            'tanggal_pertemuan': row['TANGGAL PERTEMUAN'],
            'harga': 0 if pd.isna(row['HARGA']) else int(row['HARGA']),            'jenis': jenis,
            'foto': 'images/Cover/default.jpg'
        }
    )

print("Import jenis buku selesai!")