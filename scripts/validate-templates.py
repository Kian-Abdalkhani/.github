#!/usr/bin/env python3
"""Validate this repository's YAML, issue forms, layout, and local links offline."""

import argparse
import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit

try:
    from ruamel.yaml import YAML
    from ruamel.yaml.error import YAMLError
except ImportError:
    sys.exit("Install the parser first: python -m pip install 'ruamel.yaml==0.19.1'")


CENTRAL_PATH = "/Kian-Abdalkhani/.github/"
FORMS = (
    ".github/ISSUE_TEMPLATE/01-bug-report.yml",
    ".github/ISSUE_TEMPLATE/02-feature-request.yml",
    ".github/ISSUE_TEMPLATE/03-general-issue.yml",
)
REQUIRED_FILES = (
    "README.md", "PULL_REQUEST_TEMPLATE.md", "CONTRIBUTING.md", "SUPPORT.md",
    "docs/defaults-and-limits.md", "docs/maintaining-this-repository.md",
    "scripts/validate-templates.py", "scripts/test-validation.py",
    ".github/ISSUE_TEMPLATE/config.yml", ".github/dependabot.yml",
    ".github/workflows/validate.yml", *FORMS,
)
EXCLUDED = {".git", ".venv", "node_modules", "__pycache__"}
LINK = re.compile(r"\[[^\]\n]*\]\(\s*(<[^>]+>|[^\s)]+)(?:\s+\"[^\"]*\")?\s*\)")


def strings(value):
    """Yield string values from YAML mappings and sequences."""
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for child in value.values():
            yield from strings(child)
    elif isinstance(value, list):
        for child in value:
            yield from strings(child)


def prose(text):
    """Exclude fenced code and HTML comments from Markdown link checks."""
    text = re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)
    lines = []
    fence = None
    for line in text.splitlines():
        match = re.match(r"^\s{0,3}(`{3,}|~{3,})", line)
        if match:
            marker = match.group(1)
            if fence is None:
                fence = marker
            elif marker[0] == fence[0] and len(marker) >= len(fence):
                fence = None
        elif fence is None:
            lines.append(line)
    return "\n".join(lines)


def anchors(path):
    """Collect GitHub-style anchors for the ordinary headings used here."""
    found = set()
    counts = {}
    for heading in re.findall(r"^#{1,6}\s+(.+?)\s*#*\s*$", prose(path.read_text()), re.MULTILINE):
        heading = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", heading)
        slug = re.sub(r"[^\w\- ]", "", heading.lower()).replace(" ", "-")
        count = counts.get(slug, 0)
        counts[slug] = count + 1
        found.add(f"{slug}-{count}" if count else slug)
    return found


def validate(root):
    errors = []

    def fail(path, message):
        errors.append(f"{path}: {message}")

    for name in REQUIRED_FILES:
        if not (root / name).is_file():
            fail(name, "required file is missing")
    for name in ("ISSUE_TEMPLATE", "workflows", "dependabot.yml"):
        if (root / name).exists():
            fail(name, "obsolete root path; use the nested .github directory")

    files = sorted(
        path for path in root.rglob("*")
        if path.is_file() and not EXCLUDED.intersection(path.relative_to(root).parts)
    )
    documents = {}
    for path in files:
        if path.suffix not in {".yml", ".yaml"}:
            continue
        parser = YAML(typ="safe", pure=True)
        parser.version = (1, 2)  # Keep workflow `on` as a string, not a YAML 1.1 boolean.
        parser.allow_duplicate_keys = False
        try:
            document = parser.load(path.read_text())
            documents[path.relative_to(root).as_posix()] = document
            if not isinstance(document, dict):
                fail(path.relative_to(root), "YAML document must be a mapping")
        except (YAMLError, ValueError) as error:
            fail(path.relative_to(root), f"invalid YAML: {error}")

    names = set()
    template_dir = root / ".github/ISSUE_TEMPLATE"
    for path in sorted(template_dir.glob("*")):
        if path.name == "config.yml" or not path.is_file():
            continue
        name = path.relative_to(root).as_posix()
        if path.suffix not in {".yml", ".yaml"}:
            fail(name, "use YAML issue forms rather than duplicate Markdown templates")
            continue
        if name not in documents:
            continue
        form = documents[name]
        if not isinstance(form, dict):
            fail(name, "form must be a mapping")
            continue
        unknown = set(form) - {"name", "description", "title", "body"}
        if unknown:
            fail(name, f"unsupported shared form metadata: {sorted(map(str, unknown))}")
        for key in ("name", "description"):
            if not isinstance(form.get(key), str) or not form[key].strip():
                fail(name, f"{key} must be a nonempty string")
        if "title" in form and not isinstance(form["title"], str):
            fail(name, "title must be a string")
        if isinstance(form.get("name"), str):
            if form["name"] in names:
                fail(name, "duplicate form name")
            names.add(form["name"])
        body = form.get("body")
        if not isinstance(body, list) or not body:
            fail(name, "body must be a nonempty array")
            continue
        ids, labels = set(), set()
        responses = 0
        for index, field in enumerate(body):
            location = f"{name} body[{index}]"
            if not isinstance(field, dict):
                fail(location, "field must be a mapping")
                continue
            if set(field) - {"type", "id", "attributes", "validations"}:
                fail(location, "unknown field keys")
            kind = field.get("type")
            if not isinstance(kind, str) or kind not in {"markdown", "input", "textarea"}:
                fail(location, "validator supports markdown, input, and textarea fields")
                continue
            attributes = field.get("attributes")
            if not isinstance(attributes, dict):
                fail(location, "attributes must be a mapping")
                continue
            allowed = {"value"} if kind == "markdown" else {"label", "description", "placeholder", "value"}
            if kind == "textarea":
                allowed.add("render")
            if set(attributes) - allowed:
                fail(location, "unknown attributes for this field type")
            if any(not isinstance(value, str) for value in attributes.values()):
                fail(location, "attributes must have string values")
            if kind == "markdown":
                if not isinstance(attributes.get("value"), str) or not attributes["value"].strip():
                    fail(location, "markdown requires a nonempty value")
                if "id" in field or "validations" in field:
                    fail(location, "markdown cannot have an id or validations")
                continue
            responses += 1
            field_id = field.get("id")
            if not isinstance(field_id, str) or not re.fullmatch(r"[A-Za-z0-9_-]+", field_id):
                fail(location, "response field needs an id containing letters, digits, - or _")
            elif field_id in ids:
                fail(location, f"duplicate field id: {field_id}")
            else:
                ids.add(field_id)
            label = attributes.get("label")
            if not isinstance(label, str) or not label.strip():
                fail(location, "response field needs a nonempty label")
            elif label in labels:
                fail(location, f"duplicate field label: {label}")
            else:
                labels.add(label)
            if "validations" in field:
                validations = field["validations"]
                if (not isinstance(validations, dict) or set(validations) != {"required"}
                        or not isinstance(validations.get("required"), bool)):
                    fail(location, "validations must contain a boolean required value")
        if not responses:
            fail(name, "form needs at least one response field")

    def check_link(source, url, inherited=False):
        url = url.strip("<>")
        parsed = urlsplit(url)
        relative = not parsed.scheme and not parsed.netloc
        if parsed.netloc == "github.com" and parsed.path.startswith(CENTRAL_PATH):
            tail = parsed.path[len(CENTRAL_PATH):]
            if tail.startswith(("blob/main/", "tree/main/")):
                target = root / unquote(tail.split("/", 2)[2])
            else:
                return  # Repository features such as /issues are not local files.
        elif relative:
            if inherited and parsed.path:
                fail(source, f"inherited guidance needs an absolute central link: {url}")
            target = root / source.parent / unquote(parsed.path) if parsed.path else root / source
        else:
            return  # External network checks are deliberately optional.
        target = target.resolve()
        if not target.is_relative_to(root):
            fail(source, f"link escapes the repository: {url}")
        elif not target.exists():
            fail(source, f"missing link target: {url}")
        elif parsed.fragment and target.is_file() and target.suffix == ".md":
            if unquote(parsed.fragment) not in anchors(target):
                fail(source, f"missing heading anchor: {url}")

    chooser = documents.get(".github/ISSUE_TEMPLATE/config.yml")
    if chooser is not None:
        if not isinstance(chooser, dict) or chooser.get("blank_issues_enabled") is not True:
            fail(".github/ISSUE_TEMPLATE/config.yml", "keep blank_issues_enabled: true")
        else:
            if set(chooser) - {"blank_issues_enabled", "contact_links"}:
                fail(".github/ISSUE_TEMPLATE/config.yml", "unknown chooser keys")
            contacts = chooser.get("contact_links")
            if not isinstance(contacts, list) or not contacts:
                fail(".github/ISSUE_TEMPLATE/config.yml", "contact_links must be a nonempty array")
            else:
                for contact in contacts:
                    if (not isinstance(contact, dict) or set(contact) != {"name", "url", "about"}
                            or any(not isinstance(v, str) or not v.strip() for v in contact.values())):
                        fail(".github/ISSUE_TEMPLATE/config.yml", "contacts need name, url, and about strings")
                    elif urlsplit(contact["url"]).scheme != "https":
                        fail(".github/ISSUE_TEMPLATE/config.yml", "contact URLs must use HTTPS")
                    else:
                        check_link(Path(".github/ISSUE_TEMPLATE/config.yml"), contact["url"])

    dependabot = documents.get(".github/dependabot.yml")
    if dependabot is not None:
        if not isinstance(dependabot, dict) or dependabot.get("version") != 2:
            fail(".github/dependabot.yml", "Dependabot requires version: 2")
        else:
            updates = dependabot.get("updates")
            if (not isinstance(updates, list) or len(updates) != 1
                    or not isinstance(updates[0], dict)
                    or updates[0].get("package-ecosystem") != "github-actions"
                    or updates[0].get("directory") != "/"):
                fail(".github/dependabot.yml", "configure only github-actions at directory /")

    workflow = documents.get(".github/workflows/validate.yml")
    if workflow is not None:
        if not isinstance(workflow, dict) or not isinstance(workflow.get("on"), dict):
            fail(".github/workflows/validate.yml", "workflow must preserve the on event mapping")
        else:
            if set(workflow["on"]) != {"push", "pull_request", "workflow_dispatch"}:
                fail(".github/workflows/validate.yml", "use push, pull_request, and workflow_dispatch events")
            if workflow.get("permissions") != {"contents": "read"}:
                fail(".github/workflows/validate.yml", "workflow requires only contents: read")
    for name, document in documents.items():
        if name.startswith(".github/workflows/"):
            for value in strings(document):
                if re.match(r"^[\w.-]+/[\w./-]+@", value) and not re.fullmatch(r"[^@]+@[0-9a-f]{40}", value):
                    fail(name, f"Action reference must use a full commit SHA: {value}")

    for path in files:
        source = path.relative_to(root)
        inherited = source.as_posix() in {"CONTRIBUTING.md", "SUPPORT.md", "SECURITY.md"} or source.as_posix() in FORMS
        if path.suffix == ".md":
            values = [prose(path.read_text())]
        elif source.as_posix() in documents:
            values = strings(documents[source.as_posix()])
        else:
            continue
        for value in values:
            for match in LINK.finditer(value):
                check_link(source, match.group(1), inherited)
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1],
                        help="candidate repository root (defaults to this script's repository)")
    root = parser.parse_args().root.resolve()
    if not root.is_dir():
        sys.exit(f"Repository root is not a directory: {root}")
    errors = validate(root)
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print("Validated YAML, issue forms, chooser, workflow policy, paths, and internal links.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
