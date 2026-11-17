# Spesifikasi Kalkulator Subnet & VLSM

## 1. Tujuan
Membuat aplikasi Kalkulator Subnet dan VLSM berbasis web untuk membantu pengguna menghitung pembagian jaringan IPv4.

## 2. Aturan Validasi
- IP Address harus memiliki empat oktet.
- Setiap oktet bernilai 0 sampai 255.
- IP tidak boleh menggunakan angka nol di depan.
- Prefix berupa bilangan bulat 0 sampai 32.
- Input tidak valid menghasilkan kesalahan.
- VLSM menggunakan alamat network yang valid.
- Kebutuhan host minimal 1.

## 3. Kontrak Fungsi

### hitung_subnet(ip, prefix)
Menghasilkan `mask`, `network`, `broadcast`, `first_host`, `last_host`, dan `usable_hosts`.
- Prefix /0 sampai /30: jumlah host = 2^(32-prefix)-2.
- Prefix /31: dua alamat untuk point-to-point.
- Prefix /32: satu alamat.

### alokasi_vlsm(network_cidr, kebutuhan_host)
Mengurutkan kebutuhan host dari terbesar, lalu mengalokasikan blok terkecil yang mampu menampung kebutuhan host dan dua alamat tambahan, dengan ukuran minimal /30.

## 4. Kontrak API
- `GET /api/subnet?ip=&prefix=`
- `POST /api/vlsm` dengan JSON `{"network":"192.168.1.0/24","kebutuhan_host":[100,50,20,2]}`
- `GET /` untuk halaman web.
- Kesalahan input menghasilkan HTTP 400 dengan field `detail`.

## 5. Halaman Web
Satu halaman responsif dengan dua mode: Subnet dan VLSM. Halaman menampilkan hasil perhitungan dan pesan kesalahan.

## 6. Test Case
- 172.16.5.130/25 menghasilkan network 172.16.5.128, broadcast 172.16.5.255, dan 126 host.
- 10.0.0.0/30 menghasilkan dua host.
- 192.168.1.0/31 mengikuti aturan point-to-point.
- 192.168.1.5/32 menghasilkan satu host.
- IP dan prefix tidak valid ditolak.
- VLSM 192.168.1.0/24 untuk 100, 50, 20, 2 host menghasilkan /25, /26, /27, /30.
- VLSM 200 dan 100 host pada /24 ditolak karena tidak cukup.

## 7. Di Luar Cakupan
- IPv6.
- Routing jaringan.
- Konfigurasi perangkat jaringan.
- Simulasi jaringan.
