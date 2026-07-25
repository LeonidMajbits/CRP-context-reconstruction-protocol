from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools import build_release_assets as release_assets
from tools import validate_repository as validator


def block_for_mode(mode: str) -> str:
    fields = [
        "state=active",
        "active=continue the validated task",
        "next_action=perform the next recorded step",
    ]
    mode_fields = {
        "HOT-RESUME": ["last_result=the prior result is stable"],
        "COLD-RESUME": [
            "world=[shared context]",
            "last_result=the prior result is stable",
        ],
        "HANDOFF": [
            "world=[shared context]",
            "constraints=[preserve the contract]",
            "last_result=the prior result is stable",
        ],
        "TRANSPOSE": ["preserve=[working style]", "strip=[stale topic context]"],
        "FORK": ["preserve=[shared base]", "delta_goal=analyze the alternate path"],
        "RECOVERY": ["problem=the prior session drifted", "preserve=[stable state]"],
        "MERGE-NOTE": [
            "lineage=[main, branch-a]",
            "preserve=[validated deltas]",
            "last_result=branch review completed",
        ],
        "CHECKPOINT": ["last_result=the prior result is stable"],
    }
    fields.extend(mode_fields[mode])
    return f"CRP::{mode} | " + " | ".join(fields)


class CrpTextContractTests(unittest.TestCase):
    def test_all_eight_modes_are_accepted(self) -> None:
        for mode in validator.MODES:
            with self.subTest(mode=mode):
                parsed, errors = validator.parse_crp_block(block_for_mode(mode))
                self.assertEqual(errors, [])
                self.assertIsNotNone(parsed)
                self.assertEqual(parsed.mode, mode)

    def test_mode_specific_required_fields_are_enforced(self) -> None:
        cases = {
            "HOT-RESUME": "last_result",
            "COLD-RESUME": "world",
            "HANDOFF": "constraints",
            "TRANSPOSE": "strip",
            "FORK": "delta_goal",
            "RECOVERY": "problem",
            "MERGE-NOTE": "lineage",
            "CHECKPOINT": "last_result",
        }
        for mode, field in cases.items():
            with self.subTest(mode=mode, field=field):
                block = block_for_mode(mode)
                segments = [
                    segment
                    for segment in block.split(" | ")
                    if not segment.startswith(field + "=")
                ]
                _, errors = validator.parse_crp_block(" | ".join(segments))
                self.assertTrue(any(field in error for error in errors), errors)

    def test_global_required_fields_are_enforced(self) -> None:
        for field in validator.GLOBAL_REQUIRED_FIELDS:
            with self.subTest(field=field):
                segments = [
                    segment
                    for segment in block_for_mode("HOT-RESUME").split(" | ")
                    if not segment.startswith(field + "=")
                ]
                _, errors = validator.parse_crp_block(" | ".join(segments))
                self.assertTrue(any(field in error for error in errors), errors)

    def test_unknown_duplicate_and_bad_delimiter_are_rejected(self) -> None:
        base = block_for_mode("HOT-RESUME")
        cases = (
            base + " | mystery=value",
            base + " | state=duplicate",
            base.replace(" | active=", "| active=", 1),
            base + " | tags=[one,,three]",
            base + " | protocol_version=9.9",
        )
        for block in cases:
            with self.subTest(block=block):
                _, errors = validator.parse_crp_block(block)
                self.assertTrue(errors)

    def test_recovery_requires_a_stable_anchor(self) -> None:
        block = (
            "CRP::RECOVERY | state=drifted | active=restore the task | "
            "problem=the session drifted | next_action=resume carefully"
        )
        _, errors = validator.parse_crp_block(block)
        self.assertTrue(any("preserve or last_result" in error for error in errors))

    def test_json_only_fields_are_rejected_in_text(self) -> None:
        base = block_for_mode("HOT-RESUME")
        for field in ("protocol_version=1.0", "extensions=value"):
            with self.subTest(field=field):
                _, errors = validator.parse_crp_block(base + " | " + field)
                self.assertTrue(
                    any("unknown field" in error for error in errors), errors
                )

    def test_text_extensions_are_namespaced_and_unprivileged(self) -> None:
        block = (
            block_for_mode("HOT-RESUME")
            + " | x_vendor.trace=opaque metadata | x_vendor.trace-id=[one, two]"
        )
        _, errors = validator.parse_crp_block(block)
        self.assertEqual(errors, [])

        missing_state = " | ".join(
            segment
            for segment in block_for_mode("HOT-RESUME").split(" | ")
            if not segment.startswith("state=")
        )
        _, errors = validator.parse_crp_block(
            missing_state + " | x_example.state=active"
        )
        self.assertTrue(
            any("missing required fields: state" in error for error in errors)
        )

        _, errors = validator.parse_crp_block(
            block_for_mode("HOT-RESUME") + " | x_=invalid"
        )
        self.assertTrue(any("unknown field" in error for error in errors))

        oversized_name = "x_a." + ("b" * 127)
        _, errors = validator.parse_crp_block(
            block_for_mode("HOT-RESUME") + f" | {oversized_name}=invalid"
        )
        self.assertTrue(any("identifier exceeds" in error for error in errors))

    def test_list_grammar_is_exact_and_bounded(self) -> None:
        valid = block_for_mode("CHECKPOINT") + " | tags=[one, two]"
        _, errors = validator.parse_crp_block(valid)
        self.assertEqual(errors, [])

        invalid_values = (
            "[one,two]",
            "[one, one]",
            "[" + ", ".join(f"item-{index}" for index in range(65)) + "]",
            "[one, [two]]",
            "[" + ("x" * 4097) + "]",
        )
        for value in invalid_values:
            with self.subTest(value=value[:40]):
                _, errors = validator.parse_crp_block(
                    block_for_mode("CHECKPOINT") + f" | tags={value}"
                )
                self.assertTrue(errors)

        scalar_as_list = block_for_mode("CHECKPOINT").replace(
            "active=continue the validated task",
            "active=[one, two]",
        )
        _, errors = validator.parse_crp_block(scalar_as_list)
        self.assertTrue(any("does not permit a list" in error for error in errors))

    def test_documentation_placeholders_require_explicit_template_mode(self) -> None:
        block = "CRP::[MODE] | state=[...] | active=[...] | next_action=[...]"
        _, runtime_errors = validator.parse_crp_block(block)
        self.assertTrue(
            any("placeholder" in error for error in runtime_errors),
            runtime_errors,
        )

        parsed, errors = validator.parse_crp_block(block, allow_placeholders=True)
        self.assertEqual(errors, [])
        self.assertIsNotNone(parsed)
        self.assertEqual(parsed.mode, "[MODE]")

        concrete = (
            "CRP::HOT-RESUME | state=[...] | active=[...] | "
            "last_result=[...] | next_action=[...]"
        )
        _, runtime_errors = validator.parse_crp_block(concrete)
        self.assertTrue(
            any("placeholder" in error for error in runtime_errors),
            runtime_errors,
        )

    def test_noncanonical_outer_and_header_whitespace_is_rejected(self) -> None:
        base = block_for_mode("HOT-RESUME")
        cases = (
            f" {base}",
            f"{base} ",
            base.replace("CRP::HOT-RESUME", "CRP:: HOT-RESUME"),
            base.replace("CRP::HOT-RESUME |", "CRP::HOT-RESUME  |"),
        )
        for block in cases:
            with self.subTest(block=block):
                _, errors = validator.parse_crp_block(block)
                self.assertTrue(errors)

    def test_marker_text_inside_a_value_is_allowed(self) -> None:
        block = block_for_mode("HOT-RESUME").replace(
            "continue the validated task",
            "document CRP::HANDOFF grammar",
        )
        _, errors = validator.parse_crp_block(block)
        self.assertEqual(errors, [])

    def test_text_limit_counts_utf8_bytes(self) -> None:
        block = block_for_mode("HOT-RESUME") + " | x_test.blob=" + ("🔥" * 16_400)
        _, errors = validator.parse_crp_block(block)
        self.assertTrue(any("byte UTF-8 limit" in error for error in errors), errors)

    def test_text_values_reject_controls_and_format_characters(self) -> None:
        for character in (
            "\x00",
            "\t",
            "\u0085",
            "\u009b",
            "\u200b",
            "\u2028",
            "\u2029",
            "\u202e",
            "\ud800",
        ):
            with self.subTest(codepoint=f"U+{ord(character):04X}"):
                block = block_for_mode("HOT-RESUME").replace(
                    "continue the validated task",
                    f"continue{character}the validated task",
                )
                _, errors = validator.parse_crp_block(block)
                self.assertTrue(errors)

    def test_inline_mentions_and_grammar_signatures_are_not_blocks(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            path = root / "docs" / "sample.md"
            report = validator.Report()
            validator.validate_crp_blocks(
                report,
                root,
                {
                    path: (
                        "An inline `CRP::MODE` mention is prose.\n"
                        "CRP::MODE | field=value | field=[item one, item two]\n"
                    )
                },
                "1.0",
            )
            self.assertEqual(report.findings, [])
            self.assertEqual(report.metrics["crp_blocks"], 0)
            self.assertEqual(report.metrics["crp_grammar"], 1)


class StructuredContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.schema = validator.load_json_strict(
            (ROOT / "schema" / "crp.schema.json").read_text(encoding="utf-8")
        )
        validator_class = jsonschema.validators.validator_for(cls.schema)
        validator_class.check_schema(cls.schema)
        cls.schema_validator = validator_class(cls.schema)

    def test_all_eight_structured_modes_are_accepted(self) -> None:
        for mode in validator.MODES:
            with self.subTest(mode=mode):
                sample = validator.build_positive_sample(mode)
                self.assertEqual(list(self.schema_validator.iter_errors(sample)), [])

    def test_structured_negative_cases_are_rejected(self) -> None:
        base = validator.build_positive_sample("HOT-RESUME")
        cases = []
        for field in ("protocol_version", "mode", "state", "active", "next_action"):
            instance = dict(base)
            instance.pop(field, None)
            cases.append((f"missing {field}", instance))
        wrong_version = dict(base)
        wrong_version["protocol_version"] = "9.9"
        cases.append(("wrong version", wrong_version))
        unknown = dict(base)
        unknown["unknown"] = True
        cases.append(("unknown property", unknown))
        empty = dict(base)
        empty["active"] = ""
        cases.append(("empty active", empty))
        empty_extensions = dict(base)
        empty_extensions["extensions"] = {}
        cases.append(("empty extensions", empty_extensions))
        for character in (
            "\x00",
            "\u0085",
            "\u0600",
            "\u200b",
            "\u2028",
            "\u2029",
            "\u202e",
            "\ud800",
        ):
            unsafe = dict(base)
            unsafe["active"] = f"unsafe{character}value"
            cases.append((f"unsafe character U+{ord(character):04X}", unsafe))
        for label, instance in cases:
            with self.subTest(label=label):
                self.assertTrue(list(self.schema_validator.iter_errors(instance)))

    def test_schema_meta_example_and_generated_contract(self) -> None:
        report = validator.Report()
        validator.validate_schema_contract(report, ROOT, "1.0")
        self.assertEqual(report.findings, [])


class FormatAndHygieneTests(unittest.TestCase):
    def test_personal_email_path_comment_and_controls_are_rejected(self) -> None:
        email = "person" + chr(64) + "gmail.com"
        windows_path = "C:" + "\\Users\\person\\private.txt"
        posix_path = "/" + "home/person/private.txt"
        hidden_comment = "<!" + "-- internal --" + ">"
        report = validator.Report()
        validator.scan_text_hygiene(
            report,
            "fixture",
            f"{email}\n{windows_path}\n{posix_path}\n{hidden_comment}\n\u202e",
        )
        messages = "\n".join(finding.message for finding in report.findings)
        self.assertIn("personal email", messages)
        self.assertIn("absolute Windows path", messages)
        self.assertIn("absolute POSIX home path", messages)
        self.assertIn("hidden HTML/XML", messages)
        self.assertIn("bidirectional control", messages)

    def test_decoded_json_escapes_are_scanned(self) -> None:
        value = validator.load_json_strict(
            '{"active":"safe\\u202evalue","note":"person\\u0040gmail.com"}'
        )
        report = validator.Report()
        validator.scan_decoded_value_hygiene(report, "fixture.json", value)
        messages = "\n".join(finding.message for finding in report.findings)
        self.assertIn("bidirectional control", messages)
        self.assertIn("personal email", messages)

    def test_duplicate_json_and_yaml_keys_are_rejected(self) -> None:
        with self.assertRaises(validator.DuplicateKeyError):
            validator.load_json_strict('{"key": 1, "key": 2}')
        with self.assertRaises(validator.DuplicateKeyError):
            validator.load_yaml_strict("key: 1\nkey: 2\n")

    def test_yaml_uses_yaml_12_boolean_rules(self) -> None:
        value = validator.load_yaml_strict("on: push\nenabled: true\n")
        self.assertIn("on", value)
        self.assertIs(value["enabled"], True)

    def test_yaml_anchors_and_excessive_decoded_depth_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            path = root / "anchored.yml"
            text = "base: &base\n  value: safe\ncopy: *base\n"
            report = validator.Report()
            validator.validate_yaml_file(report, root, path, text)
            self.assertTrue(
                any("anchors and aliases" in item.message for item in report.findings)
            )

        nested: object = "leaf"
        for _ in range(validator.MAX_DECODED_DEPTH + 2):
            nested = [nested]
        report = validator.Report()
        validator.scan_decoded_value_hygiene(report, "fixture.json", nested)
        self.assertTrue(
            any("nesting-depth limit" in item.message for item in report.findings)
        )

    def test_markdown_links_and_fences(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            docs = root / "docs"
            docs.mkdir()
            target = docs / "target.md"
            target.write_text("# Target heading\n", encoding="utf-8")
            valid = root / "README.md"
            valid.write_text(
                "# Readme\n\n[Target](docs/target.md#target-heading)\n\n```text\nsafe\n```\n",
                encoding="utf-8",
            )
            report = validator.Report()
            validator.validate_markdown_file(
                report, root, valid, valid.read_text(encoding="utf-8")
            )
            self.assertEqual(report.findings, [])

            broken = root / "broken.md"
            broken.write_text("[Missing](none.md)\n\n```text\n", encoding="utf-8")
            report = validator.Report()
            validator.validate_markdown_file(
                report, root, broken, broken.read_text(encoding="utf-8")
            )
            self.assertGreaterEqual(len(report.findings), 2)

    def test_svg_active_content_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            path = root / "unsafe.svg"
            text = '<svg xmlns="http://www.w3.org/2000/svg"><script>bad</script></svg>'
            report = validator.Report()
            validator.validate_svg_file(report, root, path, text)
            self.assertTrue(
                any("active SVG" in item.message for item in report.findings)
            )

            data_href = (
                '<svg xmlns="http://www.w3.org/2000/svg">'
                '<a href="data:text/html;base64,PHNjcmlwdD4=" /></svg>'
            )
            report = validator.Report()
            validator.validate_svg_file(report, root, path, data_href)
            self.assertTrue(
                any("non-fragment SVG" in item.message for item in report.findings)
            )


class RepositoryAndReleaseTests(unittest.TestCase):
    def test_release_index_boundary_rejects_dirty_private_and_unsafe_inputs(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)

            def git(*arguments: str) -> None:
                subprocess.run(
                    ["git", "-C", str(root), *arguments],
                    check=True,
                    capture_output=True,
                )

            git("init", "--quiet")
            tracked = root / "tracked.txt"
            tracked.write_bytes(b"indexed content\n")
            (root / ".gitignore").write_text(
                ".env\n.crp-private/\n!.env.example\n",
                encoding="utf-8",
            )
            git("add", ".gitignore", "tracked.txt")

            sources = release_assets._indexed_sources(root)
            self.assertEqual(sources["tracked.txt"][1], b"indexed content\n")

            tracked.write_bytes(b"dirty worktree content\n")
            with self.assertRaisesRegex(
                release_assets.ReleaseAssetError,
                "worktree content differs",
            ):
                release_assets._indexed_sources(root)
            tracked.write_bytes(b"indexed content\n")

            private = root / ".env"
            private.write_text("TOKEN=private\n", encoding="utf-8")
            git("add", "--force", ".env")
            with self.assertRaisesRegex(
                release_assets.ReleaseAssetError,
                "ignored or private files are tracked",
            ):
                release_assets._indexed_sources(root)

        unsafe_paths = (
            "../escape",
            "/absolute",
            "dir\\escape",
            "file:stream",
            "bad<name",
            "bad>name",
            'bad"name',
            "bad|name",
            "bad?name",
            "bad*name",
            "CON.txt",
            "trailing.",
            "control\u202ename",
            "non-nfc-e\u0301.txt",
            "dist/generated.txt",
        )
        for path in unsafe_paths:
            with (
                self.subTest(path=path),
                self.assertRaises(release_assets.ReleaseAssetError),
            ):
                release_assets._validate_indexed_path(path)

    def test_history_rejects_a_personal_annotated_tag_identity(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)

            def git(*arguments: str) -> None:
                subprocess.run(
                    ["git", "-C", str(root), *arguments],
                    check=True,
                    capture_output=True,
                )

            git("init", "--quiet")
            git("config", "user.name", "Fixture")
            git(
                "config",
                "user.email",
                "fixture" + chr(64) + "users.noreply.github.com",
            )
            (root / "fixture.txt").write_text("safe\n", encoding="utf-8")
            git("add", "fixture.txt")
            git("commit", "--quiet", "-m", "Fixture")
            personal_email = "tagger" + chr(64) + "gmail.com"
            git(
                "-c",
                "user.email=" + personal_email,
                "tag",
                "--annotate",
                "v0.0.0",
                "--message",
                "Fixture tag",
            )

            report = validator.Report()
            validator.validate_git_history(report, root)
            self.assertTrue(
                any("personal tagger email" in item.message for item in report.findings)
            )

    def test_repository_worktree_is_valid(self) -> None:
        report = validator.Report()
        validator.validate_worktree(report, ROOT)
        self.assertEqual(
            report.findings,
            [],
            "\n".join(
                f"{item.path}:{item.line}: {item.message}" for item in report.findings
            ),
        )

    def test_release_assets_build_and_verify_deterministically(self) -> None:
        private_directory = ROOT / ".crp-private"
        private_directory_already_existed = private_directory.exists()
        private_directory.mkdir(exist_ok=True)
        ignored_fixture = private_directory / "release-bundle-secret-fixture.txt"
        ignored_fixture.write_text(
            "must never enter a release bundle\n", encoding="utf-8"
        )
        with (
            tempfile.TemporaryDirectory() as first,
            tempfile.TemporaryDirectory() as second,
        ):
            try:
                first_output = Path(first)
                second_output = Path(second)
                first_payloads = release_assets.build_assets(ROOT, first_output)
                release_assets.verify_assets(ROOT, first_output)
                second_payloads = release_assets.build_assets(ROOT, second_output)
                release_assets.verify_assets(ROOT, second_output)
                self.assertEqual(first_payloads, second_payloads)
                self.assertEqual(
                    (first_output / release_assets.MANIFEST_NAME).read_bytes(),
                    (second_output / release_assets.MANIFEST_NAME).read_bytes(),
                )
                manifest_lines = (
                    (first_output / release_assets.MANIFEST_NAME)
                    .read_text(encoding="utf-8")
                    .splitlines()
                )
                self.assertEqual(len(manifest_lines), 7)

                bundle = first_output / "crp-1.0.0-bundle.zip"
                with zipfile.ZipFile(bundle) as archive:
                    names = archive.namelist()
                    self.assertEqual(names, sorted(names, key=str.lower))
                    self.assertIn("crp-1.0.0/docs/crp-spec-v1.md", names)
                    self.assertIn("crp-1.0.0/tools/validate_repository.py", names)
                    self.assertNotIn("crp-1.0.0/.git/config", names)
                    self.assertFalse(
                        any("release-bundle-secret-fixture" in name for name in names)
                    )
                    for info in archive.infolist():
                        self.assertEqual(info.date_time, (1980, 1, 1, 0, 0, 0))
                        self.assertEqual(info.compress_type, zipfile.ZIP_STORED)

                standalone_spec = (first_output / "crp-1.0.0-spec.md").read_text(
                    encoding="utf-8"
                )
                self.assertIn(
                    "https://github.com/LeonidMajbits/"
                    "CRP-context-reconstruction-protocol/blob/v1.0.0/"
                    "schema/crp.schema.json",
                    standalone_spec,
                )
            finally:
                ignored_fixture.unlink(missing_ok=True)
                if not private_directory_already_existed:
                    private_directory.rmdir()

    def test_version_surfaces_are_consistent(self) -> None:
        report = validator.Report()
        exact, protocol = validator._parse_version(report, ROOT)
        schema = json.loads(
            (ROOT / "schema" / "crp.schema.json").read_text(encoding="utf-8")
        )
        example = json.loads(
            (ROOT / "schema" / "example-crp.json").read_text(encoding="utf-8")
        )
        validator.validate_version_consistency(
            report, ROOT, exact, protocol, schema, example
        )
        self.assertEqual(report.findings, [])


if __name__ == "__main__":
    unittest.main()
