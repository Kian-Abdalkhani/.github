# Shared GitHub community defaults

This public repository provides fallback contribution, support, and issue/PR
guidance for repositories owned by Kian-Abdalkhani. GitHub uses supported defaults
where a repository has no applicable local counterpart. Project-specific guidance
takes precedence, and local issue templates or chooser configuration replace the
shared issue configuration as a set.

| Content | Effect |
| --- | --- |
| Supported community files and templates | GitHub fallback where no local counterpart applies. |
| `.github/workflows/validate.yml` | Validates this repository's files only. |
| `.github/dependabot.yml` | Updates Action references in this repository only. |
| `docs/` | Central reference material available through links. |

## Guidance and templates

- [Contribution guidelines](CONTRIBUTING.md)
- [Support guidance and interim security routing](SUPPORT.md)
- [Issue forms and chooser configuration](.github/ISSUE_TEMPLATE/)
- [Pull request template](PULL_REQUEST_TEMPLATE.md)
- [Default behavior, supported locations, and limits](docs/defaults-and-limits.md)
- [Validation and maintenance](docs/maintaining-this-repository.md)

A shared security policy is pending an owner-selected, monitored private contact.
Until then, follow the affected project's private reporting instructions or its
**Report a vulnerability** control when available. Do not post vulnerability
details in public issues or PRs.

Changes to defaults on `main` can affect applicable owned repositories immediately;
review shared wording before merging. Defaults are surfaced by GitHub, not copied
into other repositories. Workflows, dependency updates, and repository settings do
not inherit from this repository.

See [GitHub's default community health file documentation](https://docs.github.com/en/communities/setting-up-your-project-for-healthy-contributions/creating-a-default-community-health-file)
for the platform's supported behavior.
