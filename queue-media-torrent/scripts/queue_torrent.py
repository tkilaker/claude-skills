#!/usr/bin/env python3
"""Validate and atomically expose a .torrent file to a qBittorrent watch folder."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import tempfile


CONFIG_PATH = Path.home() / ".config" / "queue-media-torrent" / "config.json"
INCOMPLETE_SUFFIXES = {".crdownload", ".download", ".part"}
MAX_TORRENT_SIZE = 100 * 1024 * 1024


class BencodeError(ValueError):
    pass


def parse_bencode(data: bytes, index: int = 0) -> tuple[object, int]:
    if index >= len(data):
        raise BencodeError("unexpected end of file")

    token = data[index : index + 1]
    if token == b"i":
        end = data.find(b"e", index + 1)
        if end == -1:
            raise BencodeError("unterminated integer")
        raw = data[index + 1 : end]
        if not raw or (raw.startswith(b"-") and len(raw) == 1):
            raise BencodeError("invalid integer")
        if raw.startswith(b"-0") or (raw.startswith(b"0") and len(raw) > 1):
            raise BencodeError("non-canonical integer")
        try:
            return int(raw), end + 1
        except ValueError as exc:
            raise BencodeError("invalid integer") from exc

    if token == b"l":
        result = []
        index += 1
        while index < len(data) and data[index : index + 1] != b"e":
            value, index = parse_bencode(data, index)
            result.append(value)
        if index >= len(data):
            raise BencodeError("unterminated list")
        return result, index + 1

    if token == b"d":
        result = {}
        index += 1
        while index < len(data) and data[index : index + 1] != b"e":
            key, index = parse_bencode(data, index)
            if not isinstance(key, bytes):
                raise BencodeError("dictionary key is not bytes")
            value, index = parse_bencode(data, index)
            result[key] = value
        if index >= len(data):
            raise BencodeError("unterminated dictionary")
        return result, index + 1

    if b"0" <= token <= b"9":
        colon = data.find(b":", index)
        if colon == -1:
            raise BencodeError("missing byte-string separator")
        try:
            length = int(data[index:colon])
        except ValueError as exc:
            raise BencodeError("invalid byte-string length") from exc
        start = colon + 1
        end = start + length
        if end > len(data):
            raise BencodeError("byte string exceeds file length")
        return data[start:end], end

    raise BencodeError(f"unexpected token at byte {index}")


def validate_torrent(source: Path) -> bytes:
    if source.suffix.lower() in INCOMPLETE_SUFFIXES:
        raise ValueError(f"incomplete download suffix: {source.suffix}")
    if source.suffix.lower() != ".torrent":
        raise ValueError("source must end in .torrent")
    if not source.is_file():
        raise ValueError(f"source is not a file: {source}")

    size = source.stat().st_size
    if size == 0 or size > MAX_TORRENT_SIZE:
        raise ValueError(f"unexpected torrent size: {size} bytes")

    data = source.read_bytes()
    decoded, end = parse_bencode(data)
    if end != len(data):
        raise BencodeError("trailing bytes after bencoded value")
    if not isinstance(decoded, dict) or b"info" not in decoded:
        raise BencodeError("top-level torrent dictionary has no info key")
    return data


def resolve_watch_dir(kind: str, explicit: Path | None) -> Path:
    if explicit is not None:
        return explicit.expanduser().resolve()
    if not CONFIG_PATH.is_file():
        raise ValueError(f"missing config: {CONFIG_PATH}")
    config = json.loads(CONFIG_PATH.read_text())
    value = config.get(kind)
    if not isinstance(value, str) or not value:
        raise ValueError(f"missing {kind!r} path in {CONFIG_PATH}")
    return Path(value).expanduser().resolve()


def queue(source: Path, watch_dir: Path, data: bytes) -> Path:
    if not watch_dir.is_dir():
        raise ValueError(f"watch directory does not exist: {watch_dir}")
    if not os.access(watch_dir, os.W_OK):
        raise ValueError(f"watch directory is not writable: {watch_dir}")

    final = watch_dir / source.name
    if final.exists():
        raise FileExistsError(f"refusing to overwrite: {final}")

    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{source.stem}.", suffix=".part", dir=watch_dir
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        shutil.copymode(source, temporary)
        os.replace(temporary, final)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise
    return final


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("--kind", required=True, choices=("tvshows", "movies"))
    parser.add_argument("--watch-dir", type=Path)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    source = args.source.expanduser().resolve()
    data = validate_torrent(source)
    watch_dir = resolve_watch_dir(args.kind, args.watch_dir)
    final = watch_dir / source.name

    if not args.apply:
        print(f"validated: {source}")
        print(f"would queue: {final}")
        return 0

    queued = queue(source, watch_dir, data)
    print(f"queued: {queued}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
