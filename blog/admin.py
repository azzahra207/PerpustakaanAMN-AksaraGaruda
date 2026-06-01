from django.contrib import admin
from .models import *

admin.site.register(Pengunjung)
admin.site.register(PengunjungIstimewa)
admin.site.register(Petugas)
admin.site.register(Jadwal)
admin.site.register(Absensi)
admin.site.register(Kunjungan)

admin.site.register(Penulis)
admin.site.register(Jenis)
admin.site.register(JenisBuku)
admin.site.register(Buku)

admin.site.register(Peminjaman)
admin.site.register(Pengembalian)

class PostAdmin(admin.ModelAdmin):
    list_display = ('title','slug','status',)
    list_filter = ('status',)
    search_field = ('title','content',)

admin.site.register(Post, PostAdmin)
# Register your models here.
