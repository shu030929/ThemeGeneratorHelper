from __future__ import annotations

import io
import json
import zipfile
from pathlib import Path
from typing import Any, Mapping, BinaryIO
from xml.sax.saxutils import escape

from ..models import merge_theme, safe_filename

ANDROID_COLOR_MAP = {
    "theme_background_color": "mainBackground",
    "theme_chatroom_background_color": "chatBackground",
    "theme_header_color": "headerText",
    "theme_title_color": "mainText",
    "theme_description_color": "descriptionText",
    "theme_paragraph_color": "paragraphText",
    "theme_section_title_color": "sectionText",
    "theme_feature_text_color": "featureText",
    "theme_chatroom_input_bar_background_color": "inputBarBackground",
    "theme_chatroom_input_bar_send_button_color": "sendButtonBackground",
    "theme_chatroom_input_bar_send_button_text_color": "sendButtonText",
    "theme_chatroom_unread_count_color": "unreadText",
    "theme_chatroom_bubble_send_text_color": "messageSendText",
    "theme_chatroom_bubble_receive_text_color": "messageReceiveText",
    "theme_passcode_background_color": "passcodeBackground",
    "theme_passcode_title_color": "passcodeTitle",
    "theme_passcode_keypad_background_color": "passcodeKeypadBackground",
    "theme_passcode_keypad_text_color": "passcodeKeypadText",
    "theme_message_notification_bar_background_color": "notificationBackground",
    "theme_message_notification_bar_name_color": "notificationName",
    "theme_message_notification_bar_message_color": "notificationMessage",
}


def render_colors_xml(theme_data: Mapping[str, Any] | None = None) -> str:
    theme = merge_theme(theme_data)
    colors = theme["colors"]
    lines = ["<?xml version=\"1.0\" encoding=\"utf-8\"?>", "<resources>"]
    for android_name, token_name in ANDROID_COLOR_MAP.items():
        lines.append(f"    <color name=\"{escape(android_name)}\">{colors[token_name]}</color>")
    lines.append("</resources>")
    return "\n".join(lines) + "\n"


def render_android_manifest_overlay(theme_data: Mapping[str, Any] | None = None) -> str:
    theme = merge_theme(theme_data)
    meta = theme["meta"]
    package_id = escape(meta["androidPackageId"])
    app_name = escape(meta["name"])
    return f'''<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android" package="{package_id}">
    <application android:label="{app_name}" />
</manifest>
'''


def build_android_resources_zip(theme_data: Mapping[str, Any] | None = None) -> bytes:
    theme = merge_theme(theme_data)
    output = io.BytesIO()
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("res/values/colors.xml", render_colors_xml(theme))
        zf.writestr("AndroidManifest.overlay.xml", render_android_manifest_overlay(theme))
        zf.writestr("theme.json", json.dumps(theme, ensure_ascii=False, indent=2))
        zf.writestr(
            "README.md",
            "# Android resources export\n\n"
            "This MVP exports Android resource overlays only. To create a full APK, "
            "wire these files into the target sample Android project in a sandboxed Gradle worker.\n",
        )
    return output.getvalue()


def export_android_resources(out: str | Path | BinaryIO, theme_data: Mapping[str, Any] | None = None) -> Path | None:
    data = build_android_resources_zip(theme_data)
    if hasattr(out, "write"):
        out.write(data)  # type: ignore[union-attr]
        return None
    path = Path(out)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return path


def default_android_resources_filename(theme_data: Mapping[str, Any] | None = None) -> str:
    theme = merge_theme(theme_data)
    return safe_filename(theme["meta"]["name"], "-android-resources.zip")
