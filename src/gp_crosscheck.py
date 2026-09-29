#!/usr/bin/env python3
"""Перекрёстная проверка Google Patents (в фоне): соединения REBCO + flux pump.

Проверяем:
  1. Tokamak Energy exfoliated ReBCO joint (есть в Lens)
  2. K-Joins resistance-free (есть в Lens)
  3. Sumitomo iGS (НЕТ в Lens — проверить GP!)
  4. Fujikura splice (НЕТ в Lens — проверить GP!)
  5. Flux pump Sichuan (есть в Lens)

Каналы: SOCKS-прокси (локальный) с ротацией circuit при 503/пустом ответе.
Результат: /tmp/gp_crosscheck_results.json
"""
import json
import socket
import subprocess
import sys
import time
import urllib.parse
import urllib.request

try:
    import socks
except ImportError:
    sys.exit("pip install pysocks")

VPS = "127.0.0.1"
TOR_SOCKS = 9051
TOR_CTRL = 9052
TOR_PASS = "ninja_tor_pass_2026"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml",
}

# Запросы для проверки
QUERIES = [
    ("Tokamak Energy ReBCO joint", "Tokamak Energy superconducting joint REBCO"),
    ("K-Joins splicing", "K Joins ReBCO persistent current splice"),
    ("Sumitomo iGS", "Sumitomo intermediate grown superconducting REBCO joint"),
    ("Fujikura splice", "Fujikura REBCO superconducting splice joint"),
    ("Sichuan flux pump", "Sichuan high temperature superconducting flux pump"),
]


def enable_tor():
    socks.set_default_proxy(socks.SOCKS5, VPS, TOR_SOCKS, rdns=True)
    socket.socket = socks.socksocket


def newnym():
    try:
        subprocess.run(
            ["ssh", "-o", "StrictHostKeyChecking=no", "-o", "ConnectTimeout=6",
             f"root@{VPS}",
             f"printf 'AUTHENTICATE \"{TOR_PASS}\"\\nSIGNAL NEWNYM\\n' | timeout 3 nc 127.0.0.1 {TOR_CTRL} >/dev/null 2>&1; echo done"],
            capture_output=True, timeout=12)
        time.sleep(4)
    except Exception:
        pass


def check_gp(query: str, retries: int = 6) -> dict:
    url = "https://patents.google.com/?q=" + urllib.parse.quote(query) + "&country=ALL&type=PATENT"
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=30) as r:
                body = r.read().decode("utf-8", errors="ignore")
            if len(body) < 3000:
                # пустая заглушка — смена circuit
                newnym()
                continue
            # Ищем номера патентов
            import re
            nums = re.findall(r'(?:US|WO|EP|CN|JP|KR)\d{6,}', body)
            found = list(set(nums))[:8]
            return {"status": "ok", "results": found, "bytes": len(body)}
        except Exception as e:
            newnym()
    return {"status": "fail", "results": [], "bytes": 0}


def main():
    enable_tor()
    results = {}
    for label, q in QUERIES:
        print(f"=== {label} ===")
        res = check_gp(q)
        results[label] = res
        print(f"  {res['status']}, {len(res['results'])} номеров: {res['results']}")
        time.sleep(2)

    with open("/tmp/gp_crosscheck_results.json", "w") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print("\nСохранено: /tmp/gp_crosscheck_results.json")


if __name__ == "__main__":
    main()
