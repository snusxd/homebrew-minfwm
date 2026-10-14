#!/usr/bin/env python3
"""Update Formula/minfwm.rb from the latest stable upstream GitHub release."""

import hashlib
import json
import os
from pathlib import Path
import re
import sys
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[2]
FORMULA_PATH = ROOT / "Formula" / "minfwm.rb"
RELEASE_API = "https://api.github.com/repos/snusxd/minfwm/releases/latest"
ARCHIVE_URL = "https://github.com/snusxd/minfwm/archive/refs/tags/{tag}.tar.gz"
MAX_ARCHIVE_BYTES = 100 * 1024 * 1024


class UpdateError(Exception):
    """Raised when upstream release metadata cannot safely update the formula."""


def version_from_tag(tag):
    match = re.fullmatch(r"v?(\d+(?:\.\d+)+)", tag)
    if not match:
        raise UpdateError(f"unsupported stable release tag: {tag!r}")
    return match.group(1)


def version_tuple(version):
    return tuple(int(part) for part in version.split("."))


def current_formula_version(formula):
    match = re.search(r'^  version "([^"\n]+)"$', formula, re.MULTILINE)
    if not match:
        raise UpdateError("could not find exactly one formula version")
    if re.search(r'^  version "[^"\n]+"$', formula[match.end():], re.MULTILINE):
        raise UpdateError("formula contains more than one version declaration")
    return match.group(1)


def replace_one(pattern, replacement, formula, field):
    updated, count = re.subn(pattern, replacement, formula, flags=re.MULTILINE)
    if count != 1:
        raise UpdateError(f"expected one {field} declaration in formula")
    return updated


def render_formula(formula, tag, sha256):
    version = version_from_tag(tag)
    if not re.fullmatch(r"[0-9a-f]{64}", sha256):
        raise UpdateError("archive checksum is not a lowercase SHA-256 value")

    formula = replace_one(
        r'^  url "https://github\.com/snusxd/minfwm/archive/refs/tags/[^"]+"$',
        f'  url "{ARCHIVE_URL.format(tag=quote(tag, safe=""))}"',
        formula,
        "upstream archive URL",
    )
    formula = replace_one(
        r'^  version "[^"\n]+"$', f'  version "{version}"', formula, "version"
    )
    formula = replace_one(
        r'^  sha256 "[0-9a-f]{64}"$', f'  sha256 "{sha256}"', formula, "SHA-256"
    )
    return formula


def request_bytes(url, token=None, limit=MAX_ARCHIVE_BYTES):
    headers = {"User-Agent": "homebrew-minfwm-formula-updater"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
        headers["Accept"] = "application/vnd.github+json"
    request = Request(url, headers=headers)
    with urlopen(request, timeout=30) as response:
        content = response.read(limit + 1)
    if len(content) > limit:
        raise UpdateError(f"response from {url} exceeds {limit} bytes")
    return content


def latest_release(token):
    try:
        metadata = json.loads(request_bytes(RELEASE_API, token).decode("utf-8"))
    except (HTTPError, URLError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise UpdateError(f"could not read latest upstream release: {error}") from error

    tag = metadata.get("tag_name")
    if not isinstance(tag, str):
        raise UpdateError("latest upstream release has no tag_name")
    version = version_from_tag(tag)
    if metadata.get("draft") or metadata.get("prerelease"):
        raise UpdateError("GitHub latest-release endpoint returned a draft or prerelease")
    return version, tag


def archive_sha256(tag):
    url = ARCHIVE_URL.format(tag=quote(tag, safe=""))
    try:
        archive = request_bytes(url)
    except (HTTPError, URLError) as error:
        raise UpdateError(f"could not download source archive for {tag}: {error}") from error
    return hashlib.sha256(archive).hexdigest()


def main():
    token = os.environ.get("GH_TOKEN")
    if not token:
        raise UpdateError("GH_TOKEN is required for authenticated GitHub API access")

    formula = FORMULA_PATH.read_text(encoding="utf-8")
    current_version = current_formula_version(formula)
    latest_version, tag = latest_release(token)
    if version_tuple(latest_version) <= version_tuple(current_version):
        print(f"Formula is current at {current_version}; latest stable release is {latest_version}.")
        return

    checksum = archive_sha256(tag)
    updated = render_formula(formula, tag, checksum)
    FORMULA_PATH.write_text(updated, encoding="utf-8")
    print(f"Updated minfwm formula from {current_version} to {latest_version} ({checksum}).")


if __name__ == "__main__":
    try:
        main()
    except (OSError, UpdateError) as error:
        print(f"update-formula: {error}", file=sys.stderr)
        raise SystemExit(1)
