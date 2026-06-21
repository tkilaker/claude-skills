#!/usr/bin/env python3
"""Small UniFi helper for Tim's Dream Router 7."""

from __future__ import annotations

import argparse
import ipaddress
import json
import os
import ssl
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any


LOCAL_BASE = "https://192.168.1.1/proxy/network/integration/v1"
SITE_MANAGER = "https://api.ui.com/v1"
DEFAULT_SITE = "default"


def read_secret() -> str:
    if os.environ.get("UNIFI_API_KEY"):
        return os.environ["UNIFI_API_KEY"].strip()

    if sys.platform == "darwin":
        try:
            out = subprocess.check_output(
                ["security", "find-generic-password", "-s", "unifi-network-api-key", "-w"],
                text=True,
                stderr=subprocess.DEVNULL,
            ).strip()
            if out:
                return out
        except Exception:
            pass

    secret_file = Path.home() / ".config" / "unifi" / "network-api-key"
    if secret_file.exists():
        return secret_file.read_text(encoding="utf-8").strip()

    raise SystemExit("Missing UniFi API key. Store it in Keychain or ~/.config/unifi/network-api-key.")


def request_json(url: str, key: str, method: str = "GET", body: dict[str, Any] | None = None) -> Any:
    data = None
    headers = {"X-API-KEY": key, "Accept": "application/json"}
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"

    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    context = ssl._create_unverified_context() if url.startswith("https://192.168.") else None
    try:
        with urllib.request.urlopen(req, timeout=25, context=context) as response:
            raw = response.read()
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", "replace")
        raise SystemExit(f"{method} {url} failed: HTTP {exc.code}: {detail}") from exc

    if not raw:
        return {}
    return json.loads(raw.decode("utf-8"))


def get_host_id(key: str) -> str:
    data = request_json(f"{SITE_MANAGER}/hosts", key)
    hosts = data.get("data", [])
    if not hosts:
        raise SystemExit("No UniFi hosts visible to this API key.")
    return hosts[0]["id"]


def connector_url(host_id: str, path: str) -> str:
    quoted = urllib.parse.quote(host_id, safe=":")
    return f"{SITE_MANAGER}/connector/consoles/{quoted}/proxy/network/{path.lstrip('/')}"


def network_get(key: str, path: str) -> Any:
    return request_json(connector_url(get_host_id(key), path), key)


def network_put(key: str, path: str, body: dict[str, Any]) -> Any:
    return request_json(connector_url(get_host_id(key), path), key, method="PUT", body=body)


def known_clients(key: str) -> list[dict[str, Any]]:
    data = network_get(key, f"api/s/{DEFAULT_SITE}/rest/user")
    return data.get("data", [])


def active_clients(key: str) -> list[dict[str, Any]]:
    data = network_get(key, f"api/s/{DEFAULT_SITE}/stat/sta")
    return data.get("data", [])


def site_manager_devices(key: str) -> list[dict[str, Any]]:
    data = request_json(f"{SITE_MANAGER}/devices", key)
    devices: list[dict[str, Any]] = []
    for host in data.get("data", []):
        devices.extend(host.get("devices", []))
    return devices


def display_name(client: dict[str, Any]) -> str:
    for field in ("name", "hostname", "display_name", "oui"):
        value = client.get(field)
        if value:
            return str(value)
    return ""


def normalize_mac(mac: str) -> str:
    mac = mac.replace("-", ":").replace(".", ":").lower()
    if ":" not in mac and len(mac) == 12:
        return ":".join(mac[i : i + 2] for i in range(0, 12, 2))
    return mac


def ip_ok(ip: str) -> bool:
    try:
        return ipaddress.ip_address(ip) in ipaddress.ip_network("192.168.1.0/24")
    except ValueError:
        return False


def stable_candidate(client: dict[str, Any], all_clients: bool) -> bool:
    if all_clients:
        return True
    name = display_name(client).lower()
    mac = normalize_mac(str(client.get("mac", "")))
    if not name:
        return False
    if any(word in name for word in ("iphone", "ipad", "watch", "macbook", "hms laptop")):
        return False
    if mac.startswith(("0a:", "1e:", "32:", "3e:", "46:", "52:", "72:", "92:", "a6:", "ae:", "ce:", "d6:", "e6:", "f2:", "fe:")):
        return False
    stable_terms = (
        "nas",
        "mini",
        "hue",
        "apple tv",
        "homepod",
        "printer",
        "brother",
        "lgwebostv",
        "g5",
        "camera",
        "esp32",
        "desktop",
        "imac",
        "nintendo",
    )
    return bool(client.get("is_wired") or any(term in name for term in stable_terms))


def reservation_plan(key: str, all_clients: bool) -> list[dict[str, Any]]:
    clients = known_clients(key)
    reserved_ips = {
        c.get("fixed_ip")
        for c in clients
        if c.get("use_fixedip") is True and c.get("fixed_ip")
    }
    plan: list[dict[str, Any]] = []
    for client in clients:
        ip = client.get("last_ip") or client.get("ip")
        if not ip or not ip_ok(str(ip)):
            continue
        if not stable_candidate(client, all_clients):
            continue
        fixed_ip = client.get("fixed_ip")
        already = client.get("use_fixedip") is True and fixed_ip == ip
        conflict = ip in reserved_ips and not already
        plan.append(
            {
                "id": client.get("_id"),
                "mac": normalize_mac(str(client.get("mac", ""))),
                "name": display_name(client),
                "current_ip": ip,
                "fixed_ip": fixed_ip or "",
                "use_fixedip": client.get("use_fixedip"),
                "already_correct": already,
                "conflict": conflict,
            }
        )
    return sorted(plan, key=lambda item: (item["conflict"], item["already_correct"], item["current_ip"]))


def print_inventory(key: str) -> None:
    rows = []
    for client in known_clients(key):
        ip = client.get("last_ip") or client.get("ip") or ""
        rows.append(
            (
                ip,
                normalize_mac(str(client.get("mac", ""))),
                display_name(client),
                str(client.get("is_wired")),
                str(client.get("use_fixedip")),
                str(client.get("fixed_ip") or ""),
            )
        )
    for row in sorted(rows):
        print("\t".join(row))


def apply_reservations(key: str, plan_path: Path, dry_run: bool) -> None:
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    clients = {c.get("_id"): c for c in known_clients(key)}
    for item in plan:
        if item.get("already_correct"):
            continue
        if item.get("conflict"):
            print(f"skip conflict {item['name']} {item['mac']} -> {item['current_ip']}")
            continue
        client = clients.get(item.get("id"))
        if not client:
            print(f"skip missing {item}")
            continue
        client["use_fixedip"] = True
        client["fixed_ip"] = item["current_ip"]
        label = f"{item['name'] or item['mac']} -> {item['current_ip']}"
        if dry_run:
            print(f"would reserve {label}")
        else:
            network_put(key, f"api/s/{DEFAULT_SITE}/rest/user/{item['id']}", client)
            print(f"reserved {label}")


def main() -> None:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("info")
    sub.add_parser("inventory")
    plan_parser = sub.add_parser("reservation-plan")
    group = plan_parser.add_mutually_exclusive_group()
    group.add_argument("--stable-only", action="store_true", default=True)
    group.add_argument("--all", action="store_true")
    plan_parser.add_argument("--output")
    apply_parser = sub.add_parser("apply-reservations")
    apply_parser.add_argument("plan")
    apply_parser.add_argument("--dry-run", action="store_true")

    args = parser.parse_args()
    key = read_secret()

    if args.cmd == "info":
        print(json.dumps(network_get(key, "integration/v1/info"), indent=2, sort_keys=True))
    elif args.cmd == "inventory":
        print_inventory(key)
    elif args.cmd == "reservation-plan":
        plan = reservation_plan(key, all_clients=args.all)
        text = json.dumps(plan, indent=2, sort_keys=True)
        if args.output:
            Path(args.output).write_text(text + "\n", encoding="utf-8")
            print(args.output)
        else:
            print(text)
    elif args.cmd == "apply-reservations":
        apply_reservations(key, Path(args.plan), dry_run=args.dry_run)


if __name__ == "__main__":
    main()
