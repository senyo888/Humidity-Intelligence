"""Regression checks for canonical public documentation banners."""

from __future__ import annotations

import hashlib
import pathlib
import struct
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]

CANONICAL_DOC_BANNERS = {
    "AGENTS.md": "![Humidity Intelligence agent header](assets/agent-banner.png)",
    "CHANGELOG.md": "![Humidity Intelligence changelog header](assets/change-log.png)",
    "CODE_OF_CONDUCT.md": "![Humidity Intelligence code of conduct header](assets/code-of-conduct.png)",
    "CONTRIBUTING.md": "![Humidity Intelligence contributing header](assets/contributing-header.png)",
    "SECURITY.md": "![Humidity Intelligence security policy header](assets/security.png)",
    "ui-gallery/CONTRIBUTING.md": "![Humidity Intelligence UI Gallery contributing banner](../assets/header.png)",
    "ui-gallery/README.md": "![Humidity Intelligence UI Gallery banner](../assets/header.png)",
}

RELEASE_BANNER_FAMILY = (
    "v2.0.6_release.png",
    "v2.0.7_release.png",
    "v2.0.8_release.png",
    "v2.0.9_release.png",
)

PUBLISHED_V208_BANNER_SHA256 = (
    "9bd301840c764af85d443a22912f73e67b98a181045db8193c052d15fb560b78"
)


def _asset_path(doc_path: pathlib.Path, markdown_line: str) -> pathlib.Path:
    start = markdown_line.rfind("(")
    end = markdown_line.rfind(")")
    if start == -1 or end == -1 or end <= start + 1:
        raise AssertionError(f"Banner line is not a Markdown image: {markdown_line}")
    return doc_path.parent / markdown_line[start + 1 : end]


class DocumentationBannerTests(unittest.TestCase):
    def test_public_docs_start_with_canonical_banner(self) -> None:
        for doc_name, banner_line in CANONICAL_DOC_BANNERS.items():
            with self.subTest(doc=doc_name):
                doc_path = ROOT / doc_name
                first_line = doc_path.read_text(encoding="utf-8").splitlines()[0]

                self.assertEqual(first_line, banner_line)

    def test_canonical_banner_assets_exist_as_pngs(self) -> None:
        for doc_name, banner_line in CANONICAL_DOC_BANNERS.items():
            with self.subTest(doc=doc_name):
                doc_path = ROOT / doc_name
                asset_path = _asset_path(doc_path, banner_line)

                self.assertTrue(asset_path.exists(), f"{asset_path} is missing")
                self.assertEqual(asset_path.suffix, ".png")
                self.assertEqual(asset_path.read_bytes()[:8], b"\x89PNG\r\n\x1a\n")

    def test_release_banner_family_preserves_published_history(self) -> None:
        release_banner_dir = ROOT / "assets" / "release_banner"

        for banner_name in RELEASE_BANNER_FAMILY:
            with self.subTest(banner=banner_name):
                banner_path = release_banner_dir / banner_name
                banner_bytes = banner_path.read_bytes()

                self.assertEqual(banner_bytes[:8], b"\x89PNG\r\n\x1a\n")
                width, height = struct.unpack(">II", banner_bytes[16:24])
                self.assertGreater(width, 0)
                self.assertGreater(height, 0)

        published_v208 = (release_banner_dir / "v2.0.8_release.png").read_bytes()
        self.assertEqual(
            hashlib.sha256(published_v208).hexdigest(),
            PUBLISHED_V208_BANNER_SHA256,
        )

        v209_bytes = (release_banner_dir / "v2.0.9_release.png").read_bytes()
        self.assertEqual(struct.unpack(">II", v209_bytes[16:24]), (1600, 900))


if __name__ == "__main__":
    unittest.main()
