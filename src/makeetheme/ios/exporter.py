from __future__ import annotations

import io
import json
import zipfile
from pathlib import Path
from typing import Any, Mapping, BinaryIO

from ..assets_payload import decode_asset_data
from ..models import merge_theme, safe_filename
from .assets import generate_assets
from .css import render_css


def build_ktheme_bytes(theme_data: Mapping[str, Any] | None = None, asset_data: Mapping[str, str] | None = None) -> bytes:
    theme = merge_theme(theme_data)
    supplied_assets = decode_asset_data(asset_data)
    assets = generate_assets(theme, supplied_assets=supplied_assets)
    css = render_css(theme).encode("utf-8")
    manifest_json = json.dumps(theme, ensure_ascii=False, indent=2).encode("utf-8")

    output = io.BytesIO()
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("KakaoTalkTheme.css", css)
        zf.writestr("theme.json", manifest_json)
        for filename, data in sorted(assets.items()):
            zf.writestr(f"Images/{filename}", data)
    return output.getvalue()


def export_ktheme(
    out: str | Path | BinaryIO,
    theme_data: Mapping[str, Any] | None = None,
    asset_data: Mapping[str, str] | None = None,
) -> Path | None:
    data = build_ktheme_bytes(theme_data=theme_data, asset_data=asset_data)
    if hasattr(out, "write"):
        out.write(data)  # type: ignore[union-attr]
        return None
    path = Path(out)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return path


def default_ktheme_filename(theme_data: Mapping[str, Any] | None = None) -> str:
    theme = merge_theme(theme_data)
    return safe_filename(theme["meta"]["name"], ".ktheme")
