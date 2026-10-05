#!/usr/bin/env python3
"""Generate and validate JediKit packages using only the Python standard library."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import stat
import sys
import tempfile
import zipfile
from pathlib import Path, PurePosixPath
from typing import Any

SKILL_NAMES = ("jedikit-tasks", "jedikit-habits")
METADATA_FILE = "package-metadata.json"
GENERATED_MANIFESTS = {
    ".claude-plugin/plugin.json": "claude",
    ".codex-plugin/plugin.json": "codex",
    "packages/jedikit/plugin.json": "hermes",
}
COPY_ROOT = Path("packages/jedikit/skills")
ARCHIVE_INPUTS = (
    ("LICENSE", "LICENSE"),
    ("THIRD-PARTY-NOTICES.md", "THIRD-PARTY-NOTICES.md"),
    ("packages/jedikit/plugin.json", "plugin.json"),
    (".claude-plugin/plugin.json", ".claude-plugin/plugin.json"),
    (".codex-plugin/plugin.json", ".codex-plugin/plugin.json"),
    ("skills", "skills"),
)
LINK_RE = re.compile(r"(?<!!)\[[^\]]*\]\((?:<([^>]+)>|([^)]+))\)")
FRONTMATTER_NAME_RE = re.compile(r"^name:\s*['\"]?([^'\"\n]+?)['\"]?\s*$", re.MULTILINE)
FRONTMATTER_DESCRIPTION_RE = re.compile(r"^description:\s*(.+?)\s*$", re.MULTILINE)
ZIP_TIMESTAMP = (1980, 1, 1, 0, 0, 0)
SEMVER_RE = re.compile(
    r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)"
    r"(?:-[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?"
    r"(?:\+[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?$"
)
COMMON_METADATA_KEYS = {
    "name",
    "version",
    "description",
    "author",
    "homepage",
    "repository",
    "license",
    "keywords",
}
PLATFORM_KEYS = {
    "claude": set(),
    "codex": {"skills", "interface"},
    "hermes": {"$schema"},
}


class BuildError(Exception):
    """A repository packaging contract was violated."""


def load_metadata(root: Path) -> dict[str, Any]:
    path = root / METADATA_FILE
    try:
        metadata = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise BuildError(f"missing metadata: {METADATA_FILE}") from exc
    except json.JSONDecodeError as exc:
        raise BuildError(f"invalid JSON in {METADATA_FILE}: {exc}") from exc

    package = metadata.get("package")
    platforms = metadata.get("platforms")
    if not isinstance(package, dict) or not isinstance(platforms, dict):
        raise BuildError(
            "metadata must contain object fields 'package' and 'platforms'"
        )
    required = (
        "name",
        "version",
        "description",
        "author",
        "repository",
        "license",
        "keywords",
    )
    missing = [key for key in required if key not in package]
    if missing:
        raise BuildError(f"metadata package is missing: {', '.join(missing)}")
    for key in ("name", "version", "description", "repository", "license"):
        if not isinstance(package[key], str) or not package[key]:
            raise BuildError(f"metadata package.{key} must be a non-empty string")
    if package["name"] != "jedikit":
        raise BuildError("metadata package.name must remain jedikit")
    if not SEMVER_RE.fullmatch(package["version"]):
        raise BuildError("metadata package.version must be a safe SemVer string")
    author = package["author"]
    if not isinstance(author, dict) or not all(
        isinstance(author.get(key), str) and author[key] for key in ("name", "url")
    ):
        raise BuildError("metadata package.author must contain non-empty name and url")
    keywords = package["keywords"]
    if (
        not isinstance(keywords, list)
        or not keywords
        or not all(isinstance(keyword, str) and keyword for keyword in keywords)
    ):
        raise BuildError("metadata package.keywords must be a non-empty string list")
    if not isinstance(metadata.get("homepage"), str):
        raise BuildError("metadata homepage must be a string")
    for platform in ("claude", "codex", "hermes"):
        additions = platforms.get(platform)
        if not isinstance(additions, dict):
            raise BuildError(f"metadata platforms.{platform} must be an object")
        conflicts = COMMON_METADATA_KEYS & additions.keys()
        if conflicts:
            raise BuildError(
                f"metadata platforms.{platform} overrides common fields: "
                f"{', '.join(sorted(conflicts))}"
            )
        unexpected = additions.keys() - PLATFORM_KEYS[platform]
        missing_platform = PLATFORM_KEYS[platform] - additions.keys()
        if unexpected or missing_platform:
            details = []
            if unexpected:
                details.append(f"unexpected {', '.join(sorted(unexpected))}")
            if missing_platform:
                details.append(f"missing {', '.join(sorted(missing_platform))}")
            raise BuildError(
                f"metadata platforms.{platform} fields are invalid: {'; '.join(details)}"
            )
    codex = platforms["codex"]
    if not isinstance(codex.get("skills"), str):
        raise BuildError("metadata Codex skills path must be a string")
    if not isinstance(codex.get("interface"), dict):
        raise BuildError("metadata platforms.codex.interface must be an object")
    if not isinstance(platforms["hermes"].get("$schema"), str):
        raise BuildError("metadata platforms.hermes.$schema must be a string")
    return metadata


def manifest_for(metadata: dict[str, Any], platform: str) -> dict[str, Any]:
    package = metadata["package"]
    common_before_repository = {
        "name": package["name"],
        "version": package["version"],
        "description": package["description"],
        "author": package["author"],
    }
    common_after_repository = {
        "repository": package["repository"],
        "license": package["license"],
        "keywords": package["keywords"],
    }
    additions = metadata["platforms"][platform]

    if platform == "hermes":
        return {
            "$schema": additions["$schema"],
            **common_before_repository,
            "homepage": metadata["homepage"],
            **common_after_repository,
        }
    if platform == "claude":
        return {
            **common_before_repository,
            "homepage": metadata["homepage"],
            **common_after_repository,
            **additions,
        }
    if platform == "codex":
        return {**common_before_repository, **common_after_repository, **additions}
    raise BuildError(f"unknown platform: {platform}")


def json_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def expected_generated_files(root: Path, metadata: dict[str, Any]) -> dict[Path, bytes]:
    expected = {
        Path(path): json_bytes(manifest_for(metadata, platform))
        for path, platform in GENERATED_MANIFESTS.items()
    }
    skills_root = root / "skills"
    if skills_root.is_symlink() or not skills_root.is_dir():
        raise BuildError("canonical skills root must be a real directory: skills")
    source_entries = {entry.name for entry in skills_root.iterdir()}
    unexpected_entries = source_entries - set(SKILL_NAMES)
    missing_entries = set(SKILL_NAMES) - source_entries
    if unexpected_entries or missing_entries:
        details = []
        if unexpected_entries:
            details.append(f"unexpected {', '.join(sorted(unexpected_entries))}")
        if missing_entries:
            details.append(f"missing {', '.join(sorted(missing_entries))}")
        raise BuildError(f"canonical skills root is invalid: {'; '.join(details)}")
    for skill_name in SKILL_NAMES:
        skill_root = root / "skills" / skill_name
        if skill_root.is_symlink() or not skill_root.is_dir():
            raise BuildError(
                f"canonical skill path must be a real directory: skills/{skill_name}"
            )
        for source in sorted(skill_root.rglob("*")):
            if source.is_symlink():
                raise BuildError(
                    f"symlinks are not allowed in skill packages: {source.relative_to(root)}"
                )
            if source.is_file():
                relative = source.relative_to(root / "skills")
                expected[COPY_ROOT / relative] = source.read_bytes()
    return expected


def generated_copy_files(root: Path) -> set[Path]:
    if not (root / COPY_ROOT).exists():
        return set()
    return {
        path.relative_to(root)
        for path in (root / COPY_ROOT).rglob("*")
        if path.is_file() or path.is_symlink()
    }


def validate_generated_roots(root: Path) -> None:
    for relative in (
        Path(".claude-plugin"),
        Path(".codex-plugin"),
        Path("packages"),
        Path("packages/jedikit"),
        COPY_ROOT,
    ):
        path = root / relative
        if path.is_symlink():
            raise BuildError(f"generated parent must not be a symlink: {relative}")
    hermes_root = root / "packages/jedikit"
    if hermes_root.exists():
        allowed = {"plugin.json", "skills"}
        unexpected = {entry.name for entry in hermes_root.iterdir()} - allowed
        if unexpected:
            raise BuildError(
                "unexpected Hermes package root entry: " + ", ".join(sorted(unexpected))
            )


def validate_frontmatter_and_links(root: Path) -> None:
    for skill_name in SKILL_NAMES:
        skill_root = root / "skills" / skill_name
        skill_file = skill_root / "SKILL.md"
        try:
            text = skill_file.read_text(encoding="utf-8")
        except FileNotFoundError as exc:
            raise BuildError(
                f"missing skill entrypoint: skills/{skill_name}/SKILL.md"
            ) from exc
        if not text.startswith("---\n") or "\n---\n" not in text[4:]:
            raise BuildError(
                f"invalid YAML frontmatter delimiters: skills/{skill_name}/SKILL.md"
            )
        frontmatter = text[4 : text.index("\n---\n", 4)]
        name_match = FRONTMATTER_NAME_RE.search(frontmatter)
        description_match = FRONTMATTER_DESCRIPTION_RE.search(frontmatter)
        if not name_match or name_match.group(1).strip() != skill_name:
            raise BuildError(
                f"frontmatter name must match directory: skills/{skill_name}/SKILL.md"
            )
        if not description_match or not description_match.group(1).strip().strip("'\""):
            raise BuildError(
                f"frontmatter description is required: skills/{skill_name}/SKILL.md"
            )

        for markdown in sorted(skill_root.rglob("*.md")):
            markdown_text = markdown.read_text(encoding="utf-8")
            for angle_target, plain_target in LINK_RE.findall(markdown_text):
                raw_target = angle_target or plain_target
                target = raw_target.strip()
                if not target or target.startswith(
                    ("#", "http://", "https://", "mailto:")
                ):
                    continue
                target = target.split("#", 1)[0]
                resolved = (markdown.parent / target).resolve()
                try:
                    resolved.relative_to(skill_root.resolve())
                except ValueError as exc:
                    raise BuildError(
                        f"local link escapes its skill: {markdown.relative_to(root)} -> {raw_target}"
                    ) from exc
                if not resolved.is_file():
                    raise BuildError(
                        f"broken local link: {markdown.relative_to(root)} -> {raw_target}"
                    )


def validate_generated(root: Path, expected: dict[Path, bytes]) -> None:
    validate_generated_roots(root)
    errors: list[str] = []
    for relative, content in sorted(
        expected.items(), key=lambda item: item[0].as_posix()
    ):
        path = root / relative
        if path.is_symlink():
            errors.append(
                f"generated file must not be a symlink: {relative.as_posix()}"
            )
        elif not path.is_file():
            errors.append(f"missing generated file: {relative.as_posix()}")
        elif path.read_bytes() != content:
            errors.append(f"generated file is stale: {relative.as_posix()}")
    extras = generated_copy_files(root) - {
        path for path in expected if path.is_relative_to(COPY_ROOT)
    }
    errors.extend(
        f"unexpected generated file: {path.as_posix()}" for path in sorted(extras)
    )
    if errors:
        raise BuildError("\n".join(errors))


def write_generated(root: Path, expected: dict[Path, bytes]) -> None:
    validate_generated_roots(root)
    expected_copies = {path for path in expected if path.is_relative_to(COPY_ROOT)}
    for stale in sorted(generated_copy_files(root) - expected_copies, reverse=True):
        (root / stale).unlink()
    for relative, content in expected.items():
        destination = root / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        if destination.is_symlink():
            destination.unlink()
        if not destination.exists() or destination.read_bytes() != content:
            destination.write_bytes(content)
    if (root / COPY_ROOT).exists():
        for directory in sorted((root / COPY_ROOT).rglob("*"), reverse=True):
            if directory.is_dir() and not any(directory.iterdir()):
                directory.rmdir()


def candidate_readme(metadata: dict[str, Any]) -> bytes:
    package = metadata["package"]
    text = f"""# JediKit

{package["description"]}

Included portable skills:

- `jedikit-tasks`
- `jedikit-habits`

Installation and development documentation: {metadata["homepage"]}

License and attribution are provided in `LICENSE` and `THIRD-PARTY-NOTICES.md`.
"""
    return text.encode("utf-8")


def archive_members(root: Path, metadata: dict[str, Any]) -> list[tuple[bytes, str]]:
    members: list[tuple[bytes, str]] = [(candidate_readme(metadata), "README.md")]
    for source_name, archive_name in ARCHIVE_INPUTS:
        source = root / source_name
        if source.is_symlink():
            raise BuildError(f"archive input must not be a symlink: {source_name}")
        if source.is_file():
            members.append((source.read_bytes(), archive_name))
        elif source.is_dir():
            for file_path in sorted(source.rglob("*")):
                if file_path.is_symlink():
                    raise BuildError(
                        f"symlinks are not allowed in archive: {file_path.relative_to(root)}"
                    )
                if file_path.is_file():
                    relative = file_path.relative_to(source).as_posix()
                    members.append(
                        (file_path.read_bytes(), f"{archive_name}/{relative}")
                    )
        else:
            raise BuildError(f"missing archive input: {source_name}")
    return sorted(members, key=lambda item: item[1])


def build_archive(
    root: Path, output: Path, metadata: dict[str, Any]
) -> tuple[Path, Path]:
    output.mkdir(parents=True, exist_ok=True)
    name = metadata["package"]["name"]
    version = metadata["package"]["version"]
    archive_path = output / f"{name}-v{version}-candidate.zip"
    checksum_path = output / f"{archive_path.name}.sha256"
    with tempfile.NamedTemporaryFile(
        dir=output, prefix=".candidate-", suffix=".zip", delete=False
    ) as temp:
        temp_path = Path(temp.name)
    try:
        with zipfile.ZipFile(temp_path, "w", compression=zipfile.ZIP_STORED) as archive:
            for content, archive_name in archive_members(root, metadata):
                info = zipfile.ZipInfo(archive_name, ZIP_TIMESTAMP)
                info.compress_type = zipfile.ZIP_STORED
                info.create_system = 3
                info.external_attr = (stat.S_IFREG | 0o644) << 16
                archive.writestr(info, content, compress_type=zipfile.ZIP_STORED)
        os.replace(temp_path, archive_path)
    finally:
        temp_path.unlink(missing_ok=True)
    digest = hashlib.sha256(archive_path.read_bytes()).hexdigest()
    checksum_path.write_text(f"{digest}  {archive_path.name}\n", encoding="ascii")
    validate_archive(archive_path)
    return archive_path, checksum_path


def validate_archive(path: Path) -> None:
    forbidden_roots = {"research", "evals", ".work", ".git", "dist", "build"}
    with zipfile.ZipFile(path) as archive:
        names = archive.namelist()
        if len(names) != len(set(names)):
            raise BuildError("archive contains duplicate paths")
        for name in names:
            pure = PurePosixPath(name)
            if pure.is_absolute() or ".." in pure.parts:
                raise BuildError(f"unsafe archive path: {name}")
            if pure.parts and pure.parts[0] in forbidden_roots:
                raise BuildError(f"forbidden archive path: {name}")
        required = {
            "plugin.json",
            "README.md",
            ".claude-plugin/plugin.json",
            ".codex-plugin/plugin.json",
            "skills/jedikit-tasks/SKILL.md",
            "skills/jedikit-habits/SKILL.md",
        }
        missing = required - set(names)
        if missing:
            raise BuildError(
                f"archive missing required files: {', '.join(sorted(missing))}"
            )


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="validate tracked generated assets without writing",
    )
    parser.add_argument(
        "--output", type=Path, help="candidate artifact directory (default: build)"
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    root = Path(__file__).resolve().parent.parent
    try:
        metadata = load_metadata(root)
        validate_frontmatter_and_links(root)
        expected = expected_generated_files(root, metadata)
        if args.check:
            validate_generated(root, expected)
            print(
                "build check: generated manifests, Hermes skills, frontmatter, and local links are current"
            )
            return 0
        write_generated(root, expected)
        validate_generated(root, expected)
        output = args.output.resolve() if args.output else root / "build"
        archive, checksum = build_archive(root, output, metadata)
        print(f"built: {archive}")
        print(f"checksum: {checksum}")
        return 0
    except (BuildError, OSError, zipfile.BadZipFile) as exc:
        print(f"build error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
