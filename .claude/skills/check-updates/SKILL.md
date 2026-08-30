---
name: check-updates
description: Check all Delphi Blocks manifests for available updates on GitHub. Runs the check_updates.py script and presents the results, highlighting which packages have newer releases or commits available. Use when the user says "check updates", "controlla aggiornamenti", "are there updates", "ci sono aggiornamenti", "what's outdated", or "cosa c'è da aggiornare".
---

# Check Updates

Checks all Delphi Blocks manifests in the repository against their GitHub sources to find available updates.

## How it works

Run the script at `tools/check_updates.py` from the repository root:

```
python tools/check_updates.py
```

The script scans all manifests under `.blocks/repository/`, groups them by project id, takes the latest local version, and checks GitHub for:

- **Release-based packages** (repository URL contains `/tree/`): compares against the latest GitHub release tag
- **Commit-based packages** (repository URL contains `/commit/`): checks if there are newer commits on the default branch

## Interpreting the output

The script prints a table with columns: Project, Current version, Latest version, Status.

Status values:
- **Up to date**: the local manifest matches the latest GitHub version
- **UPDATE AVAILABLE**: a newer release exists on GitHub — report the new version and publish date
- **NEWER COMMIT**: for commit-based packages, newer commits exist — report the commit date
- **Could not fetch**: GitHub API call failed (likely rate limiting)

## After running

Present the results to the user in a clear summary. For each package with an available update:
- Name the package and its current vs latest version
- If a release, mention the publish date

If the user wants to update a specific package, suggest using the `/update-manifest` skill.

## Notes

- The script respects the `GITHUB_TOKEN` environment variable to avoid GitHub API rate limits (60 requests/hour without a token)
- The script requires the `packaging` Python library (`pip install packaging`)
- There is a 0.5s delay between API calls to avoid rate limiting
