# Maintaining this repository

Review changes to shared wording carefully before merging to `main`. GitHub uses
the default branch for community defaults, and applicable owned repositories may
surface those changes immediately. See [defaults and limits](defaults-and-limits.md)
for supported inheritance and local overrides.

## Files to maintain

| Files | Purpose |
| --- | --- |
| `README.md`, `docs/` | Scope, reference documentation, and maintenance instructions. |
| `CONTRIBUTING.md`, `SUPPORT.md` | Shared contribution and support guidance. |
| `PULL_REQUEST_TEMPLATE.md` | One generic Markdown PR template. |
| `.github/ISSUE_TEMPLATE/` | Three YAML issue forms and the chooser. |
| `.github/workflows/validate.yml` | Validation in this repository. |
| `.github/dependabot.yml` | Weekly Monday updates for Action references here. |
| `scripts/validate-templates.py` | Offline YAML, form, path, and internal link checks. |
| `scripts/test-validation.py` | Temporary candidate tests for validation failures and recovery. |
| `.markdownlint-cli2.jsonc` | Markdown lint rules for this repository only. |

The old root `ISSUE_TEMPLATE/`, `workflows/`, and `dependabot.yml` paths must stay
absent. The validator rejects them, including empty obsolete directories.

## Run the checks

Use Python 3.12, Node.js 24, and actionlint 1.7.12. From the repository root:

```sh
python -m venv /tmp/github-defaults-venv
. /tmp/github-defaults-venv/bin/activate
python -m pip install 'ruamel.yaml==0.19.1'
python scripts/validate-templates.py
python scripts/test-validation.py
npx --yes markdownlint-cli2@0.23.3 '**/*.md'
actionlint
```

Install actionlint from its [v1.7.12 release](https://github.com/rhysd/actionlint/releases/tag/v1.7.12)
for your platform and place the executable on your PATH. The workflow downloads
the Linux amd64 archive and checks its SHA-256:
`8aca8db96f1b94770f1b0d72b6dddcb1ebb8123cb3712530b08cc387b349a3d8`.
Use the release's checksums for other platforms.

The YAML parser uses YAML 1.2, so workflow `on` keys stay strings. The script
checks required files, duplicate YAML keys, unique form names/IDs/labels, the
Markdown/input/textarea schema used here, boolean required flags, shared metadata,
chooser destinations, workflow permissions/pins, and local links and heading
anchors. Extend its supported schema deliberately if adding other field types.
It checks candidate files, including unpublished central `main` link destinations,
rather than requiring them to exist online before merge.

The failure-case tests copy the candidate into a temporary directory. They verify
malformed YAML, duplicate keys/IDs, missing linked policies, dangling chooser
destinations, missing heading anchors, obsolete paths, repository-specific labels,
and invalid required flags. Corrected content must pass again.

Markdown lint allows long lines (tables and URLs) and a PR template that starts
with a second-level heading. The remaining default rules apply. actionlint checks
workflow syntax and expressions; it also uses ShellCheck when available. All
workflow checks fail the job on errors. External network link checking is optional
and separate from the offline checks.

## Preview without submitting

Before merge, inspect the YAML field order, labels, descriptions, and required
flags in the candidate. Local validation cannot prove GitHub's form rendering.
GitHub currently documents forms as a public preview; recheck its
[form syntax](https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/syntax-for-issue-forms)
and [field schema](https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/syntax-for-githubs-form-schema)
when editing forms.

After the files reach `main`, open the
[new-issue chooser](https://github.com/Kian-Abdalkhani/.github/issues/new/choose).
Confirm the bug, feature, and general categories, the support contact link, and the
blank-issue option. Open each form and check its fields without clicking **Submit
new issue**. A branch or PR alone does not activate defaults in that chooser.

For the PR template, preview the Markdown file, then inspect the populated body on
GitHub's new-PR screen after selecting a comparison with changes. Use the body's
**Preview** tab and leave without clicking **Create pull request**. PR templates
remain Markdown; issue-form YAML does not apply to PRs.

Optionally inspect an existing owned repository with no local counterpart to
confirm fallback display. This is a read-only check; record which file or chooser
was observed. If no suitable repository is available, record that inheritance
was not directly demonstrated. Do not claim all repositories use these defaults.

## Tools, Actions, and Dependabot

Action references use verified full commit SHAs with release comments: checkout
v6.1.0, setup-python v6.3.0, and setup-node v6.5.0. When updating, verify each
release's commit in its upstream repository, review runtime compatibility, and
update the SHA and version comment together. Re-run the checks.

Update ruamel.yaml 0.19.1, markdownlint-cli2 0.23.3, and actionlint 1.7.12 manually
in the workflow, installation guidance, and parser's missing-dependency hint as
appropriate. For actionlint, verify the new release checksum and update it too.
There are no npm/pip package manifests here; running Python or npx alone does not
justify adding those Dependabot ecosystems.

Dependabot checks `.github/workflows/` with `directory: "/"`, opens up to five
Actions update PRs, and does not auto-merge them. It does not update standalone
tool versions in shell commands or dependencies in other repositories. After
merge, inspect **Insights → Dependency graph → Dependabot** for a successful
Actions update check, even if no update PR is needed.

Check the [validation runs](https://github.com/Kian-Abdalkhani/.github/actions/workflows/validate.yml)
after opening a PR and after merge. Add a README badge only after a successful
run. If Actions is disabled or a repository policy blocks tools, these files
cannot override that setting. Private vulnerability reporting also requires
separate settings and is not enabled by a policy file.

## Pending policies and maintenance checklist

`SECURITY.md` and its chooser link are deferred until the owner chooses a real,
monitored private contact. When ready, publish the policy and all security links
together. Include the affected repository/version, impact, reproduction details,
and optional mitigation in private reports. Describe coordinated, best-effort
handling without promising a response deadline, bounty, or guaranteed fix. Update
the interim security routing in SUPPORT, CONTRIBUTING, the forms, and README.

Code of conduct, accessibility/funding guidance, private reporting forms, and
reusable workflows remain optional. Each needs a real use case and its applicable
prerequisites; see [the file map](defaults-and-limits.md#file-map).

When files change:

- Run all documented checks and review the diff for unintended changes or private data.
- Confirm shared instructions fit different project types and local guidance takes precedence.
- Keep inherited links absolute and publish chooser links with their destination files.
- Review successful validation before merge; preview forms and the PR body afterward.
- Inspect Dependabot results and manually maintain standalone tool pins when needed.

No scheduled maintenance, cross-repository writes, or new support commitments are
required by this setup.
