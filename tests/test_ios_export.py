from __future__ import annotations

import io
import json
import unittest
import zipfile

from makeetheme.ios.exporter import build_ktheme_bytes
from makeetheme.ios.css import render_css
from makeetheme.models import merge_theme
from makeetheme.android.resources import render_colors_xml, build_android_resources_zip


class IosExportTests(unittest.TestCase):
    def test_ios_export_contains_css_images_and_theme_json(self) -> None:
        theme = merge_theme({"meta": {"name": "Test Theme", "iosThemeId": "com.example.test.theme.ios", "androidPackageId": "com.example.test.theme"}})
        data = build_ktheme_bytes(theme)
        with zipfile.ZipFile(io.BytesIO(data)) as zf:
            names = set(zf.namelist())
            self.assertIn("KakaoTalkTheme.css", names)
            self.assertIn("theme.json", names)
            self.assertIn("Images/mainBgImage@3x.png", names)
            self.assertIn("Images/chatroomBubbleSend01@3x.png", names)
            css = zf.read("KakaoTalkTheme.css").decode("utf-8")
            self.assertIn("-kakaotalk-theme-name: 'Test Theme';", css)
            self.assertIn("MessageCellStyle-Send", css)
            theme_json = json.loads(zf.read("theme.json").decode("utf-8"))
            self.assertEqual(theme_json["meta"]["name"], "Test Theme")

    def test_css_contains_expected_theme_id(self) -> None:
        theme = merge_theme({"meta": {"iosThemeId": "com.example.theme.custom.ios"}})
        css = render_css(theme)
        self.assertIn("-kakaotalk-theme-id: 'com.example.theme.custom.ios';", css)

    def test_android_resources_zip_contains_colors_xml(self) -> None:
        theme = merge_theme({"colors": {"mainBackground": "#123456"}})
        colors_xml = render_colors_xml(theme)
        self.assertIn("<color name=\"theme_background_color\">#123456</color>", colors_xml)
        data = build_android_resources_zip(theme)
        with zipfile.ZipFile(io.BytesIO(data)) as zf:
            self.assertIn("res/values/colors.xml", zf.namelist())
            self.assertIn("theme.json", zf.namelist())


if __name__ == "__main__":
    unittest.main()
