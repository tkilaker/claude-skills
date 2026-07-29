#!/usr/bin/env python3
"""Sync selected always-on UniFi devices into Uptime Kuma."""

from __future__ import annotations

import argparse
import os
import subprocess
from dataclasses import dataclass
from pathlib import Path

from uptime_kuma_api import MonitorType, UptimeKumaApi

import unifi_network


KUMA_URL = "http://192.168.1.169:3001"


@dataclass(frozen=True)
class PingMonitor:
    name: str
    host: str


def kuma_password() -> str:
    if os.environ.get("UPTIME_KUMA_PASSWORD"):
        return os.environ["UPTIME_KUMA_PASSWORD"].strip()

    secret = unifi_network.read_agent_secret("UPTIME_KUMA_PASSWORD")
    if secret:
        return secret

    try:
        out = subprocess.check_output(
            ["security", "find-generic-password", "-s", "uptime-kuma", "-w"],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
        if out:
            return out
    except Exception:
        pass

    secret_file = Path.home() / ".config" / "uptime-kuma" / "password"
    if secret_file.exists():
        return secret_file.read_text(encoding="utf-8").strip()

    raise SystemExit("Missing Uptime Kuma password. Store UPTIME_KUMA_PASSWORD in Agent Secrets.")


def desired_monitors() -> list[PingMonitor]:
    key = unifi_network.read_secret()
    plan = unifi_network.reservation_plan(key, all_clients=False)
    monitors = [
        PingMonitor("Router", "192.168.1.1"),
    ]
    for item in plan:
        name = item["name"]
        ip = item["current_ip"]
        lower = name.lower()
        if lower == "nas":
            monitors.append(PingMonitor("NAS", ip))
        elif lower == "mini":
            monitors.append(PingMonitor("Mac Mini (LAN)", ip))
        elif any(term in lower for term in ("hue", "g5", "apple tv", "lgwebostv", "esp32", "nintendo")):
            monitors.append(PingMonitor(f"Device: {name}", ip))
    return monitors


def sync(dry_run: bool) -> None:
    api = UptimeKumaApi(KUMA_URL)
    api.login("tim", kuma_password())
    try:
        existing = {m["name"]: m for m in api.get_monitors()}
        for monitor in desired_monitors():
            current = existing.get(monitor.name)
            if current:
                current_host = current.get("hostname")
                if current.get("type") == MonitorType.PING and current_host == monitor.host:
                    print(f"ok {monitor.name} {monitor.host}")
                elif dry_run:
                    print(f"would update {monitor.name}: {current_host} -> {monitor.host}")
                else:
                    api.edit_monitor(current["id"], type=MonitorType.PING, hostname=monitor.host)
                    print(f"updated {monitor.name}: {current_host} -> {monitor.host}")
            elif dry_run:
                print(f"would create {monitor.name}: {monitor.host}")
            else:
                api.add_monitor(type=MonitorType.PING, name=monitor.name, hostname=monitor.host, interval=60, maxretries=3)
                print(f"created {monitor.name}: {monitor.host}")
    finally:
        api.disconnect()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    sync(dry_run=args.dry_run)


if __name__ == "__main__":
    main()
