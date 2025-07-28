# Odoo Development Environment

## Deskripsi

Repositori ini berisi lingkungan pengembangan untuk Odoo beserta dependensi terkait seperti PostgreSQL, Python, dan berbagai tools pendukung. Struktur direktori telah diatur untuk memudahkan proses instalasi, pengembangan, dan pemeliharaan aplikasi Odoo.

## Struktur Direktori

- `developments/` : Modul dan custom development Odoo.
- `PostgreSQL/`   : Database server PostgreSQL dan tools terkait.
- `python/`       : Instalasi dan paket Python yang digunakan.
- `server/`       : Source code utama Odoo.
- `sessions/`     : Data sesi aplikasi.
- `thirdparty/`   : Dependensi pihak ketiga.
- `vcredist/`     : Redistributable Visual C++.

## Instalasi

1. **Clone repositori**
   ```sh
   git clone https://github.com/aalfatah/ShippingAgency-OdooDev.git
   cd odoo-dev
   ```

2. **Instalasi Python**
   - Pastikan Python versi 3.x sudah terinstal.
   - Install dependencies dengan:
     ```sh
     pip install -r requirements.txt
     ```

3. **Instalasi PostgreSQL**
   - Ikuti petunjuk pada [PostgreSQL/pgAdmin 4/README.txt](PostgreSQL/pgAdmin%204/README.txt) untuk setup database.

4. **Konfigurasi Odoo**
   - Copy file konfigurasi contoh:
     ```sh
     cp server/odoo.conf.example server/odoo.conf
     ```
   - Edit `server/odoo.conf` sesuai kebutuhan.

## Menjalankan Aplikasi

```sh
python server/odoo-bin -c server/odoo.conf
```
  - Rename `python` menjadi `pyodoo16` yang tersedia di folder `python/`.

1.  **Update Modul via Terminal**
- Perbarui modul tertentu *(misal: nama_modul)* dengan menjalankan perintah berikut : 
    ```sh
    python server/odoo-bin -c server/odoo.conf -u nama_modul
    ```
    Opsi `-u` (atau `--update`) digunakan untuk meng-update modul yang disebutkan.

3. **Update Modul via UI**
   - Masuk ke odoo dengan akun admin
   - Buka menu **Apps**
   - Cari modul yang ingin di-update
   - Klik **Update** atau **Upgrade** pada modul tersebut

## Tips

- Untuk development, aktifkan mode developer di Odoo UI agar menu update modul muncul `/web?debug=1`.
- Jika ada error, cek log Odoo di terminal untuk troubleshooting.

## Kontribusi

Silakan baca [server/CONTRIBUTING.md](server/CONTRIBUTING.md) untuk panduan kontribusi.

## Lisensi

Lihat file lisensi di:
- [PostgreSQL/server_license.txt](PostgreSQL/server_license.txt)
- [PostgreSQL/pgAdmin_license.txt](PostgreSQL/pgAdmin_license.txt)

## Dokumentasi

- Dokumentasi Odoo: [https://www.odoo.com/documentation](https://www.odoo.com/documentation)
- Dokumentasi PostgreSQL: [https://www.postgresql.org/docs/](https://www.postgresql.org/docs/)
