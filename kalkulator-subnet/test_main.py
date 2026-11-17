import pytest
from fastapi.testclient import TestClient
from main import app, hitung_subnet, alokasi_vlsm, bersihkan_html

client = TestClient(app)


@pytest.mark.parametrize(
    "ip,prefix,network,broadcast,hosts",
    [
        ("172.16.5.130", 25, "172.16.5.128", "172.16.5.255", 126),
        ("10.0.0.0", 30, "10.0.0.0", "10.0.0.3", 2),
        ("192.168.1.0", 31, "192.168.1.0", None, 2),
        ("192.168.1.5", 32, "192.168.1.5", None, 1),
    ],
)
def test_hitung_subnet(ip, prefix, network, broadcast, hosts):
    hasil = hitung_subnet(ip, prefix)
    assert hasil["network"] == network
    assert hasil["broadcast"] == broadcast
    assert hasil["usable_hosts"] == hosts


@pytest.mark.parametrize(
    "ip,prefix",
    [
        ("256.1.1.1", 24),
        ("192.168.01.1", 24),
        ("192.168.1", 24),
        ("abc", 24),
        ("", 24),
        ("192.168.1.1", 33),
        ("192.168.1.1", -1),
    ],
)
def test_subnet_invalid(ip, prefix):
    with pytest.raises(ValueError):
        hitung_subnet(ip, prefix)


def test_api_subnet_sukses():
    response = client.get("/api/subnet?ip=172.16.5.130&prefix=25")
    assert response.status_code == 200
    assert response.json()["network"] == "172.16.5.128"


def test_api_subnet_invalid():
    response = client.get("/api/subnet?ip=256.1.1.1&prefix=24")
    assert response.status_code == 400


def test_halaman_utama():
    response = client.get("/")
    assert response.status_code == 200
    assert "Kalkulator Subnet" in response.text
    assert "<head>ji" not in response.text


def test_bersihkan_html_hapus_ji():
    html = "<html><head>ji\n  <meta charset='UTF-8'>"
    assert bersihkan_html(html) == "<html><head>\n  <meta charset='UTF-8'>"


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_vlsm_sukses():
    hasil = alokasi_vlsm("192.168.1.0/24", [100, 50, 20, 2])
    network = [item["network_cidr"] for item in hasil]
    assert network == [
        "192.168.1.0/25",
        "192.168.1.128/26",
        "192.168.1.192/27",
        "192.168.1.224/30",
    ]


def test_vlsm_jaringan_tidak_cukup():
    with pytest.raises(ValueError):
        alokasi_vlsm("192.168.1.0/24", [200, 100])


@pytest.mark.parametrize(
    "network,host",
    [
        ("192.168.1.1/24", [10]),
        ("192.168.1.0/24", []),
        ("192.168.1.0/24", [0]),
        ("192.168.1.0/24", [-1]),
    ],
)
def test_vlsm_invalid(network, host):
    with pytest.raises(ValueError):
        alokasi_vlsm(network, host)


def test_api_vlsm():
    response = client.post(
        "/api/vlsm",
        json={"network": "192.168.1.0/24", "kebutuhan_host": [100, 50, 20, 2]},
    )
    assert response.status_code == 200
    assert len(response.json()) == 4


def test_api_vlsm_invalid():
    response = client.post(
        "/api/vlsm",
        json={"network": "192.168.1.0/24", "kebutuhan_host": [200, 100]},
    )
    assert response.status_code == 400
