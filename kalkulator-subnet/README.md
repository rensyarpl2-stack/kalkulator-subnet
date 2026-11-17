# Kalkulator Subnet & VLSM

Aplikasi web untuk menghitung subnet IPv4 dan pembagian jaringan menggunakan VLSM.

## Fitur
- Kalkulator subnet IPv4 dengan visualisasi prefix dan rentang host.
- Alokasi VLSM untuk beberapa kebutuhan host sekaligus.
- Unduh hasil alokasi VLSM sebagai CSV.
- Tema terang/gelap yang tersimpan di browser.
- Riwayat lima perhitungan subnet terakhir, tersimpan lokal dan bisa dihapus.

## Teknologi
- Python 3.12
- FastAPI
- HTML, CSS, JavaScript
- Pytest

## Instalasi
```bash
uv sync --dev
```

## Menjalankan aplikasi
```bash
uv run fastapi dev main.py
```

Buka http://127.0.0.1:8000

Dokumentasi API: http://127.0.0.1:8000/docs

## Menjalankan dengan Docker
Pastikan Docker Desktop sudah terpasang dan berjalan. Dari folder proyek, jalankan:

```powershell
docker compose up --build -d
```

Di komputer yang menjalankan Docker, aplikasi tersedia di http://localhost:8000.
Container berjalan sebagai pengguna non-root, menggunakan filesystem read-only,
dibangun dengan multi-stage image, memiliki batas resource dan rotasi log,
serta menyediakan pemeriksaan kesehatan di `/health`.

### Membuka dari komputer lain di jaringan yang sama
1. Pastikan kedua komputer terhubung ke jaringan lokal yang sama.
2. Di komputer server, jalankan `ipconfig` dan catat alamat **IPv4 Address** adaptor Wi-Fi/Ethernet yang aktif (misalnya `192.168.1.25`).
3. Jika Windows Firewall meminta izin, izinkan Docker pada jaringan **Private**. Jika perlu, buka PowerShell sebagai Administrator lalu jalankan:

   ```powershell
   New-NetFirewallRule -DisplayName "Kalkulator Subnet Docker" -Direction Inbound -Protocol TCP -LocalPort 8000 -Action Allow -Profile Private
   ```

4. Dari komputer lain, buka `http://ALAMAT-IP-SERVER:8000`, misalnya `http://192.168.1.25:8000`.

Untuk memakai port lain, jalankan Compose dengan port pilihan, misalnya:

```powershell
$env:APP_PORT = "8080"
docker compose up --build -d
```

Kemudian akses `http://ALAMAT-IP-SERVER:8080`. Untuk menghentikan aplikasi:

```powershell
docker compose down
```

Panduan ini untuk jaringan lokal tepercaya. Jangan meneruskan port tersebut langsung ke internet melalui router tanpa menambahkan HTTPS dan kontrol akses.

## Menjalankan pengujian
```bash
uv run pytest test_main.py -v
```

## Pengujian dengan coverage
```bash
uv run pytest test_main.py -v --cov=main --cov-report=term-missing
```

## Endpoint
- GET `/api/subnet`
- POST `/api/vlsm`
- GET `/`
- GET `/health` (pemeriksaan kesehatan container)
