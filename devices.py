from pythonping import ping
import socket
import ipaddress
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict
import subprocess
import re

try:
    # scapy is optional; melhora descoberta via ARP quando disponível
    from scapy.all import arping  # type: ignore
except Exception:
    arping = None


def checar_dispositivo(ip: str, timeout: float = 1.0) -> Dict:
    """Retorna informações do IP: host, latência (ms) e online(bool)."""
    try:
        host = socket.gethostbyaddr(ip)[0]
    except Exception:
        host = "Desconhecido"

    try:
        response = ping(ip, count=1, timeout=timeout)
        latencia = getattr(response, "rtt_avg_ms", None)
        # Tratar timeouts como offline: se latência for None ou >= timeout*1000, considerar offline
        if latencia is None:
            online = False
        else:
            # pythonping retorna ms; se >= timeout (s) * 1000 => provavelmente timeout
            online = (latencia < (timeout * 1000))
            if not online:
                latencia = None
    except Exception:
        latencia = None
        online = False

    return {"ip": ip, "host": host, "latencia": latencia, "online": online}


def scan_network(cidr: str, max_workers: int = 100, timeout: float = 1.0) -> List[Dict]:
    """Faz um ping-sweep do CIDR informado e retorna lista de dispositivos.

    Exemplo: scan_network('192.168.0.0/24')
    """
    net = ipaddress.ip_network(cidr, strict=False)
    hosts = [str(h) for h in net.hosts()]

    results: List[Dict] = []
    with ThreadPoolExecutor(max_workers=min(max_workers, len(hosts))) as ex:
        futures = {ex.submit(checar_dispositivo, ip, timeout): ip for ip in hosts}
        for fut in as_completed(futures):
            try:
                res = fut.result()
                results.append(res)
            except Exception:
                # em caso de erro isolado, adiciona como offline
                ip = futures[fut]
                results.append({"ip": ip, "host": "Desconhecido", "latencia": None, "online": False})

    # Ordena por IP para estabilidade
    results.sort(key=lambda d: ipaddress.ip_address(d["ip"]))
    return results


def _parse_arp_table() -> List[str]:
    """Lê a tabela ARP do sistema e retorna lista de IPs conhecidos (fallback)."""
    try:
        proc = subprocess.run(["arp", "-a"], capture_output=True, text=True, timeout=5)
        out = proc.stdout
    except Exception:
        return []

    ips = re.findall(r"(\d+\.\d+\.\d+\.\d+)", out)
    # remove endereços de broadcast/duplicados
    unique = []
    for ip in ips:
        if ip not in unique:
            unique.append(ip)
    return unique


def arp_scan(cidr: str) -> List[str]:
    """Tenta descobrir hosts ativos na LAN via ARP.

    Primeiro tenta usar scapy. Se não disponível ou falhar, usa `arp -a`.
    Retorna lista de IPs ativos.
    """
    # preferir scapy arping (envia requisições ARP diretamente)
    if arping is not None:
        try:
            answered, _ = arping(cidr, timeout=2, verbose=False)
            ips = []
            for snd, rcv in answered:
                ip = rcv.psrc if hasattr(rcv, "psrc") else None
                if ip:
                    ips.append(ip)
            return sorted(list(set(ips)), key=lambda s: ipaddress.ip_address(s))
        except Exception:
            pass

    # fallback: ler tabela ARP do SO
    return _parse_arp_table()


def scan_active_hosts(cidr: str, max_workers: int = 100, timeout: float = 1.0) -> List[Dict]:
    """Varre a rede e retorna apenas os hosts ativos (detectados por ARP), com latência via ping."""
    ips = arp_scan(cidr)
    results: List[Dict] = []
    if not ips:
        return results

    with ThreadPoolExecutor(max_workers=min(max_workers, len(ips))) as ex:
        futures = {ex.submit(checar_dispositivo, ip, timeout): ip for ip in ips}
        for fut in as_completed(futures):
            try:
                res = fut.result()
                results.append(res)
            except Exception:
                ip = futures[fut]
                results.append({"ip": ip, "host": "Desconhecido", "latencia": None, "online": False})

    results.sort(key=lambda d: ipaddress.ip_address(d["ip"]))
    return results
