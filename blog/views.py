from django.views import generic
from .models import *
import json
from django.http import JsonResponse
from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.shortcuts import render
from django.db import transaction
from django.core.paginator import Paginator
import qrcode
from io import BytesIO
import xhtml2pdf.pisa as pisa
from django.template.loader import get_template
from django.http import HttpResponse
from datetime import datetime
import re
import zipfile
import os
from django.utils.text import slugify
from PIL import Image, ImageDraw, ImageFont
import base64



QR_MASUK = "https://q.me-qr.com/i52v6v49"
QR_KELUAR = "https://q.me-qr.com/lgws7mpe"



class PostList(generic.ListView):
    """
    Return all posts that are with status 1 (published) and order fron the latest one
    """
    queryset = Post.objects.filter(status=1).order_by('created_at')
    template_name = 'index.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['books'] = JenisBuku.objects.all()[:4]
        context['petugas'] = Petugas.objects.filter(jabatan="Ketua")
        return context

class PostDetail(generic.DetailView):
    model = Post
    template_name = 'post_detail.html'

from django.shortcuts import render
from .models import Kunjungan

# def kunjungan_list(request):
#     data = Kunjungan.objects.all()

#     return render(request, 'kunjungan/index.html', {
#         'data': data
#     })

def login_options(request):
    return render(request, 'auth/login-options.html')

def index_petugas(request):
    petugas = Petugas.objects.all()
    context = {
        "petugas" : petugas
    }
    return render(request,'petugas/struktur.html', context)

def scanner_hardware(request):
    return render(request, 'auth/scanner.html')

def login_biasa(request):
    return render(request, 'auth/login.html')

@login_required
def dashboard(request):
    user = request.user
    try:
        pengunjung = user.pengunjung
        if hasattr(pengunjung, 'pengunjungistimewa'):
            pengunjung = pengunjung.pengunjungistimewa
        peminjaman_aktif = Peminjaman.objects.filter(
            peminjam=pengunjung,
            status='DIPINJAM'
        ).count()
    except Exception:
        pengunjung = None
        peminjaman_aktif = 0
    context = {
        "user": user,
        "pengunjung": pengunjung,
        "peminjaman_aktif": peminjaman_aktif,
        "status": pengunjung.get_status() if pengunjung else "Unknown"
    }

    return render(request, "dashboard.html", context)

def login_send(request):
    if request.method == 'POST':
        nik = request.POST.get('nik')
        password = request.POST.get('password')
        try:
            pengunjung = Pengunjung.objects.get(nik=nik)
            user = authenticate(
                request,
                username=pengunjung.user.username,
                password=password
            )
            if user is not None:
                login(request, user)
                messages.success(request, 'Login berhasil')
                if user.username=='22110009':
                    return redirect('kunjungan.hari.ini')
                elif user.username == '22120020':
                    return redirect('buku.index')
                else:
                    return redirect('dashboard')
            else:
                messages.error(request, 'Password salah')
        except Pengunjung.DoesNotExist:
            messages.error(request, 'NIK tidak ditemukan')

    return redirect('login')

def scanner_auth(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            raw_data = data.get('qr_code')
            
            print(f"RAW: {repr(raw_data)}")
            clean_data = raw_data.strip()
            clean_data = clean_data.replace('\n', '').replace('\r', '').replace('\t', '')
            
            if '|' not in clean_data:
                return JsonResponse({
                    'success': False,
                    'message': 'Format QR tidak valid (tidak ada pemisah |)'
                })
            
            parts = clean_data.split('|')
            
            if len(parts) < 2:
                return JsonResponse({
                    'success': False,
                    'message': f'Format QR tidak valid (hanya {len(parts)} bagian)'
                })
            
            secret = parts[0].strip()
            
            nik = None
            for part in parts[1:]:
                if part.strip():
                    nik = part.strip()
                    break
            
            if not nik:
                return JsonResponse({
                    'success': False,
                    'message': 'NIK tidak ditemukan dalam QR Code'
                })
            
            print(f"Secret: {secret}")
            print(f"NIK: {nik}")
            
            expected_secret = settings.QR_SCANNER_SECRET
            
            if secret.upper() != expected_secret.upper():
                return JsonResponse({
                    'success': False,
                    'message': 'Secret QR tidak valid'
                })
            
            pengunjung = Pengunjung.objects.filter(nik=nik).first()
            
            if not pengunjung:
                return JsonResponse({
                    'success': False,
                    'message': f'Pengunjung dengan NIK {nik} tidak ditemukan'
                })
            
            login(request, pengunjung.user)
            return JsonResponse({
                'success': True,
                'redirect': '/dashboard/'
            })

        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'message': 'Data JSON tidak valid'
            })
        except Exception as e:
            print(f"Error: {str(e)}")
            return JsonResponse({
                'success': False,
                'message': f'Terjadi kesalahan: {str(e)}'
            })

    return JsonResponse({
        'success': False,
        'message': 'Method tidak diizinkan'
    })

def store_visit(request,pengunjung_nik):
    if request.method == "POST":
        pengunjung = Pengunjung.objects.get(nik=pengunjung_nik)
        pengunjung.tambah_hadir()
        tujuan = request.POST.get('tujuan')
        Kunjungan.objects.create(
            pengunjung=pengunjung,
            tujuan=tujuan
        )
        logout(request)
        return redirect('scanner.hardware')
        # return JsonResponse({
        #     'success': True,
        #     'redirect': '/scanner'
        # })
    return JsonResponse({
        'success': False,
        'message': 'Method tidak valid'
    })

@login_required
def register_tamu(request):
    if request.method == 'POST':
        try:
            username = request.POST.get('nik')
            password = 'tamu123'
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name', '')
            nik = request.POST.get('nik')
            no_hp = request.POST.get('no_hp')
            instansi = request.POST.get('instansi')
            alamat = request.POST.get('alamat')
            jabatan = request.POST.get('jabatan')
            tujuan = request.POST.get('tujuan')
            foto = request.FILES.get('foto')
            tamu = PengunjungIstimewa.register(
                username=username,
                password=password,
                first_name=first_name,
                last_name=last_name,
                nik=nik,
                no_hp=no_hp,
                instansi=instansi,
                alamat=alamat,
                jabatan=jabatan,
                tujuan=tujuan,
                foto=foto
            )
            messages.success(
                request, 
                f" {tamu.user.first_name} {tamu.user.last_name} berhasil terdaftar!"
            )
            return redirect('register.tamu')
        except ValueError as e:
            messages.error(request, str(e))
        except Exception as e:
            messages.error(request, f"Terjadi kesalahan: {str(e)}")
    return render(request, 'kunjungan/register.html')

@login_required
def daftar_tamu(request):
    tamu_list = PengunjungIstimewa.objects.all().order_by('-id')
    context = {
        'data': tamu_list,
        'total_tamu': tamu_list.count(),
    }
    return render(request, 'kunjungan/daftar_tamu.html', context)

def logout_user(request):
    logout(request)
    messages.success(
        request,
        'Logout berhasil'
    )
    return redirect('home')

def Penghuni(request):
    data = Pengunjung.objects.all()
    return render(request, 'kunjungan/index.html', {
        'data': data
    })

def galeri(request):
    return render(request,'galeri.html')

def pinjam(request):
    pengunjung = request.user.pengunjung
    peminjaman = Peminjaman.objects.filter(peminjam = pengunjung).filter(status='SELESAI').order_by('-masuk')
    pinjam_aktif = Peminjaman.objects.filter(peminjam = pengunjung).filter(status = 'DIPINJAM').select_related('buku', 'buku__jenis_buku').order_by('-masuk')
    now = timezone.now()
    for buku in pinjam_aktif:
        sisa_hari = (buku.batas_pengembalian - now).days
        if sisa_hari < 0:
            buku.sisa_waktu = f"Terlambat {abs(sisa_hari)} hari"
        elif sisa_hari == 0:
            buku.sisa_waktu = "Hari terakhir!"
        else:
            buku.sisa_waktu = f"{sisa_hari} hari lagi"
    return render(request,'buku/pinjam.html',{
        'peminjaman':peminjaman,
        'pinjam_aktif':pinjam_aktif
    })

def KunjunganToday(request):
    bulan_angka = request.GET.get('bulan', timezone.now().month)
    tahun = request.GET.get('tahun', timezone.now().year)
    bulan_angka = int(bulan_angka)
    tahun = int(tahun)
    today = timezone.now().date()
    data = Kunjungan.objects.filter(masuk__date = today)
    return render(request,'kunjungan/today.html',{
        'data':data,
        'bulan_angka':bulan_angka,
        'tahun':tahun,
        })

def kunjungan_detail(request, id):
    kunjungan = Kunjungan.objects.get(id=id)

    if isinstance(kunjungan.pengunjung, PengunjungIstimewa):
        tipe = "ISTIMEWA"
    else:
        tipe = "BIASA"

    return render(request, "detail.html", {
        "kunjungan": kunjungan,
        "tipe": tipe
    })

def rekap_pdf(request):
    bulan_angka = request.GET.get('bulan', timezone.now().month)
    tahun = request.GET.get('tahun', timezone.now().year)
    bulan_angka = int(bulan_angka)
    tahun = int(tahun)
    today = timezone.now().date()
    nama_bulan = [
        'Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni',
        'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember'
    ]
    bulan = nama_bulan[bulan_angka - 1]
    data = Kunjungan.objects.filter(
        masuk__month=bulan_angka,
        masuk__year=tahun
    ).order_by('-masuk') 
    logo_upn_base64 = ""
    logo_amn_base64 = ""
    kop_base64 = ""
    logo_upn_path = os.path.join(settings.STATICFILES_DIRS[0], 'img', 'logoUPN.png')
    logo_amn_path = os.path.join(settings.STATICFILES_DIRS[0], 'img', 'LOGO AMN FIX.png')
    kop_path = os.path.join(settings.STATICFILES_DIRS[0], 'img', 'kop.png')
    if os.path.exists(logo_upn_path):
        with open(logo_upn_path, 'rb') as f:
            logo_upn_base64 = base64.b64encode(f.read()).decode('utf-8')
    
    if os.path.exists(logo_amn_path):
        with open(logo_amn_path, 'rb') as f:
            logo_amn_base64 = base64.b64encode(f.read()).decode('utf-8')
    if os.path.exists(kop_path):
        with open(kop_path, 'rb') as f:
            kop_base64 = base64.b64encode(f.read()).decode('utf-8')
    context = {
        'data': data,
        'bulan': bulan,
        'tahun': tahun,
        'total_pengunjung': data.count(),
        'tanggal_cetak': timezone.now().strftime('%d %B %Y %H:%M:%S'),
        'logo_upn_base64': logo_upn_base64,
        'logo_amn_base64': logo_amn_base64,
        'kop_base64': kop_base64,
        'hari':today,
    }
    
    template = get_template('kunjungan/rekapPDF.html')
    html = template.render(context)
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Rekap_Kunjungan_{bulan}_{tahun}.pdf"'
    
    pisa_status = pisa.CreatePDF(html, dest=response)
    
    if pisa_status.err:
        return HttpResponse('Terjadi error saat generate PDF: %s' % pisa_status.err)
    
    return response

def rekap(request):
    bulan_angka = request.GET.get('bulan', timezone.now().month)
    tahun = request.GET.get('tahun', timezone.now().year)
    bulan_angka = int(bulan_angka)
    tahun = int(tahun)
    nama_bulan = [
        'Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni',
        'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember'
    ]
    bulan = nama_bulan[bulan_angka - 1]
    data = Kunjungan.objects.filter(
        masuk__month=bulan_angka,
        masuk__year=tahun
    ).order_by('-masuk')
    context = {
        'data': data,
        'bulan': bulan,
        'tahun': tahun,
        'bulan_angka': bulan_angka,
        'total_pengunjung': data.count(),
        'list_bulan': nama_bulan,
        'list_tahun': range(2020, timezone.now().year + 1)
    }
    return render(request, 'kunjungan/rekap.html', context)

def show_scanner(request):
    return render(request, 'petugas/absensi.html')

def scan_absensi_petugas(request):

    if request.method != "POST":
        return JsonResponse({
            "success": False,
            "message": "Method tidak diizinkan"
        })

    data = json.loads(request.body)
    qr_code = data.get("qr_code")

    try:
        petugas = Petugas.objects.get(
            pengunjung__user=request.user
        )

    except Petugas.DoesNotExist:
        return JsonResponse({
            "success": False,
            "message": "Bukan petugas"
        })
    jadwal = Jadwal.objects.filter(
        petugas=petugas,
        hari=timezone.now().strftime("%A")
    ).first()
    absensi_aktif = Absensi.objects.filter(
        petugas=petugas,
        masuk__date=timezone.now().date(),
        keluar__isnull=True
    ).first()

    now_datetime = timezone.localtime()
    now_time = now_datetime.time()
    if qr_code == QR_MASUK:
        if absensi_aktif:
            return JsonResponse({
                "success": False,
                "message": "Kamu belum absensi keluar"
            })
        if not jadwal:
            status = "HADIR"

        else:
            if now_time <= jadwal.mulai:
                status = "HADIR"
            else:
                status = "TERLAMBAT"

        Absensi.objects.create(
            petugas=petugas,
            jadwal=jadwal,
            status=status
        )

        petugas.posisi = True
        petugas.save()

        petugas.tambah_hadir()

        return JsonResponse({
            "success": True,
            "message": f"Absensi masuk berhasil ({status})"
        })
    elif qr_code == QR_KELUAR:

        if not absensi_aktif:
            return JsonResponse({
                "success": False,
                "message": "Belum absensi masuk"
            })

        if jadwal:

            if now_time < jadwal.selesai:
                return JsonResponse({
                    "success": False,
                    "message": "Belum waktunya pulang"
                })

        absensi_aktif.keluar = timezone.now()
        absensi_aktif.save()

        petugas.posisi = False
        petugas.pengunjung.save()

        return JsonResponse({
            "success": True,
            "message": "Absensi keluar berhasil"
        })
    else:
        return JsonResponse({
            "success": False,
            "message": "QR tidak valid"
        })

@login_required
def rekap_absensi(request):
    data_rekap = []
    jadwal_semua = Jadwal.objects.all()
    hari_ini = timezone.now().date()
    for jadwal in jadwal_semua:
        absensi = Absensi.objects.filter(
            petugas=jadwal.petugas,
            jadwal=jadwal,
            masuk__date=hari_ini
        ).first()
        if absensi:
            status = absensi.status
            jam_masuk = absensi.masuk
        else:
            status = "ALPA"
            jam_masuk = None
        data_rekap.append({
            'petugas': jadwal.petugas,
            'hari': jadwal.hari,
            'mulai': jadwal.mulai,
            'selesai': jadwal.selesai,
            'status': status,
            'jam_masuk': jam_masuk
        })
    return render(request, 'petugas/rekap.html', {
        'data_rekap': data_rekap
    })

def indexBuku(request):
    books = JenisBuku.objects.all()
    judul = request.GET.get('Judul')
    if judul:
        books = books.filter(
            judul__icontains=judul
        )
    paginator = Paginator(books, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'buku/index.html', {
        'books': page_obj
    })

def showBuku(request, id_buku):
    jenis_buku = JenisBuku.objects.get(id=id_buku)
    jenis_serupa = JenisBuku.objects.filter(jenis = jenis_buku.jenis).exclude(id=id_buku)
    books = Buku.objects.filter(
        jenis_buku=jenis_buku
    )

    return render(request, 'buku/show.html', {
        'book': jenis_buku,
        'books': books,
        'jenis_serupa':jenis_serupa,
    })

def tatib(request):
    return render(request,'kunjungan/tatib.html')

def jadwal_kunjung(request):
    jadwal = Jadwal.objects.all()
    hari = {
        'Monday': 'Senin',
        'Tuesday': 'Selasa', 
        'Wednesday': 'Rabu',
        'Thursday': 'Kamis',
        'Friday': 'Jumat',
        'Saturday': 'Sabtu',
        'Sunday': 'Minggu'
    }
    hari_ini_inggris = timezone.now().strftime('%A')
    hari_ini_indonesia = hari[hari_ini_inggris]
    jadwalHariIni = Jadwal.objects.filter(hari=hari_ini_inggris)
    return render(request, 'kunjungan/jadwal.html', {
        'jadwal': jadwal,
        'jadwalHariIni': jadwalHariIni,
        'hari_ini': hari_ini_indonesia,
    })

def download_qr_buku(request, id):
    buku = JenisBuku.objects.get(id=id)
    qr_content = (
        f"{settings.QR_BOOK_SECRET}|"
        f"{buku.isbn_issn}"
    )
    qr = qrcode.QRCode(
        version=1,
        box_size=10,
        border=5
    )
    qr.add_data(qr_content)
    qr.make(fit=True)
    img = qr.make_image(
        fill_color="black",
        back_color="white"
    )
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    filename = (
        f"{buku.judul}-{buku.isbn_issn}.png"
    )
    filename = re.sub(
        r'[^a-zA-Z0-9._-]',
        '_',
        filename
    )
    response = HttpResponse(
        buffer.getvalue(),
        content_type='image/png'
    )
    response[
        'Content-Disposition'
    ] = f'attachment; filename="{filename}"'
    return response

def download_all_qr(request):
    memory_file = BytesIO()
    with zipfile.ZipFile(memory_file, 'w') as zf:
        books = JenisBuku.objects.all()
        for book in books:
            isbn = str(book.isbn_issn).strip()
            if not isbn or isbn == 'nan':
                continue
            
            qr_content = (
                f"{settings.QR_BOOK_SECRET}|"
                f"{isbn}"
            )
            
            qr = qrcode.QRCode(
                version=1,
                box_size=10,
                border=5
            )
            qr.add_data(qr_content)
            qr.make(fit=True)
            qr_img = qr.make_image(
                fill_color="black",
                back_color="white"
            )
            qr_img = qr_img.convert("RGB")
            judul = book.judul
            text = f"{judul}\n{isbn}"
            width = qr_img.size[0]
            height = qr_img.size[1] + 80
            canvas = Image.new(
                "RGB",
                (width, height),
                "white"
            )
            canvas.paste(qr_img, (0, 0))
            draw = ImageDraw.Draw(canvas)
            font = ImageFont.load_default()
            draw.text(
                (10, qr_img.size[1] + 10),
                text,
                fill="black",
                font=font
            )
            
            qr_bytes = BytesIO()
            canvas.save(qr_bytes, format='PNG')
            judul_slug = slugify(book.judul)
            filename = f"{judul_slug}-{isbn}.png"
            zf.writestr(
                filename,
                qr_bytes.getvalue()
            )
    
    memory_file.seek(0)
    response = HttpResponse(
        memory_file,
        content_type='application/zip'
    )
    response['Content-Disposition'] = (
        'attachment; filename="semua_qr_buku.zip"'
    )
    return response

def show_scan_buku(request):
    return render(request,'buku/scanner.html')

@login_required
def scanner_buku(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Method tidak diizinkan'})
    
    try:
        data = json.loads(request.body)
        raw_data = data.get('qr_code', '').strip()
        isbn_match = re.search(r'\|([0-9Xx-]+)$', raw_data)
        isbn = isbn_match.group(1) if isbn_match else re.sub(r'^[a-zA-Z_]+\d+\|', '', raw_data)
        if not isbn:
            return JsonResponse({'success': False, 'message': 'ISBN tidak valid'})
        with transaction.atomic():
            jenis_buku = JenisBuku.objects.filter(isbn_issn__iexact=isbn).first()
            if not jenis_buku:
                return JsonResponse({'success': False, 'message': f'Buku dengan ISBN {isbn} tidak ditemukan'})
            pengunjung = Pengunjung.objects.select_for_update().get(user=request.user)
            
            peminjaman_aktif = Peminjaman.objects.filter(
                peminjam=pengunjung,
                status='DIPINJAM'
            )
            peminjaman_buku_ini = peminjaman_aktif.filter(
                buku__jenis_buku=jenis_buku
            ).first()
            
            if peminjaman_buku_ini:
                waktu_kembali = timezone.now()

                peminjaman_buku_ini.status = 'SELESAI'
                peminjaman_buku_ini.keluar = waktu_kembali
                peminjaman_buku_ini.save()

                buku = peminjaman_buku_ini.buku
                buku.status = 'TERSEDIA'
                buku.save()

                if waktu_kembali > peminjaman_buku_ini.batas_pengembalian:
                    status_pengembalian = "TERLAMBAT"
                    terlambat = (waktu_kembali - peminjaman_buku_ini.batas_pengembalian).days
                    denda = terlambat * 1000
                else:
                    status_pengembalian = "TEPAT_WAKTU"
                    denda = 0

                Pengembalian.objects.create(
                    peminjaman=peminjaman_buku_ini,
                    tanggal_pengembalian=waktu_kembali,
                    status=status_pengembalian,
                    denda=denda
                )

                message = f'Berhasil mengembalikan {jenis_buku.judul}'
                if status_pengembalian == "TERLAMBAT":
                    message += f' (Terlambat {terlambat} hari, denda Rp{denda:,})'

                return JsonResponse({
                    'success': True,
                    'message': message
                })
            
            buku = Buku.objects.select_for_update().filter(
                jenis_buku=jenis_buku,
                status='TERSEDIA'
            ).first()
            
            if not buku:
                return JsonResponse({
                    'success': False,
                    'message': f'Stok buku "{jenis_buku.judul}" sedang habis'
                })
            
            Peminjaman.objects.create(
                peminjam=pengunjung,
                buku=buku,
                batas_pengembalian=timezone.now() + timedelta(days=14),
                status='DIPINJAM'
            )
            buku.status = 'DIPINJAM'
            buku.save()
            
            return JsonResponse({
                'success': True,
                'message': f'Berhasil meminjam {jenis_buku.judul}'
            })
    
    except Pengunjung.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Data pengunjung tidak ditemukan'})
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Format data tidak valid'})
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Scanner error: {str(e)}", exc_info=True)
        return JsonResponse({'success': False, 'message': 'Terjadi kesalahan sistem'})

def about_me(request):
    return render(request,'about.html');
