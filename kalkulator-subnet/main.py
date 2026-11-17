from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
import ipaddress
import json
import re

app = FastAPI(
    title="Kalkulator Subnet & VLSM",
    description="API perhitungan subnet IPv4 dan VLSM",
    version="1.0.0",
)


def bersihkan_html(html: str) -> str:
    """Hapus teks asing ``ji`` yang tersisip tepat setelah tag <head>."""
    return re.sub(r"(<head>\s*)ji(?=\s*<)", r"\1", html, count=1, flags=re.IGNORECASE)


def hitung_subnet(ip: str, prefix: int) -> dict:
    """Menghitung informasi subnet IPv4."""
    if not isinstance(ip, str):
        raise ValueError("IP Address harus berupa teks")

    try:
        alamat = ipaddress.IPv4Address(ip)
    except ipaddress.AddressValueError:
        raise ValueError("Format IP Address tidak valid")

    if not isinstance(prefix, int) or isinstance(prefix, bool):
        raise ValueError("Prefix harus berupa bilangan bulat")
    if not 0 <= prefix <= 32:
        raise ValueError("Prefix harus antara 0 sampai 32")

    network = ipaddress.IPv4Network(f"{alamat}/{prefix}", strict=False)
    network_address = network.network_address
    broadcast_address = network.broadcast_address

    if prefix == 31:
        first_host = network_address
        last_host = broadcast_address
        broadcast = None
        usable_hosts = 2
    elif prefix == 32:
        first_host = alamat
        last_host = alamat
        broadcast = None
        usable_hosts = 1
    else:
        first_host = network_address + 1
        last_host = broadcast_address - 1
        broadcast = str(broadcast_address)
        usable_hosts = (2 ** (32 - prefix)) - 2

    return {
        "mask": str(network.netmask),
        "network": str(network_address),
        "broadcast": broadcast,
        "first_host": str(first_host),
        "last_host": str(last_host),
        "usable_hosts": usable_hosts,
    }


def alokasi_vlsm(network_cidr: str, kebutuhan_host: list[int]) -> list[dict]:
    """Mengalokasikan subnet VLSM dari kebutuhan host terbesar."""
    try:
        network = ipaddress.IPv4Network(network_cidr, strict=True)
    except (ValueError, ipaddress.AddressValueError):
        raise ValueError("Network CIDR tidak valid atau bukan alamat network")

    if not isinstance(kebutuhan_host, list) or not kebutuhan_host:
        raise ValueError("Daftar kebutuhan host tidak boleh kosong")

    for jumlah in kebutuhan_host:
        if (
            not isinstance(jumlah, int)
            or isinstance(jumlah, bool)
            or jumlah < 1
        ):
            raise ValueError("Kebutuhan host harus bilangan bulat minimal 1")

    hasil = []
    cursor = int(network.network_address)
    batas_akhir = int(network.broadcast_address)

    for kebutuhan in sorted(kebutuhan_host, reverse=True):
        # Minimal blok 4 alamat (/30); kebutuhan host ditambah 2 alamat.
        ukuran_blok = max(4, 1 << (kebutuhan + 1).bit_length())
        if ukuran_blok > 2**32:
            raise ValueError("Kebutuhan host terlalu besar")

        prefix = 32 - (ukuran_blok.bit_length() - 1)
        cursor = ((cursor + ukuran_blok - 1) // ukuran_blok) * ukuran_blok
        alamat_akhir = cursor + ukuran_blok - 1

        if alamat_akhir > batas_akhir:
            raise ValueError(
                "Blok jaringan tidak cukup untuk seluruh kebutuhan host"
            )

        subnet = ipaddress.IPv4Network((cursor, prefix))
        detail = hitung_subnet(str(subnet.network_address), prefix)

        hasil.append({
            "kebutuhan": kebutuhan,
            "network_cidr": str(subnet),
            **detail,
        })
        cursor = alamat_akhir + 1

    return hasil


@app.get("/", response_class=HTMLResponse)
def halaman_utama():
    try:
        with open("index.html", "r", encoding="utf-8") as file:
            return bersihkan_html(file.read())
    except FileNotFoundError:
        return bersihkan_html("""
        <h1>Kalkulator Subnet & VLSM</h1>
        <p>API berhasil dijalankan.</p>
        <a href="/docs">Buka Dokumentasi API</a>
        """)


@app.get("/health", include_in_schema=False)
def health_check():
    return {"status": "ok"}


@app.get("/api/subnet")
def api_subnet(ip: str, prefix: str):
    try:
        if not prefix.isdigit():
            raise ValueError("Prefix harus berupa angka")
        return hitung_subnet(ip, int(prefix))
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))


@app.post("/api/vlsm")
async def api_vlsm(request: Request):
    try:
        data = await request.json()
        if not isinstance(data, dict):
            raise ValueError("Format JSON harus berupa objek")

        network = data.get("network")
        kebutuhan_host = data.get("kebutuhan_host")

        if not isinstance(network, str):
            raise ValueError("Network harus berupa teks CIDR")
        if not isinstance(kebutuhan_host, list):
            raise ValueError("Kebutuhan host harus berupa daftar")

        return alokasi_vlsm(network, kebutuhan_host)

    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Format JSON tidak valid")
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
