"""Regression checks for canonical public documentation banners."""

from __future__ import annotations

import pathlib
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


if __name__ == "__main__":
    unittest.main()
