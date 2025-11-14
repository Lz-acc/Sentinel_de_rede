from flask import Flask, render_template, jsonify
import time
import threading
import socket
from devices import checar_dispositivo, scan_network

app = Flask(__name__)

# Configuração: rede a ser escaneada automaticamente (se None, será detectada)
SUBNET = None
# Intervalo entre scans em segundos
SCAN_INTERVAL = 30

# Cache de dispositivos e lock para acesso seguro entre threads
_devices_cache = []
_cache_lock = threading.Lock()


def _background_scanner():
    """Loop em background que atualiza `_devices_cache` periodicamente."""
    global _devices_cache
    while True:
        try:
            # Detectar SUBNET se não estiver definida
            subnet = SUBNET
            if subnet is None:
                subnet = detect_local_subnet()

            # Usar descoberta por ARP para retornar apenas hosts ativos
            try:
                from devices import scan_active_hosts
                results = scan_active_hosts(subnet, max_workers=120, timeout=1.0)
            except Exception:
                # fallback para varredura completa caso scan_active_hosts falhe
                results = scan_network(subnet, max_workers=120, timeout=1.0)
            # adiciona hora da checagem
            now = time.strftime("%H:%M:%S")
            for r in results:
                r["hora"] = now

            with _cache_lock:
                _devices_cache = results
        except Exception:
            # não crashar o scanner em caso de erro
            pass
        finally:
            time.sleep(SCAN_INTERVAL)


def start_scanner_once():
    """Inicia a thread do scanner caso não tenha sido iniciada."""
    if not hasattr(start_scanner_once, "started"):
        t = threading.Thread(target=_background_scanner, daemon=True)
        t.start()
        start_scanner_once.started = True


def detect_local_subnet() -> str:
    """Tenta detectar o IP local e assume uma /24 para o bloco.

    Usa uma conexão UDP para descobrir o IP local (não realiza tráfego externo real).
    Retorna uma string CIDR, ex: '192.168.1.0/24'.
    """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # destino arbitrário apenas para descobrir a interface e IP local
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
    except Exception:
        local_ip = "192.168.0.1"
    finally:
        try:
            s.close()
        except Exception:
            pass

    parts = local_ip.split('.')
    if len(parts) == 4:
        return f"{parts[0]}.{parts[1]}.{parts[2]}.0/24"
    return "192.168.0.0/24"


@app.route("/")
def index():
    start_scanner_once()
    return render_template("index.html")


@app.route("/status")
def status():
    # Retorna o cache atual (rápido). Front-end atualiza a cada 5s.
    with _cache_lock:
        snapshot = list(_devices_cache)
    return jsonify(snapshot)


if __name__ == "__main__":
    start_scanner_once()
    app.run(debug=True)
