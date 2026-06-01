import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pbo_project.settings')

import django
django.setup()

import pandas as pd
from django.contrib.auth.models import User
from blog.models import Pengunjung
from django.conf import settings

def import_pengunjung_from_excel(excel_file_path):
    """
    Import pengunjung from Excel file
    
    Expected columns:
    - NO URUT
    - NO REGISTRASI
    - NAMA LENGKAP
    - TAHUN ANGKATAN
    - UNIVERSITAS
    - PRODI
    - PROVINSI ASAL
    - JENIS KELAMIN
    """
    
    # Read Excel file - PASTIKAN NO REGISTRASI BACA SEBAGAI STRING
    df = pd.read_excel(excel_file_path, dtype={'NO REGISTRASI': str})
    
    # Print columns to verify
    print("Columns found:", df.columns.tolist())
    
    # Clean column names (remove extra spaces)
    df.columns = df.columns.str.strip()
    
    success_count = 0
    error_count = 0
    skipped_count = 0
    
    for index, row in df.iterrows():
        try:
            # Extract data from row - DENGAN PEMBERSIHAN .0
            no_registrasi_raw = str(row['NO REGISTRASI']) if pd.notna(row['NO REGISTRASI']) else ''
            # HILANGKAN .0 jika ada
            no_registrasi = no_registrasi_raw.replace('.0', '').strip()
            
            nama_lengkap = str(row['NAMA LENGKAP']).strip() if pd.notna(row['NAMA LENGKAP']) else ''
            # Remove newlines and extra spaces
            nama_lengkap = ' '.join(nama_lengkap.split())
            
            tahun_angkatan = str(row['TAHUN ANGKATAN']).strip() if pd.notna(row['TAHUN ANGKATAN']) else ''
            universitas = str(row['UNIVERSITAS']).strip() if pd.notna(row['UNIVERSITAS']) else ''
            prodi = str(row['PRODI']).strip() if pd.notna(row['PRODI']) else ''
            # Remove newlines from prodi
            prodi = ' '.join(prodi.split())
            
            provinsi_asal = str(row['PROVINSI ASAL']).strip() if pd.notna(row['PROVINSI ASAL']) else ''
            # Remove newlines from provinsi
            provinsi_asal = ' '.join(provinsi_asal.split())
            
            jenis_kelamin = str(row['JENIS KELAMIN']).strip().upper() if pd.notna(row['JENIS KELAMIN']) else ''
            
            # Skip if no_registrasi is empty
            if not no_registrasi or no_registrasi == 'nan':
                print(f"Baris {index + 2}: No Registrasi kosong, dilewati")
                skipped_count += 1
                continue
            
            # Skip if nama lengkap is empty
            if not nama_lengkap or nama_lengkap == 'nan':
                print(f"Baris {index + 2}: Nama lengkap kosong, dilewati")
                skipped_count += 1
                continue
            
            # Split nama lengkap into first_name and last_name
            nama_parts = nama_lengkap.split()
            if len(nama_parts) >= 2:
                first_name = nama_parts[0]
                last_name = ' '.join(nama_parts[1:])
            else:
                first_name = nama_lengkap
                last_name = ''
            
            # Generate username: penghuni + no_registrasi
            username = f"penghuni{no_registrasi}"
            
            # Check if username already exists
            if User.objects.filter(username=username).exists():
                print(f"Baris {index + 2}: Username {username} sudah ada, dilewati")
                skipped_count += 1
                continue
            
            # Check if NIK (no_registrasi) already exists
            if Pengunjung.objects.filter(nik=no_registrasi).exists():
                print(f"Baris {index + 2}: NIK {no_registrasi} sudah ada, dilewati")
                skipped_count += 1
                continue
            
            # Create User
            user = User.objects.create_user(
                username=username,
                password='12345678',
                first_name=first_name,
                last_name=last_name,
                email='amn@upnjatim.ac.id'
            )
            
            # Generate kode_qr: QR_SCANNER_SECRET|no_registrasi
            qr_scanner_secret = settings.QR_SCANNER_SECRET
            kode_qr = f"{qr_scanner_secret}|{no_registrasi}"
            
            # Determine foto based on gender
            if jenis_kelamin == 'L':
                foto_path = 'images/default2.png'  # foto untuk laki-laki
            elif jenis_kelamin == 'P':
                foto_path = 'images/default1.png'  # foto untuk perempuan
            else:
                # Default if gender not specified or invalid
                foto_path = 'images/default.jpg'
                print(f"Baris {index + 2}: Jenis kelamin '{jenis_kelamin}' tidak dikenal, menggunakan foto default")
            
            # Create Pengunjung
            pengunjung = Pengunjung.objects.create(
                user=user,
                nik=no_registrasi,
                no_hp='082142635182',
                foto=foto_path,
                instansi=universitas,
                alamat=provinsi_asal,
                kode_qr=kode_qr
            )
            
            success_count += 1
            
            # Print progress every row (biar keliatan)
            gender_text = "Laki-laki" if jenis_kelamin == 'L' else "Perempuan" if jenis_kelamin == 'P' else "Unknown"
            print(f"✓ {success_count}. {nama_lengkap} | Username: {username} | NIK: {no_registrasi} | {gender_text}")
                
        except Exception as e:
            print(f"✗ Error baris {index + 2}: {str(e)}")
            error_count += 1
    
    # Print summary
    print("\n" + "="*50)
    print("IMPORT SELESAI")
    print(f"✓ Berhasil: {success_count} data")
    print(f"✗ Gagal: {error_count} data")
    print(f"➤ Dilewati: {skipped_count} data")
    print(f"Total data di file: {len(df)}")
    print("="*50)
    
    # Show sample of created users
    print("\nContoh data yang berhasil diimport (5 pertama):")
    created_users = Pengunjung.objects.all().order_by('-id')[:5]
    for p in created_users:
        gender = "Laki-laki" if 'default2' in p.foto.name else "Perempuan" if 'default1' in p.foto.name else "Unknown"
        print(f"  - {p.user.username} | {p.user.first_name} {p.user.last_name} | NIK: {p.nik} | {gender}")

if __name__ == "__main__":
    # Ganti dengan path file excel Anda
    excel_file = "data_pengunjung.xlsx"
    import_pengunjung_from_excel(excel_file)