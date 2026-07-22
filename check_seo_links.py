#!/usr/bin/env python3
"""Technical SEO smoke checks for the Qefro marketing site."""

from __future__ import annotations

import re
import sys
from collections import defaultdict
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent
SITE = "https://qefro.com"

SKIP_PREFIXES = ("http://", "https://", "mailto:", "tel:", "#", "data:")


class LinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.hrefs: list[str] = []
        self.skip = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in {"script", "style", "noscript"}:
            self.skip = True
        if self.skip:
            return
        if tag == "a":
            for k, v in attrs:
                if k == "href" and v:
                    self.hrefs.append(v)

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style", "noscript"}:
            self.skip = False


def normalize_internal(href: str) -> str | None:
    if href.startswith(SKIP_PREFIXES):
        if href.startswith(SITE):
            path = urlparse(href).path or "/"
        else:
            return None
    else:
        path = href.split("#", 1)[0].split("?", 1)[0]
    if not path or path.startswith("//"):
        return None
    if path.endswith(".html"):
        path = path[: -len(".html")]
    if path != "/" and path.endswith("/"):
        path = path.rstrip("/")
    return path or "/"


def file_for_path(path: str) -> Path | None:
    if path == "/":
        return ROOT / "index.html"
    clean = path.lstrip("/")
    candidate = ROOT / f"{clean}.html"
    if candidate.is_file():
        return candidate
    return None


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []

    robots = (ROOT / "robots.txt").read_text(encoding="utf-8")
    if "Sitemap: https://qefro.com/sitemap.xml" not in robots:
        errors.append("robots.txt missing Sitemap: https://qefro.com/sitemap.xml")

    sitemap = (ROOT / "sitemap.xml").read_text(encoding="utf-8")
    locs = re.findall(r"<loc>(.*?)</loc>", sitemap)
    if not locs:
        errors.append("sitemap.xml has no <loc> entries")

    html_files = sorted(ROOT.glob("*.html"))
    html_files = [p for p in html_files if p.name != "404.html"]

    inbound: dict[str, int] = defaultdict(int)
    broken: list[str] = []

    for html in html_files:
        parser = LinkParser()
        parser.feed(html.read_text(encoding="utf-8", errors="replace"))
        page_path = "/" if html.name == "index.html" else f"/{html.stem}"
        for href in parser.hrefs:
            target = normalize_internal(href)
            if target is None:
                continue
            # Ignore asset-only and special files
            if target.startswith("/assets") or target in {"/llms.txt", "/sitemap.xml", "/robots.txt"}:
                continue
            dest = file_for_path(target)
            if dest is None:
                broken.append(f"{page_path} → {target}")
            else:
                inbound[target] += 1

    # Orphans: HTML pages with zero inbound internal links (except home)
    for html in html_files:
        path = "/" if html.name == "index.html" else f"/{html.stem}"
        if path == "/":
            continue
        if inbound.get(path, 0) == 0:
            warnings.append(f"orphan (no inbound internal links): {path}")

    # Sitemap coverage for generated landings
    sitemap_paths = set()
    for loc in locs:
        p = urlparse(loc).path or "/"
        if p != "/" and p.endswith("/"):
            p = p.rstrip("/")
        sitemap_paths.add(p if p else "/")

    missing_from_sitemap = []
    for html in html_files:
        path = "/" if html.name == "index.html" else f"/{html.stem}"
        if path not in sitemap_paths:
            missing_from_sitemap.append(path)

    if missing_from_sitemap:
        errors.append(
            "HTML pages missing from sitemap.xml: " + ", ".join(missing_from_sitemap[:20])
            + ("…" if len(missing_from_sitemap) > 20 else "")
        )

    extra_in_sitemap = []
    for path in sorted(sitemap_paths):
        if path.startswith("/assets"):
            continue
        if file_for_path(path) is None:
            extra_in_sitemap.append(path)
    if extra_in_sitemap:
        errors.append("sitemap locs without HTML files: " + ", ".join(extra_in_sitemap[:20]))

    if broken:
        errors.append(f"{len(broken)} broken internal links (showing 15): " + "; ".join(broken[:15]))

    print(f"pages={len(html_files)} sitemap_urls={len(locs)} inbound_checked_ok")
    for w in warnings[:30]:
        print("WARN:", w)
    if len(warnings) > 30:
        print(f"WARN: … {len(warnings) - 30} more orphans")
    for e in errors:
        print("ERR:", e)

    # Soft: orphans are warnings (hubs may cover). Hard fail on broken/sitemap/robots.
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
