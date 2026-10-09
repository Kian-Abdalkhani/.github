# Defaults and limits

This public `.github` repository belongs to a personal account, Kian-Abdalkhani.
GitHub can surface its supported community files as defaults for public and
private repositories owned by that account. Repositories owned by organizations
or other people are outside that scope, even if the account contributes to them.
Keep this source repository public and its contents suitable for public use.

## What takes effect

| Content | Effect |
| --- | --- |
| Supported community files and templates | GitHub fallback where no local counterpart applies. |
| `.github/workflows/validate.yml` | Validation for this repository only. |
| `.github/dependabot.yml` | Action dependency updates for this repository only. |
| `docs/` and the root README | Reference material reached through links. |

A project's corresponding local file takes precedence. If it has valid local
issue templates **or local issue-template configuration**, that configuration
replaces the default set; the sets do not merge. Shared changes on the default
branch can affect applicable owned repositories immediately.

Defaults are surfaced in GitHub's interface. They are not copied into another
repository's tracked files, history, clone, or download. Essential instructions
belong in the supported community files themselves; links provide extra context.

## File map

All paths are relative to this repository's root. The repository name `.github`
does not replace the nested directory required for issue forms and automation.

| Community content | Location used here | Status |
| --- | --- | --- |
| Contribution guidelines | `CONTRIBUTING.md` | Included. |
| Support guidance | `SUPPORT.md` | Included. |
| PR template | `PULL_REQUEST_TEMPLATE.md` | Included at its valid root location. |
| Issue forms and chooser | `.github/ISSUE_TEMPLATE/` | Bug, feature, and general forms; blank issues enabled. |
| Security policy | `SECURITY.md` | Deferred until a monitored private contact is chosen. |
| Code of conduct | `CODE_OF_CONDUCT.md` | Deferred until an enforcement policy and private contact are chosen. |
| Accessibility guidance | `ACCESSIBILITY.md` | Optional; omitted initially. |
| Funding destinations | `.github/FUNDING.yml` | Optional; omitted initially. |
| Discussion category forms | `.github/DISCUSSION_TEMPLATE/` | Omitted; depend on enabled Discussions and applicable categories. |
| Private vulnerability report form | `.github/VULNERABILITY_REPORT.yml` | Omitted; depends on private reporting being enabled where used. |

These optional files are supported platform features, not prerequisites for the
initial setup. See GitHub's [supported defaults and locations](https://docs.github.com/en/communities/setting-up-your-project-for-healthy-contributions/creating-a-default-community-health-file)
before adding one. The default forms avoid labels, assignees, projects, and
organization issue types because those are repository-specific dependencies.

## Boundaries

- A shared policy does not enable Issues, Discussions, private vulnerability
  reporting, advisories, scanning, or security alerts. Existing settings determine
  which features are available. No settings on other repositories are changed.
- Branch protections, rulesets, required checks/reviews, labels, secrets, and
  permissions are separate configuration. Community templates do not enforce them.
- Workflows and Dependabot configuration do not inherit. A reusable workflow would
  require an explicit caller; none is included in this initial setup. No generic
  Python/npm CI library or cross-repository automation is installed.
- CODEOWNERS, AGENTS.md, Copilot instructions, editor configuration, lint rules,
  and project READMEs are not supported community-file defaults. Any such files
  added here would concern this repository's own use.
- A license in this repository would concern its own material; it would not
  supply a license to other projects. No license changes are included.
- Shared guidance cannot promise every project is maintained, uses one stack,
  accepts every contribution, or supports the same versions. Project-specific
  support statements take precedence; otherwise maintenance is best effort.

## Personal profile and workflow discovery

`profile/README.md` is an organization-profile feature. A personal profile README
requires a public repository named after the username and a nonempty root README.
The README here describes these shared defaults; no personal-profile repository
is created or edited.

Likewise, GitHub documents custom `workflow-templates/` discovery for organizations.
Even those templates require adoption and do not automatically enforce CI. That
directory is omitted from this personal account's setup.

See [organization profile READMEs](https://docs.github.com/en/organizations/collaborating-with-groups-in-organizations/customizing-your-organizations-profile),
[personal profile requirements](https://docs.github.com/en/account-and-profile/how-tos/profile-customization/managing-your-profile-readme),
and [organization workflow templates](https://docs.github.com/en/actions/how-tos/reuse-automations/create-workflow-templates).
