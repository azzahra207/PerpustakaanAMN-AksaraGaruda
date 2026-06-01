import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pbo_project.settings')

import django
django.setup()

import pandas as pd

from blog.models import Buku, JenisBuku

df = pd.read_csv('data_buku.csv', sep=',')

print(df.columns)

for index, row in df.iterrows():

    if index % 100 == 0:
        print(f"{index} data diproses")

    judul = str(row['JUDUL']).strip()

    try:
        jenis_buku = JenisBuku.objects.get(
            judul=judul
        )

        tanggal_masuk = pd.to_datetime(
            row['TANGGAL MASUK'],
            dayfirst=True,
            errors='coerce'
        )

        tanggal_inventaris = pd.to_datetime(
            row['TANGGAL INVENTARIS'],
            dayfirst=True,
            errors='coerce'
        )

        tanggal_masuk = None if pd.isna(tanggal_masuk) else tanggal_masuk.date()
        tanggal_inventaris = None if pd.isna(tanggal_inventaris) else tanggal_inventaris.date()

        Buku.objects.get_or_create(
            nomor_induk_buku=str(row['NOMOR INDUK BUKU']).strip(),
            defaults={
                'jenis_buku': jenis_buku,
                'nomor_inventaris': str(row['NOMOR INVENTARIS']).strip(),
                'tanggal_masuk': tanggal_masuk,
                'tanggal_inventaris': tanggal_inventaris,
                'status': 'TERSEDIA'
            }
        )

    except JenisBuku.DoesNotExist:
        print(f"JenisBuku tidak ditemukan: {judul}")
        
print("Import buku selesai!")