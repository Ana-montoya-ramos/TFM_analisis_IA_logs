import requests
import time
import random


# Dirección principal del servidor Apache2
base_url = "http://localhost/index.html"


# Payloads de ataques simulados
attack_payloads = {
    "SQL Injection": "?id=1' OR '1'='1",
    "Cross-site Scripting (XSS)": "?search=<script>alert('XSS')</script>",
    "Path Traversal": "?file=../../etc/passwd"
}


# URLs y paths normales para peticiones legítimas
normal_paths = [
    "",
    "?page=home",
    "?page=about",
    "?page=contact",
    "?search=ubuntu",
    "?search=security",
    "?id=123",
]


# Lista de IPs falsas
fake_ips = [
    "192.168.1.10",
    "10.0.0.5",
    "172.16.0.3",
    "203.0.113.9",
    "198.51.100.7"
]


# Lista de User-Agents variados
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) Gecko/20100101 Firefox/115.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/17A577 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 13; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Mobile Safari/537.36"
]


def simulate_traffic(iterations=20):
    for i in range(iterations):
        # Decide aleatoriamente si enviar ataque o petición normal 
        if random.random() < 0.4:
            # Ataque
            attack_type, payload = random.choice(list(attack_payloads.items()))
            url = base_url + payload
            event_type = "Attack"
        else:
            # Petición normal
            path = random.choice(normal_paths)
            url = base_url + path
            attack_type = None
            event_type = "Normal"


        # Cabeceras con IP y UA falsos
        fake_ip = random.choice(fake_ips)
        user_agent = random.choice(user_agents)
        headers = {
            "X-Forwarded-For": fake_ip,
            "User-Agent": user_agent
        }


        try:
            response = requests.get(url, headers=headers, timeout=5)
            status = response.status_code
        except Exception as e:
            status = f"Error: {e}"


        # Imprime información
        if event_type == "Attack":
            print(f"[{event_type}] {attack_type} | URL: {url} | IP: {fake_ip} | UA: {user_agent.split(' ')[0]} | Status: {status}")
        else:
            print(f"[{event_type}] URL: {url} | IP: {fake_ip} | UA: {user_agent.split(' ')[0]} | Status: {status}")


if __name__ == "__main__":
    simulate_traffic()
