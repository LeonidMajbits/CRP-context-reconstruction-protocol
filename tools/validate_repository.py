#!/usr/bin/env python3
"""Fail-closed validation for the public CRP repository and its reachable history."""

from __future__ import annotations

import argparse
import copy
import json
import re
import subprocess
import sys
import unicodedata
import urllib.parse
import xml.etree.ElementTree as ET
from collections import Counter
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import jsonschema
import yaml
from yaml.constructor import ConstructorError
from yaml.resolver import BaseResolver
from yaml.tokens import AliasToken, AnchorToken

REPOSITORY_URL = "https://github.com/LeonidMajbits/CRP-context-reconstruction-protocol"
SCHEMA_DRAFT = "https://json-schema.org/draft/2020-12/schema"
SEMVER_RE = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")
EMAIL_RE = re.compile(r"\b[A-Z0-9._%+-]+@([A-Z0-9.-]+\.[A-Z]{2,})\b", re.IGNORECASE)
WINDOWS_PATH_RE = re.compile(
    r"(?i)(?<![A-Z0-9])(?:[A-Z]:[\\/](?:[^<>:\"|?*\r\n]+)|"
    r"\\\\[^\\/\s]+[\\/][^\\/\s]+)"
)
POSIX_HOME_PATH_RE = re.compile(r"(?<![A-Za-z0-9])/(?:home|Users)/[^/\s]+(?:/[^\s]*)?")
MARKDOWN_LINK_RE = re.compile(r"!?\[[^\]]*\]\(([^)\r\n]+)\)")
MARKDOWN_REFERENCE_RE = re.compile(r"^\s*\[[^\]]+\]:\s*(\S+)", re.MULTILINE)
FENCE_RE = re.compile(r"^\s*(`{3,}|~{3,})")
CRP_MARKER = "CRP::"
TEXT_EXTENSION_RE = re.compile(r"^x_[a-z][a-z0-9]*(?:[._-][a-z0-9]+)+$")
TEXT_BLOCK_MAX_BYTES = 65_536
TEXT_VALUE_MAX_CODEPOINTS = 4_096
TEXT_LIST_MAX_ITEMS = 64
EXTENSION_IDENTIFIER_MAX_CODEPOINTS = 128
MAX_SOURCE_FILE_BYTES = 1_048_576
MAX_SOURCE_TREE_BYTES = 16_777_216
MAX_SOURCE_FILES = 2_000
MAX_DECODED_DEPTH = 64
MAX_DECODED_NODES = 100_000
GITLEAKS_VERSION = "8.30.1"
GITLEAKS_LINUX_X64_SHA256 = (
    "551f6fc83ea457d62a0d98237cbad105af8d557003051f41f3e7ca7b3f2470eb"
)
COMMENT_OPEN = "<!" + "--"
COMMENT_CLOSE = "--" + ">"

MODES = (
    "HOT-RESUME",
    "COLD-RESUME",
    "HANDOFF",
    "TRANSPOSE",
    "FORK",
    "RECOVERY",
    "MERGE-NOTE",
    "CHECKPOINT",
)
GLOBAL_REQUIRED_FIELDS = frozenset({"state", "active", "next_action"})
MODE_REQUIRED_FIELDS = {
    "HOT-RESUME": frozenset({"last_result"}),
    "COLD-RESUME": frozenset({"world", "last_result"}),
    "HANDOFF": frozenset({"world", "constraints", "last_result"}),
    "TRANSPOSE": frozenset({"preserve", "strip"}),
    "FORK": frozenset({"preserve", "delta_goal"}),
    "RECOVERY": frozenset({"problem"}),
    "MERGE-NOTE": frozenset({"lineage", "preserve", "last_result"}),
    "CHECKPOINT": frozenset({"last_result"}),
}
KNOWN_FIELDS = frozenset(
    {
        "state",
        "world",
        "active",
        "constraints",
        "memory",
        "last_result",
        "next_action",
        "tags",
        "lineage",
        "preserve",
        "strip",
        "delta_goal",
        "problem",
    }
)
ARRAY_CAPABLE_FIELDS = frozenset(
    {"world", "constraints", "memory", "tags", "lineage", "preserve", "strip"}
)
SKIPPED_DIRECTORIES = frozenset(
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
BINARY_SUFFIXES = frozenset(
    {
        ".7z",
        ".bmp",
        ".bz2",
        ".gif",
        ".gz",
        ".ico",
        ".jpeg",
        ".jpg",
        ".pdf",
        ".png",
        ".tar",
        ".webp",
        ".woff",
        ".woff2",
        ".zip",
    }
)
PERSONAL_EMAIL_DOMAINS = frozenset(
    {
        "aol.com",
        "gmail.com",
        "googlemail.com",
        "hotmail.com",
        "icloud.com",
        "live.com",
        "me.com",
        "outlook.com",
        "proton.me",
        "protonmail.com",
        "yahoo.com",
        "ymail.com",
    }
)
BIDI_CODEPOINTS = frozenset(
    {
        0x061C,
        0x200E,
        0x200F,
        0x202A,
        0x202B,
        0x202C,
        0x202D,
        0x202E,
        0x2066,
        0x2067,
        0x2068,
        0x2069,
    }
)
PINNED_ACTIONS = {
    "actions/checkout": "3d3c42e5aac5ba805825da76410c181273ba90b1",
    "actions/setup-python": "5fda3b95a4ea91299a34e894583c3862153e4b97",
    "actions/upload-artifact": "043fb46d1a93c77aae656e7c1c64a875d1fc6a0a",
    "actions/download-artifact": "3e5f45b2cfb9172054b4087a40e8e0b5a5461e7c",
    "actions/attest-build-provenance": "0f67c3f4856b2e3261c31976d6725780e5e4c373",
}


@dataclass(frozen=True, order=True)
class Finding:
    path: str
    line: int
    message: str


class Report:
    """Collect deterministic validation findings instead of failing at the first error."""

    def __init__(self) -> None:
        self.findings: list[Finding] = []
        self.metrics: Counter[str] = Counter()

    def error(self, path: str | Path, message: str, line: int = 0) -> None:
        self.findings.append(Finding(str(path).replace("\\", "/"), line, message))

    def bump(self, metric: str, amount: int = 1) -> None:
        self.metrics[metric] += amount

    @property
    def ok(self) -> bool:
        return not self.findings


@dataclass(frozen=True)
class ParsedBlock:
    mode: str
    fields: dict[str, str]


class DuplicateKeyError(ValueError):
    """Raised when JSON or YAML silently would have overwritten a mapping key."""


class Yaml12SafeLoader(yaml.SafeLoader):
    """Safe PyYAML loader with YAML 1.2 booleans and duplicate-key rejection."""


Yaml12SafeLoader.yaml_implicit_resolvers = copy.deepcopy(
    yaml.SafeLoader.yaml_implicit_resolvers
)
for resolver_key, resolvers in list(Yaml12SafeLoader.yaml_implicit_resolvers.items()):
    Yaml12SafeLoader.yaml_implicit_resolvers[resolver_key] = [
        resolver for resolver in resolvers if resolver[0] != "tag:yaml.org,2002:bool"
    ]
Yaml12SafeLoader.add_implicit_resolver(
    "tag:yaml.org,2002:bool",
    re.compile(r"^(?:true|True|TRUE|false|False|FALSE)$"),
    list("tTfF"),
)


def _construct_unique_mapping(
    loader: Yaml12SafeLoader, node: yaml.nodes.MappingNode, deep: bool = False
) -> dict[Any, Any]:
    loader.flatten_mapping(node)
    mapping: dict[Any, Any] = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        try:
            duplicate = key in mapping
        except TypeError as exc:
            raise ConstructorError(
                "while constructing a mapping",
                node.start_mark,
                "found an unhashable key",
                key_node.start_mark,
            ) from exc
        if duplicate:
            raise DuplicateKeyError(f"duplicate YAML key: {key!r}")
        mapping[key] = loader.construct_object(value_node, deep=deep)
    return mapping


Yaml12SafeLoader.add_constructor(
    BaseResolver.DEFAULT_MAPPING_TAG,
    _construct_unique_mapping,
)


def load_yaml_strict(text: str) -> Any:
    return yaml.load(text, Loader=Yaml12SafeLoader)


def _unique_json_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateKeyError(f"duplicate JSON key: {key!r}")
        result[key] = value
    return result


def load_json_strict(text: str) -> Any:
    return json.loads(text, object_pairs_hook=_unique_json_object)


def _relative(root: Path, path: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return str(path)


def _source_path_problem(path_text: str) -> str | None:
    if (
        not path_text
        or path_text.startswith("/")
        or any(character in path_text for character in '\\:<>"|?*')
    ):
        return "source path is unsafe or non-portable"
    if unicodedata.normalize("NFC", path_text) != path_text:
        return "source path is not Unicode NFC"
    if len(path_text.encode("utf-8")) > 1_024:
        return "source path exceeds 1024 UTF-8 bytes"
    excluded = {part.casefold() for part in SKIPPED_DIRECTORIES}
    for part in path_text.split("/"):
        if not part or part in {".", ".."}:
            return "source path contains an unsafe component"
        if len(part.encode("utf-8")) > 255:
            return "source path component exceeds 255 UTF-8 bytes"
        if part.endswith((" ", ".")):
            return "source path component ends with a dot or space"
        if part.split(".", 1)[0].casefold() in WINDOWS_RESERVED_COMPONENTS:
            return "source path uses a Windows-reserved component"
        if part.casefold() in excluded:
            return "generated or private directory is tracked"
        if any(
            unicodedata.category(character) in {"Cc", "Cf", "Cs", "Zl", "Zp"}
            for character in part
        ):
            return "source path contains an unsafe Unicode character"
    return None


def iter_repository_files(root: Path) -> Iterable[Path]:
    for path in sorted(root.rglob("*"), key=lambda item: item.as_posix().lower()):
        if any(part in SKIPPED_DIRECTORIES for part in path.parts):
            continue
        if path.is_file():
            yield path


def _line_number(text: str, index: int) -> int:
    return text.count("\n", 0, index) + 1


def _is_personal_email(address: str) -> bool:
    domain = address.rsplit("@", 1)[-1].lower()
    return domain in PERSONAL_EMAIL_DOMAINS


def _unsafe_character_message(
    character: str,
    *,
    allow_layout_controls: bool,
) -> str | None:
    codepoint = ord(character)
    if codepoint in BIDI_CODEPOINTS:
        return f"bidirectional control U+{codepoint:04X} is not permitted"
    if unicodedata.category(character) == "Cf":
        return f"Unicode format control U+{codepoint:04X} is not permitted"
    if unicodedata.category(character) in {"Zl", "Zp"}:
        return f"Unicode line or paragraph separator U+{codepoint:04X} is not permitted"
    if unicodedata.category(character) == "Cs":
        return f"Unicode surrogate U+{codepoint:04X} is not permitted"
    allowed_controls = "\t\n\r" if allow_layout_controls else ""
    if unicodedata.category(character) == "Cc" and character not in allowed_controls:
        return f"control character U+{codepoint:04X} is not permitted"
    return None


def scan_text_hygiene(
    report: Report,
    label: str,
    text: str,
    *,
    check_comments: bool = True,
) -> None:
    for match in EMAIL_RE.finditer(text):
        address = match.group(0)
        if _is_personal_email(address):
            report.error(
                label,
                "personal email address is not permitted",
                _line_number(text, match.start()),
            )

    for match in WINDOWS_PATH_RE.finditer(text):
        report.error(
            label,
            "absolute Windows path is not permitted",
            _line_number(text, match.start()),
        )

    for match in POSIX_HOME_PATH_RE.finditer(text):
        report.error(
            label,
            "absolute POSIX home path is not permitted",
            _line_number(text, match.start()),
        )

    if check_comments:
        for marker in (COMMENT_OPEN, COMMENT_CLOSE):
            start = 0
            while True:
                index = text.find(marker, start)
                if index < 0:
                    break
                report.error(
                    label,
                    "hidden HTML/XML source comments are not permitted",
                    _line_number(text, index),
                )
                start = index + len(marker)

    for index, character in enumerate(text):
        message = _unsafe_character_message(
            character,
            allow_layout_controls=True,
        )
        if message:
            report.error(
                label,
                message,
                _line_number(text, index),
            )


def scan_decoded_value_hygiene(
    report: Report,
    label: str,
    value: Any,
    location: str = "$",
    *,
    _depth: int = 0,
    _budget: list[int] | None = None,
    _seen: set[int] | None = None,
) -> None:
    """Scan decoded JSON/YAML strings so escapes cannot bypass public-boundary checks."""

    if _budget is None:
        _budget = [MAX_DECODED_NODES]
    if _seen is None:
        _seen = set()
    _budget[0] -= 1
    if _budget[0] < 0:
        report.error(label, "decoded document exceeds the node limit")
        return
    if _depth > MAX_DECODED_DEPTH:
        report.error(label, f"decoded value {location} exceeds the nesting-depth limit")
        return
    if isinstance(value, str):
        nested = Report()
        scan_text_hygiene(nested, label, value)
        for finding in nested.findings:
            report.error(
                label,
                f"decoded value {location}: {finding.message}",
            )
        return
    if isinstance(value, dict):
        identity = id(value)
        if identity in _seen:
            report.error(label, f"decoded value {location} contains a reference cycle")
            return
        _seen.add(identity)
        for key, child in value.items():
            scan_decoded_value_hygiene(
                report,
                label,
                key,
                f"{location}.<key>",
                _depth=_depth + 1,
                _budget=_budget,
                _seen=_seen,
            )
            scan_decoded_value_hygiene(
                report,
                label,
                child,
                f"{location}.{key}",
                _depth=_depth + 1,
                _budget=_budget,
                _seen=_seen,
            )
        _seen.remove(identity)
        return
    if isinstance(value, list):
        identity = id(value)
        if identity in _seen:
            report.error(label, f"decoded value {location} contains a reference cycle")
            return
        _seen.add(identity)
        for index, child in enumerate(value):
            scan_decoded_value_hygiene(
                report,
                label,
                child,
                f"{location}[{index}]",
                _depth=_depth + 1,
                _budget=_budget,
                _seen=_seen,
            )
        _seen.remove(identity)


def decode_and_scan(
    report: Report,
    label: str,
    data: bytes,
    *,
    check_comments: bool = True,
) -> str | None:
    if data.startswith(b"\xef\xbb\xbf"):
        report.error(label, "UTF-8 BOM is not permitted")
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as exc:
        report.error(label, f"file is not valid UTF-8: {exc}")
        return None
    scan_text_hygiene(report, label, text, check_comments=check_comments)
    return text


def _markdown_headings(text: str) -> set[str]:
    headings: set[str] = set()
    counts: Counter[str] = Counter()
    in_fence = False
    fence_character = ""
    fence_length = 0
    for line in text.splitlines():
        fence = FENCE_RE.match(line)
        if fence:
            marker = fence.group(1)
            if not in_fence:
                in_fence = True
                fence_character = marker[0]
                fence_length = len(marker)
            elif marker[0] == fence_character and len(marker) >= fence_length:
                in_fence = False
            continue
        if in_fence:
            continue
        match = re.match(r"^\s{0,3}#{1,6}\s+(.+?)\s*#*\s*$", line)
        if not match:
            continue
        heading = match.group(1).lower().strip()
        heading = re.sub(r"[^\w\s-]", "", heading, flags=re.UNICODE)
        heading = re.sub(r"\s+", "-", heading)
        heading = re.sub(r"-+", "-", heading).strip("-")
        suffix = counts[heading]
        counts[heading] += 1
        headings.add(heading if suffix == 0 else f"{heading}-{suffix}")
    return headings


def _link_destination(raw: str) -> str:
    raw = raw.strip()
    if raw.startswith("<") and ">" in raw:
        return raw[1 : raw.index(">")]
    return raw.split(maxsplit=1)[0]


def validate_markdown_file(report: Report, root: Path, path: Path, text: str) -> None:
    label = _relative(root, path)
    in_fence = False
    fence_character = ""
    fence_length = 0
    opening_line = 0
    for line_number, line in enumerate(text.splitlines(), start=1):
        match = FENCE_RE.match(line)
        if not match:
            continue
        marker = match.group(1)
        if not in_fence:
            in_fence = True
            fence_character = marker[0]
            fence_length = len(marker)
            opening_line = line_number
        elif marker[0] == fence_character and len(marker) >= fence_length:
            in_fence = False
    if in_fence:
        report.error(label, "unclosed Markdown code fence", opening_line)

    targets = [match.group(1) for match in MARKDOWN_LINK_RE.finditer(text)]
    targets.extend(match.group(1) for match in MARKDOWN_REFERENCE_RE.finditer(text))
    for raw_target in targets:
        target = _link_destination(raw_target)
        if not target:
            report.error(label, "empty Markdown link target")
            continue
        if re.match(r"^[A-Za-z][A-Za-z0-9+.-]*:", target) or target.startswith("//"):
            continue
        decoded = urllib.parse.unquote(target)
        path_part, separator, fragment = decoded.partition("#")
        destination = path if not path_part else (path.parent / path_part)
        resolved = destination.resolve()
        try:
            resolved.relative_to(root.resolve())
        except ValueError:
            report.error(label, f"local link escapes repository: {target}")
            continue
        if not resolved.exists():
            report.error(label, f"broken local link: {target}")
            continue
        if (
            separator
            and fragment
            and resolved.is_file()
            and resolved.suffix.lower() == ".md"
        ):
            try:
                destination_text = resolved.read_text(encoding="utf-8")
            except (OSError, UnicodeError) as exc:
                report.error(label, f"cannot inspect Markdown anchor {target}: {exc}")
                continue
            if fragment.lower() not in _markdown_headings(destination_text):
                report.error(label, f"broken local Markdown anchor: {target}")
        report.bump("markdown_links")


def validate_json_file(report: Report, root: Path, path: Path, text: str) -> Any:
    label = _relative(root, path)
    try:
        value = load_json_strict(text)
    except (json.JSONDecodeError, DuplicateKeyError, RecursionError) as exc:
        report.error(label, f"invalid JSON: {exc}")
        return None
    scan_decoded_value_hygiene(report, label, value)
    report.bump("json_files")
    return value


def validate_yaml_file(report: Report, root: Path, path: Path, text: str) -> Any:
    label = _relative(root, path)
    try:
        if any(
            isinstance(token, (AliasToken, AnchorToken)) for token in yaml.scan(text)
        ):
            report.error(label, "YAML anchors and aliases are not permitted")
            return None
        value = load_yaml_strict(text)
    except (yaml.YAMLError, DuplicateKeyError, RecursionError) as exc:
        report.error(label, f"invalid YAML: {exc}")
        return None
    if value is None:
        report.error(label, "YAML document must not be empty")
    else:
        scan_decoded_value_hygiene(report, label, value)
    report.bump("yaml_files")
    return value


def validate_svg_file(report: Report, root: Path, path: Path, text: str) -> None:
    label = _relative(root, path)
    if re.search(r"<!\s*(?:DOCTYPE|ENTITY)\b", text, re.IGNORECASE):
        report.error(label, "DOCTYPE and ENTITY declarations are not permitted")
    try:
        document = ET.fromstring(text)
    except ET.ParseError as exc:
        report.error(label, f"invalid SVG XML: {exc}")
        return
    if document.tag.rsplit("}", 1)[-1].lower() != "svg":
        report.error(label, "SVG document must have an svg root element")
    for element in document.iter():
        local_name = element.tag.rsplit("}", 1)[-1].lower()
        if local_name in {"script", "foreignobject"}:
            report.error(label, f"active SVG element is not permitted: {local_name}")
        for attribute, value in element.attrib.items():
            local_attribute = attribute.rsplit("}", 1)[-1].lower()
            if local_attribute.startswith("on"):
                report.error(
                    label, f"SVG event attribute is not permitted: {local_attribute}"
                )
            if local_attribute == "href":
                normalized = value.strip().lower()
                if normalized and not normalized.startswith("#"):
                    report.error(
                        label, f"non-fragment SVG reference is not permitted: {value}"
                    )
    report.bump("svg_files")


def _validate_text_value(
    key: str,
    value: str,
    *,
    is_extension: bool,
    allow_placeholders: bool,
    errors: list[str],
) -> None:
    """Validate one text-profile value without granting extensions core semantics."""

    if not value:
        errors.append(f"empty field value: {key}")
        return
    if "\n" in value or "\r" in value or "|" in value:
        errors.append(f"field value contains a reserved delimiter: {key}")
    for character in value:
        message = _unsafe_character_message(
            character,
            allow_layout_controls=False,
        )
        if message:
            errors.append(f"{key}: {message}")

    if value == "[...]":
        if not allow_placeholders:
            errors.append(f"documentation placeholder is not a runtime value: {key}")
        return

    if value.startswith("["):
        if not value.endswith("]"):
            errors.append(f"unclosed bracketed value: {key}")
            return
        if key not in ARRAY_CAPABLE_FIELDS and not is_extension:
            errors.append(f"field does not permit a list value: {key}")

        inner = value[1:-1]
        if not inner:
            errors.append(f"empty bracketed value: {key}")
            return
        if "[" in inner or "]" in inner:
            errors.append(f"nested brackets are not permitted: {key}")

        if "," in inner and not re.fullmatch(r"[^,]+(?:, [^,]+)*", inner):
            errors.append(f"list items must use the exact comma-space delimiter: {key}")
        items = inner.split(", ")
        if not 1 <= len(items) <= TEXT_LIST_MAX_ITEMS:
            errors.append(
                f"list must contain between 1 and {TEXT_LIST_MAX_ITEMS} items: {key}"
            )
        if len(items) != len(set(items)):
            errors.append(f"list items must be unique: {key}")
        for item in items:
            if not item or not item.strip():
                errors.append(f"list contains an empty item: {key}")
                continue
            if item != item.strip():
                errors.append(f"list item spacing is not canonical: {key}")
            if len(item) > TEXT_VALUE_MAX_CODEPOINTS:
                errors.append(
                    f"list item exceeds the {TEXT_VALUE_MAX_CODEPOINTS}-code-point limit: {key}"
                )
            if any(delimiter in item for delimiter in (",", "|", "[", "]", "\n", "\r")):
                errors.append(f"list item contains a reserved delimiter: {key}")
        return

    if "[" in value or "]" in value:
        errors.append(f"unbalanced bracket in field value: {key}")
    if len(value) > TEXT_VALUE_MAX_CODEPOINTS:
        errors.append(
            f"field value exceeds the {TEXT_VALUE_MAX_CODEPOINTS}-code-point limit: {key}"
        )
    if key == "state" and not re.fullmatch(r"[a-z][a-z0-9._-]{0,63}", value):
        errors.append("state must be a lowercase token of at most 64 characters")


def parse_crp_block(
    block: str,
    protocol_version: str = "1.0",
    *,
    allow_placeholders: bool = False,
) -> tuple[ParsedBlock | None, list[str]]:
    errors: list[str] = []
    candidate = block
    if candidate != candidate.strip():
        errors.append("leading or trailing whitespace is not canonical")
        candidate = candidate.strip()
    try:
        encoded_length = len(candidate.encode("utf-8"))
    except UnicodeEncodeError:
        encoded_length = 0
        errors.append("block contains a surrogate and is not valid UTF-8 text")
    if encoded_length > TEXT_BLOCK_MAX_BYTES:
        errors.append(f"block exceeds the {TEXT_BLOCK_MAX_BYTES}-byte UTF-8 limit")
    if "\n" in candidate or "\r" in candidate:
        errors.append("block must be a single line")
    if not candidate.startswith(CRP_MARKER):
        return None, ["block must begin with the CRP:: marker"]
    if "|" in candidate and len(candidate.split(" | ")) != candidate.count("|") + 1:
        errors.append("field delimiters must use exactly one space around |")
    parts = candidate.split(" | ")
    header = parts[0]
    mode = header[len(CRP_MARKER) :]
    if not re.fullmatch(r"CRP::(?:[A-Z][A-Z-]*|\[MODE\])", header):
        errors.append("header must use the exact CRP::MODE form")
    if mode == "[MODE]" and not allow_placeholders:
        errors.append("documentation mode placeholder is not valid at runtime")
    elif mode != "[MODE]" and mode not in MODES:
        errors.append(f"unknown mode: {mode!r}")

    fields: dict[str, str] = {}
    for segment in parts[1:]:
        if "=" not in segment:
            errors.append(f"field segment has no equals sign: {segment!r}")
            continue
        key, value = segment.split("=", 1)
        if key != key.strip() or value != value.strip():
            errors.append(f"field spacing is not canonical: {segment!r}")
        key = key.strip()
        value = value.strip()
        is_extension = bool(TEXT_EXTENSION_RE.fullmatch(key))
        if not re.fullmatch(r"[a-z][a-z0-9_]*", key) and not is_extension:
            errors.append(f"invalid field name: {key!r}")
            continue
        if (
            is_extension
            and len(key.removeprefix("x_")) > EXTENSION_IDENTIFIER_MAX_CODEPOINTS
        ):
            errors.append(
                "extension identifier exceeds the "
                f"{EXTENSION_IDENTIFIER_MAX_CODEPOINTS}-code-point limit: {key}"
            )
        if key in fields:
            errors.append(f"duplicate field: {key}")
            continue
        fields[key] = value
        if key not in KNOWN_FIELDS and not is_extension:
            errors.append(f"unknown field: {key}")
        _validate_text_value(
            key,
            value,
            is_extension=is_extension,
            allow_placeholders=allow_placeholders,
            errors=errors,
        )

    extension_count = sum(bool(TEXT_EXTENSION_RE.fullmatch(key)) for key in fields)
    if extension_count > 32:
        errors.append("text profile permits at most 32 extension fields")

    required = set(GLOBAL_REQUIRED_FIELDS)
    if mode in MODE_REQUIRED_FIELDS:
        required.update(MODE_REQUIRED_FIELDS[mode])
    missing = sorted(required.difference(fields))
    if missing:
        errors.append("missing required fields: " + ", ".join(missing))
    if mode == "RECOVERY" and not ({"preserve", "last_result"} & fields.keys()):
        errors.append("RECOVERY requires either preserve or last_result")
    return ParsedBlock(mode=mode, fields=fields), errors


def _is_crp_content_path(path: Path) -> bool:
    return path.suffix.lower() == ".md"


def validate_crp_blocks(
    report: Report, root: Path, text_files: dict[Path, str], protocol_version: str
) -> None:
    for path, text in text_files.items():
        if not _is_crp_content_path(path):
            continue
        label = _relative(root, path)
        relative = path.relative_to(root)
        allow_placeholders = (
            bool(relative.parts and relative.parts[0] == "templates")
            or relative.as_posix() == "reference/quickstart.md"
        )
        for line_number, line in enumerate(text.splitlines(), start=1):
            stripped = line.strip()
            if not stripped.startswith(CRP_MARKER):
                continue
            block = line
            if re.match(r"^CRP::MODE(?:\s+\||$)", block):
                report.bump("crp_grammar")
                continue
            _, errors = parse_crp_block(
                block,
                protocol_version,
                allow_placeholders=allow_placeholders,
            )
            for error in errors:
                report.error(label, f"invalid CRP block: {error}", line_number)
            report.bump("crp_blocks")


def build_positive_sample(mode: str, protocol_version: str = "1.0") -> dict[str, Any]:
    sample: dict[str, Any] = {
        "protocol_version": protocol_version,
        "mode": mode,
        "state": "active",
        "active": "continue the validated task",
        "next_action": "perform the next recorded step",
    }
    field_values: dict[str, Any] = {
        "world": ["shared project context"],
        "constraints": ["preserve the validated contract"],
        "last_result": "the previous result was validated",
        "preserve": ["stable state"],
        "strip": ["stale state"],
        "delta_goal": "evaluate the branch-specific change",
        "problem": "the prior session drifted",
        "lineage": ["main@checkpoint"],
    }
    for field in MODE_REQUIRED_FIELDS[mode]:
        sample[field] = field_values[field]
    if mode == "RECOVERY":
        sample["preserve"] = field_values["preserve"]
    return sample


def _schema_errors(
    validator: jsonschema.protocols.Validator, instance: Any
) -> list[str]:
    return [error.message for error in validator.iter_errors(instance)]


def validate_schema_contract(
    report: Report, root: Path, protocol_version: str
) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    schema_path = root / "schema" / "crp.schema.json"
    example_path = root / "schema" / "example-crp.json"
    try:
        schema = load_json_strict(schema_path.read_text(encoding="utf-8"))
        example = load_json_strict(example_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError, DuplicateKeyError) as exc:
        report.error("schema", f"cannot load schema contract: {exc}")
        return None, None

    if schema.get("$schema") != SCHEMA_DRAFT:
        report.error("schema/crp.schema.json", f"$schema must be {SCHEMA_DRAFT}")
    schema_id = schema.get("$id")
    if not isinstance(schema_id, str) or not schema_id.startswith("https://"):
        report.error(
            "schema/crp.schema.json", "$id must be an absolute HTTPS identifier"
        )
    if schema.get("additionalProperties") is not False:
        report.error(
            "schema/crp.schema.json", "top-level additionalProperties must be false"
        )

    properties = schema.get("properties")
    if not isinstance(properties, dict):
        report.error("schema/crp.schema.json", "properties must be an object")
        return schema, example
    protocol_property = properties.get("protocol_version", {})
    if protocol_property.get("const") != protocol_version:
        report.error(
            "schema/crp.schema.json",
            f"protocol_version const must be {protocol_version!r}",
        )
    extensions_property = properties.get("extensions")
    if (
        not isinstance(extensions_property, dict)
        or extensions_property.get("type") != "object"
    ):
        report.error(
            "schema/crp.schema.json", "extensions must be defined as an object"
        )
    required = schema.get("required", [])
    for field in ("protocol_version", "mode", "state", "active", "next_action"):
        if field not in required:
            report.error("schema/crp.schema.json", f"required must include {field}")

    mode_enum = properties.get("mode", {}).get("enum")
    if mode_enum != list(MODES):
        report.error(
            "schema/crp.schema.json", "mode enum must match the eight v1 modes"
        )

    try:
        validator_class = jsonschema.validators.validator_for(schema)
        validator_class.check_schema(schema)
        validator = validator_class(schema)
    except jsonschema.exceptions.SchemaError as exc:
        report.error(
            "schema/crp.schema.json", f"invalid meta-schema conformance: {exc.message}"
        )
        return schema, example

    example_errors = _schema_errors(validator, example)
    for message in example_errors:
        report.error("schema/example-crp.json", f"schema validation failed: {message}")

    for mode in MODES:
        positive = build_positive_sample(mode, protocol_version)
        errors = _schema_errors(validator, positive)
        for message in errors:
            report.error(
                "schema/crp.schema.json", f"{mode} positive case failed: {message}"
            )

        for field in sorted(GLOBAL_REQUIRED_FIELDS):
            negative = dict(positive)
            negative.pop(field, None)
            if not _schema_errors(validator, negative):
                report.error(
                    "schema/crp.schema.json",
                    f"{mode} accepts missing globally required field {field}",
                )
        for field in sorted(MODE_REQUIRED_FIELDS[mode]):
            negative = dict(positive)
            negative.pop(field, None)
            if mode == "RECOVERY" and field != "problem":
                continue
            if not _schema_errors(validator, negative):
                report.error(
                    "schema/crp.schema.json",
                    f"{mode} accepts missing mode-required field {field}",
                )
        if mode == "RECOVERY":
            negative = dict(positive)
            negative.pop("preserve", None)
            negative.pop("last_result", None)
            if not _schema_errors(validator, negative):
                report.error(
                    "schema/crp.schema.json",
                    "RECOVERY accepts an object without preserve or last_result",
                )

    base = build_positive_sample("HOT-RESUME", protocol_version)
    negative_cases: list[tuple[str, dict[str, Any]]] = []
    wrong_version = dict(base)
    wrong_version["protocol_version"] = "9.9"
    negative_cases.append(("wrong protocol version", wrong_version))
    unknown_mode = dict(base)
    unknown_mode["mode"] = "UNKNOWN"
    negative_cases.append(("unknown mode", unknown_mode))
    unknown_property = dict(base)
    unknown_property["unexpected"] = "not allowed"
    negative_cases.append(("unknown top-level property", unknown_property))
    empty_state = dict(base)
    empty_state["state"] = ""
    negative_cases.append(("empty state", empty_state))
    oversized_state = dict(base)
    oversized_state["state"] = "x" * 100_000
    negative_cases.append(("oversized state", oversized_state))
    empty_constraints = build_positive_sample("HANDOFF", protocol_version)
    empty_constraints["constraints"] = []
    negative_cases.append(("empty constraints array", empty_constraints))
    for label, instance in negative_cases:
        if not _schema_errors(validator, instance):
            report.error(
                "schema/crp.schema.json", f"schema accepts negative case: {label}"
            )

    extension_case = dict(base)
    extension_case["extensions"] = {"example.value": "value"}
    for message in _schema_errors(validator, extension_case):
        report.error(
            "schema/crp.schema.json", f"extensions object was rejected: {message}"
        )

    empty_extensions = dict(base)
    empty_extensions["extensions"] = {}
    if not _schema_errors(validator, empty_extensions):
        report.error(
            "schema/crp.schema.json",
            "schema accepts negative case: empty extensions object",
        )
    oversized_extension = dict(base)
    oversized_extension["extensions"] = {"a." + ("b" * 127): "value"}
    if not _schema_errors(validator, oversized_extension):
        report.error(
            "schema/crp.schema.json",
            "schema accepts an oversized extension identifier",
        )
    report.bump("schema_negative_cases")
    report.bump("schema_positive_cases", len(MODES))
    report.bump("schema_negative_cases", len(negative_cases))
    return schema, example


def _parse_version(report: Report, root: Path) -> tuple[str, str]:
    path = root / "VERSION"
    try:
        version = path.read_text(encoding="utf-8").strip()
    except (OSError, UnicodeError) as exc:
        report.error("VERSION", f"cannot read version: {exc}")
        return "", ""
    match = SEMVER_RE.fullmatch(version)
    if not match:
        report.error("VERSION", "version must be a stable semantic version")
        return version, ""
    return version, f"{match.group(1)}.{match.group(2)}"


def validate_version_consistency(
    report: Report,
    root: Path,
    exact_version: str,
    protocol_version: str,
    schema: dict[str, Any] | None,
    example: dict[str, Any] | None,
) -> None:
    if not exact_version or not protocol_version:
        return
    try:
        citation = load_yaml_strict((root / "CITATION.cff").read_text(encoding="utf-8"))
    except (OSError, UnicodeError, yaml.YAMLError, DuplicateKeyError) as exc:
        report.error("CITATION.cff", f"cannot validate citation version: {exc}")
    else:
        if (
            not isinstance(citation, dict)
            or str(citation.get("version")) != exact_version
        ):
            report.error("CITATION.cff", f"version must be {exact_version}")
        if citation.get("repository-code") != REPOSITORY_URL:
            report.error(
                "CITATION.cff", "repository-code must use the canonical repository URL"
            )

    if schema is not None:
        actual = schema.get("properties", {}).get("protocol_version", {}).get("const")
        if actual != protocol_version:
            report.error(
                "schema/crp.schema.json", f"protocol version must be {protocol_version}"
            )
    if example is not None and example.get("protocol_version") != protocol_version:
        report.error(
            "schema/example-crp.json", f"protocol_version must be {protocol_version}"
        )

    required_markers = {
        "README.md": re.compile(
            rf"^- Specification version: \*\*{re.escape(exact_version)}\*\*\s*$",
            re.MULTILINE,
        ),
        "docs/crp-spec-v1.md": re.compile(
            rf"^# Context Reconstruction Protocol Specification v{re.escape(exact_version)}\s*$",
            re.MULTILINE,
        ),
        "docs/crp-paper.md": re.compile(
            rf"^\*\*Specification version:\*\*\s+{re.escape(exact_version)}\s*$",
            re.MULTILINE,
        ),
        "CHANGELOG.md": re.compile(
            rf"^## \[?{re.escape(exact_version)}\]?(?:\s+-\s+\d{{4}}-\d{{2}}-\d{{2}})?\s*$",
            re.MULTILINE,
        ),
    }
    for relative, pattern in required_markers.items():
        try:
            text = (root / relative).read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            report.error(relative, f"cannot validate version marker: {exc}")
            continue
        if not pattern.search(text):
            report.error(
                relative, f"missing version marker consistent with {exact_version}"
            )
    report.bump("version_surfaces", len(required_markers) + 3)


def _iter_action_uses(value: Any) -> Iterable[Any]:
    if isinstance(value, dict):
        for key, child in value.items():
            if key == "uses":
                yield child
            else:
                yield from _iter_action_uses(child)
    elif isinstance(value, list):
        for child in value:
            yield from _iter_action_uses(child)


def _job_run_text(job: Any) -> str:
    if not isinstance(job, dict):
        return ""
    steps = job.get("steps", [])
    if not isinstance(steps, list):
        return ""
    return "\n".join(
        step.get("run", "")
        for step in steps
        if isinstance(step, dict) and isinstance(step.get("run"), str)
    )


def _job_uses_action(job: Any, action: str) -> bool:
    if not isinstance(job, dict):
        return False
    return any(
        isinstance(value, str) and value.startswith(action + "@")
        for value in _iter_action_uses(job)
    )


def _validate_full_history_gitleaks_job(
    report: Report,
    label: str,
    workflow: dict[str, Any],
    job: Any,
) -> None:
    if not isinstance(job, dict):
        report.error(label, "a dedicated Gitleaks job is required")
        return
    environment = workflow.get("env", {})
    if not isinstance(environment, dict):
        environment = {}
    if str(environment.get("GITLEAKS_VERSION")) != GITLEAKS_VERSION:
        report.error(label, f"Gitleaks version must be pinned to {GITLEAKS_VERSION}")
    if str(environment.get("GITLEAKS_LINUX_X64_SHA256")) != GITLEAKS_LINUX_X64_SHA256:
        report.error(
            label, "Gitleaks Linux archive checksum is not the approved digest"
        )
    run_text = _job_run_text(job)
    required_fragments = {
        "official pinned Gitleaks archive": (
            "github.com/gitleaks/gitleaks/releases/download/"
        ),
        "archive checksum verification": "sha256sum --check",
        "full reachable-history scan": '--log-opts="--all"',
        "redacted findings": "--redact",
    }
    for contract, fragment in required_fragments.items():
        if fragment not in run_text:
            report.error(label, f"Gitleaks job lacks {contract}")


def validate_workflow_contract(
    report: Report, root: Path, yaml_documents: dict[Path, Any]
) -> None:
    workflow_path = root / ".github" / "workflows" / "validation.yml"
    document = yaml_documents.get(workflow_path)
    if not isinstance(document, dict):
        report.error(
            ".github/workflows/validation.yml",
            "validation workflow is missing or invalid",
        )
        return
    permissions = document.get("permissions")
    if permissions != {"contents": "read"}:
        report.error(
            ".github/workflows/validation.yml",
            "workflow permissions must be exactly contents: read",
        )
    triggers = document.get("on")
    if isinstance(triggers, dict) and "pull_request_target" in triggers:
        report.error(
            ".github/workflows/validation.yml", "pull_request_target is not permitted"
        )

    for path, workflow in yaml_documents.items():
        if ".github/workflows" not in path.as_posix() or not isinstance(workflow, dict):
            continue
        label = _relative(root, path)
        jobs = workflow.get("jobs", {})
        if not isinstance(jobs, dict):
            report.error(label, "workflow jobs must be a mapping")
            continue
        for job_name, job in jobs.items():
            if not isinstance(job, dict):
                report.error(label, f"job {job_name} must be a mapping")
                continue
            runner = job.get("runs-on")
            runner_values = runner if isinstance(runner, list) else [runner]
            if any(str(value).lower() == "self-hosted" for value in runner_values):
                report.error(label, f"job {job_name} must not use a self-hosted runner")
        for value in _iter_action_uses(workflow):
            if not isinstance(value, str):
                report.error(label, "action reference must be a string")
                continue
            if value.startswith("./"):
                continue
            if "@" not in value or "/" not in value:
                report.error(label, f"invalid action reference: {value}")
                continue
            action, reference = value.rsplit("@", 1)
            if not re.fullmatch(r"[0-9a-f]{40}", reference):
                report.error(label, f"action is not pinned to a full commit: {value}")
                continue
            expected = PINNED_ACTIONS.get(action)
            if expected is None:
                report.error(
                    label, f"action is not on the approved allowlist: {action}"
                )
            elif reference != expected:
                report.error(label, f"action uses an unapproved commit: {action}")

    jobs = document.get("jobs", {})
    matrix_job = jobs.get("validate") if isinstance(jobs, dict) else None
    validation_gitleaks_job = jobs.get("gitleaks") if isinstance(jobs, dict) else None
    _validate_full_history_gitleaks_job(
        report,
        ".github/workflows/validation.yml",
        document,
        validation_gitleaks_job,
    )
    if not isinstance(matrix_job, dict):
        report.error(
            ".github/workflows/validation.yml", "validate matrix job is required"
        )
    else:
        matrix = matrix_job.get("strategy", {}).get("matrix", {})
        if set(matrix.get("os", [])) != {"ubuntu-latest", "windows-latest"}:
            report.error(
                ".github/workflows/validation.yml",
                "validation matrix must cover Ubuntu and Windows",
            )
        if {str(value) for value in matrix.get("python-version", [])} != {
            "3.10",
            "3.14",
        }:
            report.error(
                ".github/workflows/validation.yml",
                "validation matrix must cover Python 3.10 and 3.14",
            )
    aggregate = jobs.get("validation") if isinstance(jobs, dict) else None
    if not isinstance(aggregate, dict) or aggregate.get("name") != "Validation":
        report.error(
            ".github/workflows/validation.yml",
            "stable aggregate job named Validation is required",
        )
    else:
        needs = aggregate.get("needs", [])
        if isinstance(needs, str):
            needs = [needs]
        if set(needs) != {"validate", "gitleaks"}:
            report.error(
                ".github/workflows/validation.yml",
                "Validation gate must depend on validate and gitleaks",
            )
        if "always()" not in str(aggregate.get("if", "")):
            report.error(
                ".github/workflows/validation.yml",
                "Validation gate must evaluate with always()",
            )

    release_path = root / ".github" / "workflows" / "release.yml"
    release_document = yaml_documents.get(release_path)
    if not isinstance(release_document, dict):
        report.error(
            ".github/workflows/release.yml", "release workflow is missing or invalid"
        )
    else:
        if release_document.get("permissions") != {"contents": "read"}:
            report.error(
                ".github/workflows/release.yml",
                "release workflow default permissions must be exactly contents: read",
            )
        release_trigger = release_document.get("on")
        if (
            not isinstance(release_trigger, dict)
            or set(release_trigger) != {"push"}
            or release_trigger.get("push", {}).get("tags") != ["v*"]
        ):
            report.error(
                ".github/workflows/release.yml",
                "release publication must be triggered only by a v* tag push",
            )
        release_jobs = release_document.get("jobs", {})
        resolve_job = (
            release_jobs.get("resolve") if isinstance(release_jobs, dict) else None
        )
        release_validate_job = (
            release_jobs.get("validate") if isinstance(release_jobs, dict) else None
        )
        release_job = (
            release_jobs.get("release") if isinstance(release_jobs, dict) else None
        )
        release_gitleaks_job = (
            release_jobs.get("gitleaks") if isinstance(release_jobs, dict) else None
        )
        _validate_full_history_gitleaks_job(
            report,
            ".github/workflows/release.yml",
            release_document,
            release_gitleaks_job,
        )
        expected_release_permissions = {
            "contents": "write",
            "id-token": "write",
            "attestations": "write",
            "artifact-metadata": "write",
        }
        if not isinstance(resolve_job, dict):
            report.error(
                ".github/workflows/release.yml",
                "release workflow must resolve one immutable source commit",
            )
        else:
            resolve_run = _job_run_text(resolve_job)
            if "merge-base --is-ancestor" not in resolve_run:
                report.error(
                    ".github/workflows/release.yml",
                    "release source must be constrained to main ancestry",
                )
            if "GITHUB_REF" not in resolve_run or "GITHUB_SHA" not in resolve_run:
                report.error(
                    ".github/workflows/release.yml",
                    "release attestation identity must be bound to the resolved tag and commit",
                )
            if "verify-tag" not in resolve_run or "release-signers" not in resolve_run:
                report.error(
                    ".github/workflows/release.yml",
                    "release tags must be verified against the approved SSH signer",
                )
            outputs = resolve_job.get("outputs", {})
            if not isinstance(outputs, dict) or set(outputs) != {
                "commit",
                "tag_object",
            }:
                report.error(
                    ".github/workflows/release.yml",
                    "release source resolver must output the commit and tag-object SHAs",
                )
        if not isinstance(release_validate_job, dict):
            report.error(
                ".github/workflows/release.yml",
                "release validation job is required",
            )
        else:
            validate_needs = release_validate_job.get("needs", [])
            if isinstance(validate_needs, str):
                validate_needs = [validate_needs]
            if set(validate_needs) != {"resolve"}:
                report.error(
                    ".github/workflows/release.yml",
                    "release validation must depend on the resolved source",
                )
            if not _job_uses_action(release_validate_job, "actions/upload-artifact"):
                report.error(
                    ".github/workflows/release.yml",
                    "validated release inputs must be uploaded for promotion",
                )
        if not isinstance(release_job, dict):
            report.error(".github/workflows/release.yml", "release job is required")
        else:
            if release_job.get("environment") != "release":
                report.error(
                    ".github/workflows/release.yml",
                    "release publication must use the protected release environment",
                )
            release_needs = release_job.get("needs", [])
            if isinstance(release_needs, str):
                release_needs = [release_needs]
            if set(release_needs) != {"resolve", "validate", "gitleaks"}:
                report.error(
                    ".github/workflows/release.yml",
                    "release publication must depend on resolve, validation, and Gitleaks",
                )
            if not _job_uses_action(release_job, "actions/download-artifact"):
                report.error(
                    ".github/workflows/release.yml",
                    "release job must download the validated inputs",
                )
            if not _job_uses_action(release_job, "actions/attest-build-provenance"):
                report.error(
                    ".github/workflows/release.yml",
                    "release inputs must receive a provenance attestation",
                )
            release_run = _job_run_text(release_job)
            if (
                "Remote release tag moved after validation" not in release_run
                or "Remote release tag object moved after validation" not in release_run
                or "verify-tag refs/tags/crp-release-publish" not in release_run
            ):
                report.error(
                    ".github/workflows/release.yml",
                    "release job must reverify and reject a tag object that moved",
                )
        if isinstance(release_job, dict) and (
            release_job.get("permissions") != expected_release_permissions
        ):
            report.error(
                ".github/workflows/release.yml",
                "release job permissions do not match the minimal publication set",
            )
        if isinstance(release_gitleaks_job, dict):
            gitleaks_needs = release_gitleaks_job.get("needs", [])
            if isinstance(gitleaks_needs, str):
                gitleaks_needs = [gitleaks_needs]
            if set(gitleaks_needs) != {"resolve"}:
                report.error(
                    ".github/workflows/release.yml",
                    "release Gitleaks scan must use the resolved source",
                )
    report.bump("workflow_contracts")


def _mandatory_paths() -> tuple[str, ...]:
    return (
        ".editorconfig",
        ".gitattributes",
        ".github/dependabot.yml",
        ".github/ISSUE_TEMPLATE/config.yml",
        ".github/pull_request_template.md",
        ".github/release-signers",
        ".github/workflows/release.yml",
        ".github/workflows/validation.yml",
        "CITATION.cff",
        "LICENSE",
        "README.md",
        "SECURITY.md",
        "VERSION",
        "requirements-dev.in",
        "requirements-dev.txt",
        "schema/crp.schema.json",
        "schema/example-crp.json",
        "tests/test_repository.py",
        "tools/build_release_assets.py",
        "tools/validate_repository.py",
    )


def validate_git_index_boundary(report: Report, root: Path) -> None:
    try:
        ignored_output = _run_git(
            root,
            ["ls-files", "--cached", "--ignored", "--exclude-standard", "-z"],
            binary=True,
        )
        index_output = _run_git(
            root,
            ["ls-files", "--cached", "--stage", "-z"],
            binary=True,
        )
    except (OSError, RuntimeError, subprocess.TimeoutExpired) as exc:
        report.error("git:index", f"cannot inspect Git index boundary: {exc}")
        return
    assert isinstance(ignored_output, bytes)
    assert isinstance(index_output, bytes)
    for raw_path in (item for item in ignored_output.split(b"\0") if item):
        path_text = raw_path.decode("utf-8", errors="backslashreplace")
        report.error(
            f"git:index:{path_text}",
            "ignored or private file is tracked",
        )

    collision_keys: dict[str, str] = {}
    for record in (item for item in index_output.split(b"\0") if item):
        metadata, separator, raw_path = record.partition(b"\t")
        fields = metadata.split()
        if not separator or len(fields) != 3:
            report.error("git:index", "unexpected Git index record")
            continue
        mode_text, _, stage = fields
        if stage != b"0":
            report.error("git:index", "unmerged index entry is not permitted")
            continue
        try:
            path_text = raw_path.decode("utf-8")
        except UnicodeDecodeError:
            report.error("git:index", "indexed source path is not UTF-8")
            continue
        problem = _source_path_problem(path_text)
        if problem:
            report.error(f"git:index:{path_text}", problem)
        try:
            mode = int(mode_text, 8)
        except ValueError:
            report.error(f"git:index:{path_text}", "invalid Git index mode")
            continue
        if mode not in {0o100644, 0o100755}:
            report.error(
                f"git:index:{path_text}",
                "tracked source is not a regular file",
            )
        collision_key = path_text.casefold()
        previous = collision_keys.get(collision_key)
        if previous is not None:
            report.error(
                f"git:index:{path_text}",
                f"case-insensitive path collision with {previous}",
            )
        else:
            collision_keys[collision_key] = path_text
        report.bump("indexed_paths")


def validate_worktree(report: Report, root: Path) -> None:
    root = root.resolve()
    for relative in _mandatory_paths():
        if not (root / relative).is_file():
            report.error(relative, "required repository file is missing")

    validate_git_index_boundary(report, root)
    text_files: dict[Path, str] = {}
    source_file_count = 0
    source_tree_bytes = 0
    worktree_collision_keys: dict[str, str] = {}
    for path in iter_repository_files(root):
        label = _relative(root, path)
        problem = _source_path_problem(label)
        if problem:
            report.error(label, problem)
            continue
        collision_key = label.casefold()
        previous = worktree_collision_keys.get(collision_key)
        if previous is not None:
            report.error(label, f"case-insensitive path collision with {previous}")
            continue
        worktree_collision_keys[collision_key] = label
        if path.is_symlink():
            report.error(label, "symbolic links are not permitted")
            continue
        try:
            size = path.stat().st_size
        except OSError as exc:
            report.error(label, f"cannot inspect file size: {exc}")
            continue
        source_file_count += 1
        source_tree_bytes += size
        if source_file_count > MAX_SOURCE_FILES:
            report.error("repository", "source tree exceeds the file-count limit")
            break
        if source_tree_bytes > MAX_SOURCE_TREE_BYTES:
            report.error("repository", "source tree exceeds the total-byte limit")
            break
        if size > MAX_SOURCE_FILE_BYTES:
            report.error(
                label,
                f"source file exceeds the {MAX_SOURCE_FILE_BYTES}-byte limit",
            )
            continue
        report.bump("files")
        if path.suffix.lower() in BINARY_SUFFIXES:
            report.error(
                label,
                "binary and archive files are not permitted in the public source tree",
            )
            report.bump("binary_files")
            continue
        try:
            data = path.read_bytes()
        except OSError as exc:
            report.error(label, f"cannot read file: {exc}")
            continue
        text = decode_and_scan(report, label, data)
        if text is None:
            continue
        text_files[path] = text

    yaml_documents: dict[Path, Any] = {}
    for path, text in text_files.items():
        suffix = path.suffix.lower()
        if suffix == ".md":
            validate_markdown_file(report, root, path, text)
        elif suffix == ".json":
            validate_json_file(report, root, path, text)
        elif suffix in {".yaml", ".yml", ".cff"}:
            yaml_documents[path] = validate_yaml_file(report, root, path, text)
        elif suffix == ".svg":
            validate_svg_file(report, root, path, text)

    exact_version, protocol_version = _parse_version(report, root)
    validate_crp_blocks(report, root, text_files, protocol_version or "1.0")
    schema, example = validate_schema_contract(report, root, protocol_version or "1.0")
    validate_version_consistency(
        report, root, exact_version, protocol_version, schema, example
    )
    validate_workflow_contract(report, root, yaml_documents)


def _run_git(root: Path, arguments: list[str], *, binary: bool = False) -> str | bytes:
    completed = subprocess.run(
        ["git", "-c", "core.quotePath=false", "-C", str(root), *arguments],
        check=False,
        capture_output=True,
        text=not binary,
        timeout=60,
    )
    if completed.returncode != 0:
        stderr = completed.stderr
        if isinstance(stderr, bytes):
            stderr = stderr.decode("utf-8", errors="replace")
        raise RuntimeError(stderr.strip() or f"git exited with {completed.returncode}")
    return completed.stdout


def validate_git_history(report: Report, root: Path) -> None:
    if not (root / ".git").exists():
        report.error("git", "reachable-history validation requires a Git checkout")
        return
    try:
        metadata = _run_git(root, ["log", "--all", "--format=%H%x00%aE%x00%cE"])
    except (OSError, RuntimeError, subprocess.TimeoutExpired) as exc:
        report.error("git", f"cannot inspect commit identities: {exc}")
        return
    assert isinstance(metadata, str)
    for line in metadata.splitlines():
        parts = line.split("\x00")
        if len(parts) != 3:
            report.error("git", "unexpected commit metadata format")
            continue
        commit, author_email, committer_email = parts
        for role, address in (("author", author_email), ("committer", committer_email)):
            if _is_personal_email(address):
                report.error(
                    f"git:{commit}",
                    f"personal {role} email address is reachable in public history",
                )
        report.bump("commits")

    try:
        tag_metadata = _run_git(
            root,
            [
                "for-each-ref",
                "refs/tags",
                "--format=%(objecttype)%00%(objectname)%00%(taggeremail)",
            ],
        )
    except (OSError, RuntimeError, subprocess.TimeoutExpired) as exc:
        report.error("git", f"cannot inspect tag identities: {exc}")
        return
    assert isinstance(tag_metadata, str)
    for line in tag_metadata.splitlines():
        parts = line.split("\x00")
        if len(parts) != 3:
            report.error("git", "unexpected tag metadata format")
            continue
        object_type, object_id, tagger_email = parts
        if object_type != "tag":
            report.error(f"git:{object_id}", "reachable tag is not annotated")
            continue
        match = EMAIL_RE.search(tagger_email)
        if match is None:
            report.error(f"git:{object_id}", "annotated tag is missing a tagger email")
        elif _is_personal_email(match.group(0)):
            report.error(
                f"git:{object_id}",
                "personal tagger email address is reachable in public history",
            )
        report.bump("tags")

    try:
        object_lines = _run_git(root, ["rev-list", "--objects", "--all"])
    except (OSError, RuntimeError, subprocess.TimeoutExpired) as exc:
        report.error("git", f"cannot enumerate reachable objects: {exc}")
        return
    assert isinstance(object_lines, str)
    seen: set[tuple[str, str]] = set()
    for line in object_lines.splitlines():
        if " " not in line:
            continue
        object_id, path_text = line.split(" ", 1)
        key = (object_id, path_text)
        if key in seen:
            continue
        seen.add(key)
        try:
            object_type = _run_git(root, ["cat-file", "-t", object_id])
            if not isinstance(object_type, str) or object_type.strip() != "blob":
                continue
            path_problem = _source_path_problem(path_text)
            if path_problem:
                report.error(f"git:{object_id}:{path_text}", path_problem)
                continue
            if Path(path_text).suffix.lower() in BINARY_SUFFIXES:
                report.error(
                    f"git:{object_id}:{path_text}",
                    "binary or archive blob is reachable in public history",
                )
                continue
            object_size = _run_git(root, ["cat-file", "-s", object_id])
            if not isinstance(object_size, str):
                raise TypeError("unexpected object-size response")
            if int(object_size.strip()) > MAX_SOURCE_FILE_BYTES:
                report.error(
                    f"git:{object_id}:{path_text}",
                    f"history blob exceeds the {MAX_SOURCE_FILE_BYTES}-byte limit",
                )
                continue
            content = _run_git(root, ["cat-file", "blob", object_id], binary=True)
        except (OSError, RuntimeError, ValueError, subprocess.TimeoutExpired) as exc:
            report.error(
                f"git:{object_id}:{path_text}", f"cannot inspect history blob: {exc}"
            )
            continue
        assert isinstance(content, bytes)
        decode_and_scan(report, f"git:{object_id}:{path_text}", content)
        report.bump("history_blobs")


def format_summary(report: Report) -> str:
    metrics = ", ".join(
        f"{key}={value}" for key, value in sorted(report.metrics.items())
    )
    return metrics or "no metrics"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="repository root")
    parser.add_argument(
        "--worktree-only",
        action="store_true",
        help="skip reachable Git history while preparing a clean-history replacement",
    )
    arguments = parser.parse_args(argv)
    root = arguments.root.resolve()
    report = Report()
    try:
        validate_worktree(report, root)
        if not arguments.worktree_only:
            validate_git_history(report, root)
    # Deliberately fail closed on any unexpected validator defect.
    except Exception as exc:  # noqa: BLE001  # pragma: no cover
        report.error(
            "validator", f"unexpected validator failure: {type(exc).__name__}: {exc}"
        )

    for finding in sorted(set(report.findings)):
        location = (
            finding.path if finding.line <= 0 else f"{finding.path}:{finding.line}"
        )
        print(f"ERROR {location}: {finding.message}")
    if report.ok:
        print(f"PASS CRP repository validation ({format_summary(report)})")
        return 0
    print(
        f"FAIL CRP repository validation: {len(set(report.findings))} finding(s) "
        f"({format_summary(report)})"
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())
