from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .android.resources import export_android_resources
from .ios.exporter import export_ktheme
from .server import run_server


def _load_theme(path: str | Path) -> dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="makeetheme")
    sub = parser.add_subparsers(dest="command", required=True)

    ios = sub.add_parser("ios", help="Generate an iOS .ktheme file")
    ios.add_argument("theme_json", help="Path to theme JSON")
    ios.add_argument("--out", required=True, help="Output .ktheme path")

    android = sub.add_parser("android-res", help="Generate Android resource zip")
    android.add_argument("theme_json", help="Path to theme JSON")
    android.add_argument("--out", required=True, help="Output zip path")

    serve = sub.add_parser("serve", help="Run the no-build web app")
    serve.add_argument("--host", default="127.0.0.1")
    serve.add_argument("--port", type=int, default=8000)

    args = parser.parse_args(argv)
    if args.command == "ios":
        export_ktheme(args.out, _load_theme(args.theme_json))
        print(args.out)
        return 0
    if args.command == "android-res":
        export_android_resources(args.out, _load_theme(args.theme_json))
        print(args.out)
        return 0
    if args.command == "serve":
        run_server(host=args.host, port=args.port)
        return 0
    parser.error("unknown command")
    return 2
