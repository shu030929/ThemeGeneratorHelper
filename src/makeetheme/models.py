from __future__ import annotations

import copy
import re
from typing import Any, Dict, Mapping

HEX_RE = re.compile(r"^#[0-9A-Fa-f]{6}([0-9A-Fa-f]{2})?$")
THEME_ID_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_]*(\.[A-Za-z][A-Za-z0-9_]*)+$")

DEFAULT_THEME: Dict[str, Any] = {
    "meta": {
        "name": "MAKEETHEME Theme",
        "authorName": "MAKEETHEME",
        "version": "25.8.0",
        "url": "https://example.com",
        "iosThemeId": "com.example.talk.theme.makeetheme.ios",
        "androidPackageId": "com.example.talk.theme.makeetheme",
    },
    "colors": {
        "tabBarBackground": "#FFFFFF",
        "headerText": "#664242",
        "tabText": "#B39898",
        "tabHighlightedText": "#664242",
        "mainBackground": "#FFDEDE",
        "mainText": "#664242",
        "mainTextPressed": "#946C6C",
        "descriptionText": "#805959",
        "descriptionTextPressed": "#946C6C",
        "paragraphText": "#805959",
        "paragraphTextPressed": "#946C6C",
        "cellBackground": "#F66C6C",
        "cellSelectedBackground": "#664242",
        "sectionBorder": "#F66C6C",
        "sectionText": "#F66C6C",
        "featureText": "#805959",
        "chatBackground": "#FFDEDE",
        "inputBarBackground": "#FFFFFF",
        "sendButtonBackground": "#FF7F7F",
        "sendButtonText": "#FFFFFF",
        "sendButtonPressedBackground": "#F27979",
        "sendButtonPressedText": "#FFDEDE",
        "inputIcon": "#E86464",
        "inputIconPressed": "#CB6F6F",
        "inputButtonText": "#191919",
        "inputButtonBackground": "#000000",
        "messageSendText": "#FFFFFF",
        "messageReceiveText": "#4D4D4D",
        "unreadText": "#FF7F7F",
        "passcodeBackground": "#FFDEDE",
        "passcodeTitle": "#664242",
        "passcodeKeypadBackground": "#FFF2F2",
        "passcodeKeypadText": "#664242",
        "notificationBackground": "#FCC5C5",
        "notificationName": "#604242",
        "notificationMessage": "#805959",
        "directShareBackground": "#FFFFFF",
        "bubbleSendBackground": "#FF7F7F",
        "bubbleSendSelectedBackground": "#F27979",
        "bubbleReceiveBackground": "#FFFFFF",
        "bubbleReceiveSelectedBackground": "#F6E8E8",
        "profileBackground": "#F6A4A4",
        "profileAccent": "#FFFFFF",
        "iconNormal": "#B39898",
        "iconSelected": "#664242",
    },
    "options": {
        "mainBackgroundImageMode": "cover",
        "chatBackgroundImageMode": "cover",
        "passcodeBackgroundImageMode": "cover",
    },
}


def deep_merge(base: Mapping[str, Any], override: Mapping[str, Any]) -> Dict[str, Any]:
    merged: Dict[str, Any] = copy.deepcopy(dict(base))
    for key, value in override.items():
        if isinstance(value, Mapping) and isinstance(merged.get(key), Mapping):
            merged[key] = deep_merge(merged[key], value)
        else:
            merged[key] = copy.deepcopy(value)
    return merged


def merge_theme(data: Mapping[str, Any] | None) -> Dict[str, Any]:
    """Merge user data with DEFAULT_THEME and validate basic values."""
    theme = deep_merge(DEFAULT_THEME, data or {})
    validate_theme(theme)
    return theme


def validate_theme(theme: Mapping[str, Any]) -> None:
    meta = theme.get("meta")
    colors = theme.get("colors")
    if not isinstance(meta, Mapping):
        raise ValueError("theme.meta must be an object")
    if not isinstance(colors, Mapping):
        raise ValueError("theme.colors must be an object")

    required_meta = ["name", "authorName", "version", "iosThemeId", "androidPackageId"]
    for key in required_meta:
        value = meta.get(key)
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"theme.meta.{key} must be a non-empty string")

    if not THEME_ID_RE.match(str(meta["iosThemeId"])):
        raise ValueError("theme.meta.iosThemeId must look like a reverse-domain id")
    if not THEME_ID_RE.match(str(meta["androidPackageId"])):
        raise ValueError("theme.meta.androidPackageId must look like a reverse-domain id")

    for key, value in colors.items():
        if not isinstance(value, str) or not HEX_RE.match(value):
            raise ValueError(f"theme.colors.{key} must be #RRGGBB or #RRGGBBAA")


def hex_to_rgba(value: str, alpha_override: int | None = None) -> tuple[int, int, int, int]:
    value = value.strip().lstrip("#")
    if len(value) == 6:
        r, g, b = int(value[0:2], 16), int(value[2:4], 16), int(value[4:6], 16)
        a = 255
    elif len(value) == 8:
        r, g, b, a = (
            int(value[0:2], 16),
            int(value[2:4], 16),
            int(value[4:6], 16),
            int(value[6:8], 16),
        )
    else:
        raise ValueError(f"Invalid color: {value!r}")
    if alpha_override is not None:
        a = alpha_override
    return r, g, b, a


def rgba_to_hex(color: tuple[int, int, int, int]) -> str:
    r, g, b, a = color
    if a == 255:
        return f"#{r:02X}{g:02X}{b:02X}"
    return f"#{r:02X}{g:02X}{b:02X}{a:02X}"


def darken(hex_color: str, amount: float = 0.08) -> str:
    r, g, b, a = hex_to_rgba(hex_color)
    factor = max(0.0, min(1.0, 1.0 - amount))
    return rgba_to_hex((int(r * factor), int(g * factor), int(b * factor), a))


def lighten(hex_color: str, amount: float = 0.08) -> str:
    r, g, b, a = hex_to_rgba(hex_color)
    amount = max(0.0, min(1.0, amount))
    return rgba_to_hex((
        int(r + (255 - r) * amount),
        int(g + (255 - g) * amount),
        int(b + (255 - b) * amount),
        a,
    ))


def safe_filename(value: str, suffix: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9._-]+", "-", value.strip()).strip("-._")
    if not slug:
        slug = "user-theme"
    return f"{slug}{suffix}"
