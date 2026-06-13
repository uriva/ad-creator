#!/usr/bin/env python3
"""Download fal.ai CDN media (images/videos) to local files.

fal output URLs can expire, so pull every asset locally right after generating it
and work from local paths downstream.

Usage:
    python fetch_media.py URL [URL ...] --outdir assets
    python fetch_media.py URL --out assets/shot1.mp4         # single, explicit name
    python fetch_media.py --manifest urls.txt --outdir assets  # one URL per line

Prints the local path of each downloaded file (one per line).
"""
import argparse
import os
import sys
import urllib.request
from urllib.parse import urlparse


def _name_from_url(url: str, idx: int) -> str:
    path = urlparse(url).path
    base = os.path.basename(path) or f"media_{idx}"
    if "." not in base:
        base += ".bin"
    return base


def download(url: str, dest: str) -> str:
    os.makedirs(os.path.dirname(dest) or ".", exist_ok=True)
    req = urllib.request.Request(url, headers={"User-Agent": "ad-creator/1.0"})
    with urllib.request.urlopen(req, timeout=120) as r, open(dest, "wb") as f:
        f.write(r.read())
    return dest


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("urls", nargs="*", help="One or more media URLs.")
    ap.add_argument("--out", help="Explicit output path (only valid with a single URL).")
    ap.add_argument("--outdir", default="assets", help="Output directory (default: assets).")
    ap.add_argument("--manifest", help="Text file with one URL per line.")
    args = ap.parse_args()

    urls = list(args.urls)
    if args.manifest:
        with open(args.manifest) as f:
            urls += [ln.strip() for ln in f if ln.strip() and not ln.startswith("#")]
    if not urls:
        ap.error("No URLs given.")
    if args.out and len(urls) != 1:
        ap.error("--out only works with exactly one URL; use --outdir for many.")

    results = []
    for i, url in enumerate(urls):
        dest = args.out if args.out else os.path.join(args.outdir, _name_from_url(url, i))
        try:
            results.append(download(url, dest))
            print(dest)
        except Exception as e:  # noqa
            print(f"ERROR downloading {url}: {e}", file=sys.stderr)
            sys.exit(1)
    return results


if __name__ == "__main__":
    main()
