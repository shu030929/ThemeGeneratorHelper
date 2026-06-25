from __future__ import annotations

import json
import mimetypes
import sys
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from .android.resources import build_android_resources_zip, default_android_resources_filename
from .ios.exporter import build_ktheme_bytes, default_ktheme_filename
from .models import DEFAULT_THEME, merge_theme

MAX_POST_BYTES = 24 * 1024 * 1024
ROOT = Path(__file__).resolve().parents[2]
WEB_DIR = ROOT / "web"


class ThemeBuilderHandler(SimpleHTTPRequestHandler):
    server_version = "MAKEETHEME/0.1"

    def translate_path(self, path: str) -> str:
        parsed = urlparse(path)
        clean_path = parsed.path
        if clean_path == "/":
            clean_path = "/index.html"
        return str((WEB_DIR / clean_path.lstrip("/")).resolve())

    def end_headers(self) -> None:
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "same-origin")
        super().end_headers()

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        if parsed.path == "/api/default-theme":
            self._send_json(DEFAULT_THEME)
            return
        static_path = Path(self.translate_path(self.path))
        try:
            static_path.relative_to(WEB_DIR.resolve())
        except ValueError:
            self.send_error(HTTPStatus.FORBIDDEN)
            return
        if not static_path.exists() or not static_path.is_file():
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        ctype = mimetypes.guess_type(static_path.name)[0] or "application/octet-stream"
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(static_path.stat().st_size))
        self.end_headers()
        with static_path.open("rb") as f:
            self.wfile.write(f.read())

    def do_POST(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        if parsed.path == "/api/export/ios":
            self._handle_ios_export()
            return
        if parsed.path == "/api/export/android-res":
            self._handle_android_export()
            return
        self.send_error(HTTPStatus.NOT_FOUND)

    def _read_json(self) -> dict:
        length = int(self.headers.get("Content-Length", "0"))
        if length <= 0:
            raise ValueError("Missing JSON request body")
        if length > MAX_POST_BYTES:
            raise ValueError("Request body is too large")
        raw = self.rfile.read(length)
        try:
            data = json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError as exc:
            raise ValueError("Invalid JSON request body") from exc
        if not isinstance(data, dict):
            raise ValueError("Request body must be a JSON object")
        return data

    def _handle_ios_export(self) -> None:
        try:
            payload = self._read_json()
            theme = merge_theme(payload.get("theme", payload))
            data = build_ktheme_bytes(theme, asset_data=payload.get("assetData"))
            filename = default_ktheme_filename(theme)
            self._send_binary(data, "application/octet-stream", filename)
        except ValueError as exc:
            self._send_json({"error": str(exc)}, status=HTTPStatus.BAD_REQUEST)
        except Exception as exc:  # pragma: no cover - defensive HTTP boundary
            self._send_json({"error": f"Export failed: {exc}"}, status=HTTPStatus.INTERNAL_SERVER_ERROR)

    def _handle_android_export(self) -> None:
        try:
            payload = self._read_json()
            theme = merge_theme(payload.get("theme", payload))
            data = build_android_resources_zip(theme)
            filename = default_android_resources_filename(theme)
            self._send_binary(data, "application/zip", filename)
        except ValueError as exc:
            self._send_json({"error": str(exc)}, status=HTTPStatus.BAD_REQUEST)
        except Exception as exc:  # pragma: no cover - defensive HTTP boundary
            self._send_json({"error": f"Export failed: {exc}"}, status=HTTPStatus.INTERNAL_SERVER_ERROR)

    def _send_json(self, value: object, status: HTTPStatus = HTTPStatus.OK) -> None:
        raw = json.dumps(value, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def _send_binary(self, data: bytes, content_type: str, filename: str) -> None:
        safe_filename = filename.replace('"', "")
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Content-Disposition", f'attachment; filename="{safe_filename}"')
        self.end_headers()
        self.wfile.write(data)


def run_server(host: str = "127.0.0.1", port: int = 8000) -> None:
    if not WEB_DIR.exists():
        raise RuntimeError(f"web directory not found: {WEB_DIR}")
    server = ThreadingHTTPServer((host, port), ThemeBuilderHandler)
    print(f"Serving on http://{host}:{port}", file=sys.stderr)
    server.serve_forever()
