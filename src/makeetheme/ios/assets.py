from __future__ import annotations

from typing import Any, Dict, Mapping

from ..models import hex_to_rgba, darken, lighten
from ..png import Canvas, RGBA, solid_png

# Dimensions are based on the public sample theme structure. The CSS references
# names without scale suffixes; iOS resolves @2x/@3x PNG variants automatically.
SCALE_SIZES: dict[str, dict[int, tuple[int, int]]] = {
    "background": {2: (750, 1500), 3: (1125, 2250)},
    "tab_bg": {2: (940, 98), 3: (1410, 147)},
    "tab_icon": {2: (76, 76), 3: (114, 114)},
    "bubble": {2: (80, 70), 3: (120, 105)},
    "profile": {2: (240, 240), 3: (360, 360)},
    "passcode_bullet": {3: (132, 132)},
    "keypad": {3: (180, 180)},
    "add_friend": {2: (84, 68), 3: (126, 102)},
    "theme_icon": {3: (162, 162)},
}

TAB_BASES = [
    "maintabIcoFriends",
    "maintabIcoChats",
    "maintabIcoNow",
    "maintabIcoPiccoma",
    "maintabIcoShopping",
    "maintabIcoCall",
    "maintabIcoMore",
]

REQUIRED_ASSET_BASES: dict[str, str] = {
    "mainBgImage": "background",
    "chatroomBgImage": "background",
    "passcodeBgImage": "background",
    "maintabBgImage": "tab_bg",
    "findBtnAddFriend": "add_friend",
    "profileImg01": "profile",
    "commonIcoTheme": "theme_icon",
    **{base: "tab_icon" for base in TAB_BASES},
    **{f"{base}Selected": "tab_icon" for base in TAB_BASES},
    "chatroomBubbleSend01": "bubble",
    "chatroomBubbleSend01Selected": "bubble",
    "chatroomBubbleSend02": "bubble",
    "chatroomBubbleSend02Selected": "bubble",
    "chatroomBubbleReceive01": "bubble",
    "chatroomBubbleReceive01Selected": "bubble",
    "chatroomBubbleReceive02": "bubble",
    "chatroomBubbleReceive02Selected": "bubble",
    "passcodeImgCode01": "passcode_bullet",
    "passcodeImgCode02": "passcode_bullet",
    "passcodeImgCode03": "passcode_bullet",
    "passcodeImgCode04": "passcode_bullet",
    "passcodeImgCode01Selected": "passcode_bullet",
    "passcodeImgCode02Selected": "passcode_bullet",
    "passcodeImgCode03Selected": "passcode_bullet",
    "passcodeImgCode04Selected": "passcode_bullet",
    "passcodeKeypadPressed": "keypad",
}


def asset_filenames() -> list[str]:
    names: list[str] = []
    for base, kind in REQUIRED_ASSET_BASES.items():
        for scale in sorted(SCALE_SIZES[kind]):
            names.append(f"{base}@{scale}x.png")
    return sorted(names)


def generate_assets(theme: Mapping[str, Any], supplied_assets: Mapping[str, bytes] | None = None) -> Dict[str, bytes]:
    supplied_assets = supplied_assets or {}
    result: Dict[str, bytes] = {}
    for base, kind in REQUIRED_ASSET_BASES.items():
        for scale, (width, height) in SCALE_SIZES[kind].items():
            filename = f"{base}@{scale}x.png"
            if filename in supplied_assets:
                result[filename] = supplied_assets[filename]
            else:
                result[filename] = _generate_asset(base, kind, width, height, scale, theme)
    return result


def _generate_asset(base: str, kind: str, width: int, height: int, scale: int, theme: Mapping[str, Any]) -> bytes:
    c = theme["colors"]
    if kind == "background":
        if base == "chatroomBgImage":
            return solid_png(width, height, hex_to_rgba(c["chatBackground"]))
        if base == "passcodeBgImage":
            return solid_png(width, height, hex_to_rgba(c["passcodeBackground"]))
        return solid_png(width, height, hex_to_rgba(c["mainBackground"]))
    if kind == "tab_bg":
        return solid_png(width, height, hex_to_rgba(c["tabBarBackground"]))
    if kind == "tab_icon":
        selected = base.endswith("Selected")
        icon_color = hex_to_rgba(c["iconSelected"] if selected else c["iconNormal"])
        return _tab_icon_png(width, height, icon_color, base.replace("Selected", ""))
    if kind == "bubble":
        return _bubble_png(width, height, base, c)
    if kind == "profile":
        return _profile_png(width, height, hex_to_rgba(c["profileBackground"]), hex_to_rgba(c["profileAccent"]))
    if kind == "passcode_bullet":
        selected = base.endswith("Selected")
        return _passcode_bullet_png(width, height, hex_to_rgba(c["iconSelected"] if selected else c["tabText"]), selected)
    if kind == "keypad":
        return _keypad_png(width, height, hex_to_rgba(lighten(c["passcodeKeypadBackground"], 0.05)))
    if kind == "add_friend":
        return _add_friend_png(width, height, hex_to_rgba(c["iconSelected"]))
    if kind == "theme_icon":
        return _profile_png(width, height, hex_to_rgba(c["bubbleSendBackground"]), hex_to_rgba(c["profileAccent"]))
    raise ValueError(f"Unsupported asset kind: {kind}")


def _tab_icon_png(width: int, height: int, color: RGBA, base: str) -> bytes:
    cv = Canvas(width, height)
    s = min(width, height)
    cx, cy = width // 2, height // 2
    t = max(2, s // 18)
    if "Friends" in base:
        cv.circle(cx - s // 10, cy - s // 10, s // 7, color)
        cv.circle(cx + s // 9, cy - s // 12, s // 8, color)
        cv.rounded_rect(cx - s // 4, cy + s // 12, cx + s // 4, cy + s // 4, s // 10, color)
    elif "Chats" in base or "Now" in base or "Piccoma" in base:
        cv.rounded_rect(s // 5, s // 4, width - s // 5, height - s // 4, s // 8, color)
        cv.polygon([(cx - s // 10, height - s // 4), (cx, height - s // 8), (cx + s // 12, height - s // 4)], color)
        dot = max(2, s // 22)
        for x in (cx - s // 7, cx, cx + s // 7):
            cv.circle(x, cy, dot, (255, 255, 255, color[3]))
    elif "Shopping" in base:
        cv.rounded_rect(s // 4, s // 3, width - s // 4, height - s // 5, s // 12, color)
        cv.ring(cx, s // 3, s // 7, t, color)
    elif "Call" in base:
        cv.line(s // 3, s // 4, width - s // 3, height - s // 4, color, t * 2)
        cv.circle(s // 3, s // 4, t * 2, color)
        cv.circle(width - s // 3, height - s // 4, t * 2, color)
    else:
        r = max(3, s // 15)
        for x in (cx - s // 6, cx, cx + s // 6):
            cv.circle(x, cy, r, color)
    return cv.to_png()


def _bubble_png(width: int, height: int, base: str, colors: Mapping[str, str]) -> bytes:
    is_send = "Send" in base
    is_selected = "Selected" in base
    is_group = "02" in base
    if is_send:
        color_hex = colors["bubbleSendSelectedBackground"] if is_selected else colors["bubbleSendBackground"]
    else:
        color_hex = colors["bubbleReceiveSelectedBackground"] if is_selected else colors["bubbleReceiveBackground"]
    color = hex_to_rgba(color_hex)
    cv = Canvas(width, height)
    pad = max(3, width // 20)
    radius = max(8, height // 5)
    tail = max(8, width // 8)
    if is_send:
        x0, x1 = pad, width - pad - (0 if is_group else tail // 2)
        cv.rounded_rect(x0, pad, x1, height - pad, radius, color)
        if not is_group:
            cv.polygon([(x1 - 2, height // 2 - tail // 2), (width - pad, height // 2 - 1), (x1 - 2, height // 2 + tail // 2)], color)
    else:
        x0, x1 = pad + (0 if is_group else tail // 2), width - pad
        cv.rounded_rect(x0, pad, x1, height - pad, radius, color)
        if not is_group:
            cv.polygon([(x0 + 2, height // 2 - tail // 2), (pad, height // 2 - 1), (x0 + 2, height // 2 + tail // 2)], color)
    return cv.to_png()


def _profile_png(width: int, height: int, bg: RGBA, accent: RGBA) -> bytes:
    cv = Canvas(width, height)
    s = min(width, height)
    cv.circle(width // 2, height // 2, s // 2 - max(2, s // 40), bg)
    cv.circle(width // 2, height // 2 - s // 9, s // 7, accent)
    cv.rounded_rect(width // 2 - s // 5, height // 2 + s // 12, width // 2 + s // 5, height // 2 + s // 4, s // 12, accent)
    return cv.to_png()


def _passcode_bullet_png(width: int, height: int, color: RGBA, selected: bool) -> bytes:
    cv = Canvas(width, height)
    if selected:
        cv.circle(width // 2, height // 2, min(width, height) // 8, color)
    else:
        cv.ring(width // 2, height // 2, min(width, height) // 8, max(3, min(width, height) // 32), color)
    return cv.to_png()


def _keypad_png(width: int, height: int, color: RGBA) -> bytes:
    cv = Canvas(width, height)
    cv.circle(width // 2, height // 2, min(width, height) // 2 - 2, color)
    return cv.to_png()


def _add_friend_png(width: int, height: int, color: RGBA) -> bytes:
    cv = Canvas(width, height)
    s = min(width, height)
    cv.circle(width // 2 - s // 8, height // 2, s // 5, color)
    t = max(3, s // 18)
    cv.line(width // 2 + s // 7, height // 2, width // 2 + s // 3, height // 2, color, t)
    cv.line(width // 2 + s // 4, height // 2 - s // 12, width // 2 + s // 4, height // 2 + s // 12, color, t)
    return cv.to_png()
