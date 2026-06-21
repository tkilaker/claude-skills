---
name: unifi-network
description: Inspect and manage Tim's UniFi home network, Dream Router 7, clients, static DHCP reservations, and Uptime Kuma monitoring. Use when asked about UniFi, the router, home network clients, static IPs, DHCP reservations, LAN reachability, Wi-Fi vs wired paths, or watcher/Kuma monitor configuration.
---

# UniFi Network

Use this skill for Tim's home UniFi network.

## Source Of Truth

- Router/controller: `https://192.168.1.1` (Dream Router 7 / UDR7)
- UniFi Site Manager API: `https://api.ui.com/v1`
- Network connector base: `https://api.ui.com/v1/connector/consoles/{hostId}/proxy/network`
- Default site: `default`
- Uptime Kuma: `http://192.168.1.169:3001`

## Secrets

Never write API keys into repo files, command output, docs, or chat.

Read the UniFi key in this order:

1. `UNIFI_API_KEY`
2. macOS Keychain service `unifi-network-api-key`
3. `$HOME/.config/unifi/network-api-key` with mode `0600`

Read the Kuma password in this order:

1. `UPTIME_KUMA_PASSWORD`
2. macOS Keychain service `uptime-kuma`
3. `$HOME/.config/uptime-kuma/password` with mode `0600`

## Quick Commands

```bash
python3 ~/.agents/skills/unifi-network/scripts/unifi_network.py info
python3 ~/.agents/skills/unifi-network/scripts/unifi_network.py inventory
python3 ~/.agents/skills/unifi-network/scripts/unifi_network.py reservation-plan --stable-only
python3 ~/.agents/skills/unifi-network/scripts/unifi_network.py apply-reservations scratch/unifi-reservations.json --dry-run
uv run --with uptime-kuma-api python ~/.agents/skills/unifi-network/scripts/kuma_sync.py --dry-run
```

## Workflow

1. Start with `info` and `inventory`; do not assume current IPs from notes.
2. For static IP work, generate a reservation plan first.
3. Exclude sleeping/mobile/private-random clients unless the user explicitly asks to reserve them.
4. Apply reservations only from a saved plan and keep the script output as evidence.
5. For Kuma, monitor always-on infrastructure only. Do not ping phones, watches, tablets, or laptops unless there is a specific reason.

## Static IP Policy

Prefer DHCP reservations at the current known IP when:

- the device is infrastructure or always-on,
- the MAC is stable,
- the device has a clear name,
- the current IP is inside `192.168.1.0/24`,
- no other reservation already owns that IP.

Always-on candidates usually include router, NAS, Mini, switches, APs, cameras, Hue Bridge, Home Assistant, Plex/NAS services, Apple TVs, and printers.

## References

Read `references/unifi-api.md` when API paths, key types, or connector mode matter.
