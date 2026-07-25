#!/usr/bin/env python3
"""Build or verify deterministic CRP specification release assets."""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import re
import subprocess
import sys
import unicodedata
import zipfile
from pathlib import Path

REPOSITORY_URL = "https://github.com/LeonidMajbits/CRP-context-reconstruction-protocol"
SEMVER_RE = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")
MANIFEST_NAME = "SHA256SUMS"
BUNDLE_EXCLUDED_DIRECTORIES = frozenset(
    {
        ".git",
        ".mypy_cache",
        ".pytest_cache",
        ".ruff_cache",
        ".tox",
        ".venv",
        "__pycache__",
        "build",
        "dist",
        "venv",
    }
)
WINDOWS_RESERVED_COMPONENTS = frozenset(
    {
        "aux",
        "clock$",
        "con",
        "nul",
        "prn",
        *(f"com{index}" for index in range(1, 10)),
        *(f"lpt{index}" for index in range(1, 10)),
    }
)
IndexedSources = dict[str, tuple[int, bytes]]


class ReleaseAssetError(RuntimeError):
    """Raised when release inputs or staged artifacts violate the release contract."""


def _indexed_bytes(sources: IndexedSources, relative: str) -> bytes:
    try:
        return sources[relative][1]
    except KeyError as exc:
        raise ReleaseAssetError(
            f"missing indexed release source file: {relative}"
        ) from exc


def read_version(sources: IndexedSources) -> tuple[str, str]:
    try:
        exact = _indexed_bytes(sources, "VERSION").decode("utf-8").strip()
    except UnicodeDecodeError as exc:
        raise ReleaseAssetError(f"VERSION is not UTF-8: {exc}") from exc
    match = SEMVER_RE.fullmatch(exact)
    if not match:
        raise ReleaseAssetError("VERSION must contain a stable semantic version")
    return exact, f"{match.group(1)}.{match.group(2)}"


def source_mapping(exact_version: str) -> dict[str, str]:
    prefix = f"crp-{exact_version}"
    return {
        f"{prefix}-citation.cff": "CITATION.cff",
        f"{prefix}-conformance.md": "docs/conformance.md",
        f"{prefix}-license.txt": "LICENSE",
        f"{prefix}-schema.json": "schema/crp.schema.json",
        f"{prefix}-security-and-trust.md": "docs/security-and-trust.md",
        f"{prefix}-spec.md": "docs/crp-spec-v1.md",
    }


def _validate_sources(
    exact_version: str,
    protocol_version: str,
    release_sources: dict[str, str],
    indexed_sources: IndexedSources,
) -> None:
    missing = [
        relative
        for relative in release_sources.values()
        if relative not in indexed_sources
    ]
    if missing:
        raise ReleaseAssetError(
            "missing release source files: " + ", ".join(sorted(missing))
        )

    try:
        schema = json.loads(
            _indexed_bytes(indexed_sources, "schema/crp.schema.json").decode("utf-8")
        )
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise ReleaseAssetError(f"cannot parse release schema: {exc}") from exc
    actual_protocol = (
        schema.get("properties", {}).get("protocol_version", {}).get("const")
    )
    if actual_protocol != protocol_version:
        raise ReleaseAssetError(
            f"schema protocol_version is {actual_protocol!r}, expected {protocol_version!r}"
        )

    try:
        citation = _indexed_bytes(indexed_sources, "CITATION.cff").decode("utf-8")
        specification = _indexed_bytes(indexed_sources, "docs/crp-spec-v1.md").decode(
            "utf-8"
        )
    except UnicodeDecodeError as exc:
        raise ReleaseAssetError(f"release metadata is not UTF-8: {exc}") from exc
    version_pattern = re.compile(
        rf"^version:\s*[\"']?{re.escape(exact_version)}[\"']?\s*$",
        re.MULTILINE,
    )
    if not version_pattern.search(citation):
        raise ReleaseAssetError(
            f"CITATION.cff does not declare version {exact_version}"
        )

    if not re.search(
        rf"^# Context Reconstruction Protocol Specification v{re.escape(exact_version)}\s*$",
        specification,
        re.MULTILINE,
    ):
        raise ReleaseAssetError("specification heading does not match VERSION")


def _git_bytes(root: Path, arguments: list[str]) -> bytes:
    try:
        completed = subprocess.run(
            ["git", "-c", "core.quotePath=false", "-C", str(root), *arguments],
            check=False,
            capture_output=True,
            timeout=30,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise ReleaseAssetError(f"cannot inspect indexed source files: {exc}") from exc
    if completed.returncode != 0:
        message = completed.stderr.decode("utf-8", errors="replace").strip()
        raise ReleaseAssetError(
            "cannot inspect indexed source files" + (f": {message}" if message else "")
        )
    return completed.stdout


def _require_clean_tracked_worktree(root: Path) -> None:
    try:
        completed = subprocess.run(
            [
                "git",
                "-C",
                str(root),
                "diff",
                "--quiet",
                "--no-ext-diff",
                "--",
            ],
            check=False,
            capture_output=True,
            timeout=30,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise ReleaseAssetError(f"cannot compare worktree with index: {exc}") from exc
    if completed.returncode == 1:
        raise ReleaseAssetError(
            "tracked worktree content differs from the release index; stage or discard it"
        )
    if completed.returncode != 0:
        message = completed.stderr.decode("utf-8", errors="replace").strip()
        raise ReleaseAssetError(
            "cannot compare worktree with index" + (f": {message}" if message else "")
        )


def _validate_indexed_path(raw_path: str) -> str:
    if (
        not raw_path
        or raw_path.startswith("/")
        or any(character in raw_path for character in '\\:<>"|?*')
    ):
        raise ReleaseAssetError(f"unsafe indexed source path: {raw_path!r}")
    if unicodedata.normalize("NFC", raw_path) != raw_path:
        raise ReleaseAssetError(f"indexed source path is not Unicode NFC: {raw_path!r}")
    if len(raw_path.encode("utf-8")) > 1_024:
        raise ReleaseAssetError(
            f"indexed source path exceeds 1024 UTF-8 bytes: {raw_path!r}"
        )
    parts = raw_path.split("/")
    excluded = {part.casefold() for part in BUNDLE_EXCLUDED_DIRECTORIES}
    for part in parts:
        if not part or part in {".", ".."}:
            raise ReleaseAssetError(f"unsafe indexed source path: {raw_path!r}")
        if len(part.encode("utf-8")) > 255:
            raise ReleaseAssetError(
                f"indexed source path component exceeds 255 UTF-8 bytes: {raw_path!r}"
            )
        if part.endswith((" ", ".")):
            raise ReleaseAssetError(
                f"indexed source path has a trailing dot or space: {raw_path!r}"
            )
        if part.split(".", 1)[0].casefold() in WINDOWS_RESERVED_COMPONENTS:
            raise ReleaseAssetError(
                f"indexed source path uses a Windows-reserved component: {raw_path!r}"
            )
        if part.casefold() in excluded:
            raise ReleaseAssetError(
                f"generated or private directory is tracked: {raw_path!r}"
            )
        for character in part:
            if unicodedata.category(character) in {"Cc", "Cf", "Cs", "Zl", "Zp"}:
                raise ReleaseAssetError(
                    f"indexed source path contains an unsafe Unicode character: {raw_path!r}"
                )
    return "/".join(parts)


def _indexed_sources(root: Path) -> IndexedSources:
    _require_clean_tracked_worktree(root)
    ignored_output = _git_bytes(
        root,
        ["ls-files", "--cached", "--ignored", "--exclude-standard", "-z"],
    )
    if ignored_output:
        ignored = [
            item.decode("utf-8", errors="backslashreplace")
            for item in ignored_output.split(b"\0")
            if item
        ]
        raise ReleaseAssetError(
            "ignored or private files are tracked: " + ", ".join(sorted(ignored))
        )
    output = _git_bytes(root, ["ls-files", "--cached", "--stage", "-z"])
    sources: IndexedSources = {}
    collision_keys: dict[str, str] = {}
    try:
        records = [record for record in output.split(b"\0") if record]
        for record in records:
            metadata, separator, raw_path = record.partition(b"\t")
            fields = metadata.split()
            if not separator or len(fields) != 3:
                raise ReleaseAssetError("unexpected Git index record")
            mode_text, object_id, stage = fields
            if stage != b"0":
                raise ReleaseAssetError("unmerged index entries are not releasable")
            try:
                relative = _validate_indexed_path(raw_path.decode("utf-8"))
                mode = int(mode_text, 8)
            except (UnicodeDecodeError, ValueError) as exc:
                raise ReleaseAssetError(f"invalid Git index record: {exc}") from exc
            if mode not in {0o100644, 0o100755}:
                raise ReleaseAssetError(
                    f"indexed source is not a regular file: {relative} (mode {mode_text.decode()})"
                )
            collision_key = relative.casefold()
            previous = collision_keys.get(collision_key)
            if previous is not None:
                raise ReleaseAssetError(
                    f"case-insensitive indexed path collision: {previous!r} and {relative!r}"
                )
            collision_keys[collision_key] = relative
            sources[relative] = (
                mode,
                _git_bytes(root, ["cat-file", "blob", object_id.decode("ascii")]),
            )
    except UnicodeDecodeError as exc:
        raise ReleaseAssetError(f"indexed source path is not UTF-8: {exc}") from exc
    if not sources:
        raise ReleaseAssetError("indexed release bundle source set is empty")
    return sources


def _bundle_bytes(sources: IndexedSources, exact_version: str) -> bytes:
    prefix = f"crp-{exact_version}"
    output = io.BytesIO()
    with zipfile.ZipFile(output, mode="w", compression=zipfile.ZIP_STORED) as archive:
        for relative, (mode, data) in sorted(
            sources.items(), key=lambda item: item[0].casefold()
        ):
            info = zipfile.ZipInfo(
                filename=f"{prefix}/{relative}",
                date_time=(1980, 1, 1, 0, 0, 0),
            )
            info.compress_type = zipfile.ZIP_STORED
            info.create_system = 3
            info.external_attr = mode << 16
            info.extra = b""
            archive.writestr(info, data)
    return output.getvalue()


def _standalone_markdown(
    source: bytes,
    *,
    exact_version: str,
) -> bytes:
    try:
        text = source.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ReleaseAssetError(f"release Markdown is not UTF-8: {exc}") from exc
    tag_root = f"{REPOSITORY_URL}/blob/v{exact_version}"
    replacements = {
        "(../schema/crp.schema.json)": f"({tag_root}/schema/crp.schema.json)",
        "(conformance.md)": f"({tag_root}/docs/conformance.md)",
        "(crp-spec-v1.md)": f"({tag_root}/docs/crp-spec-v1.md)",
        "(security-and-trust.md)": f"({tag_root}/docs/security-and-trust.md)",
    }
    for source_target, release_target in replacements.items():
        text = text.replace(source_target, release_target)
    return text.encode("utf-8")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def expected_assets(root: Path) -> dict[str, bytes]:
    root = root.resolve()
    indexed_sources = _indexed_sources(root)
    exact_version, protocol_version = read_version(indexed_sources)
    release_sources = source_mapping(exact_version)
    _validate_sources(
        exact_version,
        protocol_version,
        release_sources,
        indexed_sources,
    )

    payloads: dict[str, bytes] = {}
    for name, relative in release_sources.items():
        data = _indexed_bytes(indexed_sources, relative)
        if name.endswith(".md"):
            data = _standalone_markdown(data, exact_version=exact_version)
        payloads[name] = data
    payloads[f"crp-{exact_version}-bundle.zip"] = _bundle_bytes(
        indexed_sources, exact_version
    )

    manifest = "".join(
        f"{sha256(payloads[name])}  {name}\n" for name in sorted(payloads)
    ).encode("utf-8")
    payloads[MANIFEST_NAME] = manifest
    return payloads


def _unexpected_names(output: Path, expected_names: set[str]) -> list[str]:
    if not output.exists():
        return []
    return sorted(
        path.name
        for path in output.iterdir()
        if not path.is_file() or path.name not in expected_names
    )


def build_assets(root: Path, output: Path) -> dict[str, bytes]:
    payloads = expected_assets(root)
    output = output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    unexpected = _unexpected_names(output, set(payloads))
    if unexpected:
        raise ReleaseAssetError(
            "output directory contains unexpected entries: " + ", ".join(unexpected)
        )
    for name, data in sorted(payloads.items()):
        destination = output / name
        temporary = output / f".{name}.tmp"
        temporary.write_bytes(data)
        os.replace(temporary, destination)
    return payloads


def verify_assets(root: Path, output: Path) -> dict[str, bytes]:
    payloads = expected_assets(root)
    output = output.resolve()
    if not output.is_dir():
        raise ReleaseAssetError(f"release output directory does not exist: {output}")
    actual_names = {path.name for path in output.iterdir()}
    expected_names = set(payloads)
    if actual_names != expected_names:
        missing = sorted(expected_names - actual_names)
        unexpected = sorted(actual_names - expected_names)
        details: list[str] = []
        if missing:
            details.append("missing=" + ",".join(missing))
        if unexpected:
            details.append("unexpected=" + ",".join(unexpected))
        raise ReleaseAssetError("release asset set differs: " + "; ".join(details))
    for name, expected in sorted(payloads.items()):
        path = output / name
        if not path.is_file():
            raise ReleaseAssetError(f"release asset is not a regular file: {name}")
        actual = path.read_bytes()
        if actual != expected:
            raise ReleaseAssetError(
                f"release asset content differs: {name} "
                f"(expected {sha256(expected)}, found {sha256(actual)})"
            )
    return payloads


def default_output(root: Path) -> Path:
    configured = os.environ.get("CRP_RELEASE_OUTPUT")
    if configured:
        return Path(configured)
    return root / "dist" / "release"


def _print_receipt(action: str, output: Path, payloads: dict[str, bytes]) -> None:
    print(f"{action} {len(payloads)} deterministic release files in {output.resolve()}")
    for name, data in sorted(payloads.items()):
        print(f"{sha256(data)}  {len(data):8d}  {name}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="repository root")
    parser.add_argument("--output", type=Path, help="release staging directory")
    parser.add_argument(
        "--verify",
        action="store_true",
        help="verify an existing staging directory without modifying it",
    )
    arguments = parser.parse_args(argv)
    root = arguments.root.resolve()
    output = arguments.output or default_output(root)
    try:
        if arguments.verify:
            payloads = verify_assets(root, output)
            _print_receipt("VERIFIED", output, payloads)
        else:
            payloads = build_assets(root, output)
            _print_receipt("BUILT", output, payloads)
    except (OSError, UnicodeError, ReleaseAssetError) as exc:
        print(f"ERROR release assets: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
