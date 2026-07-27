---
name: queue-media-torrent
description: Safely queue an authorized .torrent file for Tim's NAS qBittorrent setup. Use when Tim asks to add, queue, or place a legal torrent for a TV show or movie in the NAS watch folders, or when selecting a compatible authorized media release for his Plex/Apple TV devices.
---

# Queue Media Torrent

Queue only material Tim owns, has permission to download, or that is freely and legally distributed.

## Known setup

- NAS shares mount over SMB at `/Volumes/tvshows` and `/Volumes/movies`.
- qBittorrent watches separate TV and movie directories on the NAS.
- Playback is Apple TV + Plex on 4K OLED displays.
- Prefer 2160p HEVC, HDR10 compatibility, and DDP/E-AC3 audio when several lawful releases are available.
- Do not invent preferences for release size, subtitles, remuxes, or languages. Ask only when the choice materially depends on one.

## Workflow

1. Confirm that the requested material is authorized. Do not search for or obtain unlicensed commercial films or TV shows.
2. Classify episodic content as `tvshows` and standalone films as `movies`. Ask if ambiguous.
3. If a signed-in website is needed for authorized content, use the user's existing browser session. Never request, print, save, or copy passwords, cookies, passkeys, or tracker credentials into the skill, Brain, shell history, or config.
4. Download the `.torrent` to a local staging directory such as `~/Downloads`. Never set a NAS watch directory as the browser's download destination.
5. Wait until the download is complete. A `.crdownload`, `.download`, `.part`, or changing file is incomplete.
6. Queue with `scripts/queue_torrent.py`. It validates the bencoded torrent and writes a non-`.torrent` temporary file inside the watch directory before an atomic rename exposes the final `.torrent` to qBittorrent.
7. Report the final watch path. Assume qBittorrent may consume or move the file immediately after the rename.

## Configure watch directories

The exact directories must be discovered from the live NAS and must not be guessed. Store them in:

`~/.config/queue-media-torrent/config.json`

```json
{
  "tvshows": "/Volumes/tvshows/<exact-watch-directory>",
  "movies": "/Volumes/movies/<exact-watch-directory>"
}
```

Do not store credentials in this file.

## Queue

Preview:

```bash
python3 scripts/queue_torrent.py /path/to/file.torrent --kind tvshows
```

Apply only when Tim asked to queue it:

```bash
python3 scripts/queue_torrent.py /path/to/file.torrent --kind tvshows --apply
```

Use `--watch-dir /exact/path` only for a verified one-off destination. Dry-run is the default.
