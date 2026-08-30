---
name: update-manifest
description: Update a Delphi Blocks manifest to a newer GitHub release or commit. Give it a project name (e.g. "SVGIconImageList", "delphi-neon", or the full id like "EtheaDev.SVGIconImageList") and it checks for a newer version on GitHub, verifies packages and source paths, and creates the new manifest file. Use when the user says "update manifest", "aggiorna manifest", "nuova versione", "new version", "bump", or names a repository to update.
---

# Update Manifest

This skill updates a Delphi Blocks package manifest to a newer version from GitHub.

## Input

The user provides a project identifier — one of:
- The manifest `id` (e.g. `EtheaDev.SVGIconImageList`)
- The project `name` (e.g. `SVGIconImageList`)
- The GitHub repo name (e.g. `SVGIconImageList`, `delphi-neon`)
- An owner/repo pair (e.g. `EtheaDev/SVGIconImageList`)

Optionally the user can specify a target version. If not specified, use the latest GitHub release.

## Procedure

Follow these steps in order. Do NOT skip verification steps.

### 1. Find the current manifest

Scan `.blocks/repository/` for all `*.manifest.json` files. Match the user's input against the `id`, `name`, or repository URL fields. If multiple projects match, ask the user to clarify.

Group all versions of the matched project and identify the **latest version** (by semantic version comparison).

### 2. Check GitHub for a newer version

Read the current manifest's `repository.url` to determine the GitHub owner/repo.

- **Release-based** (URL contains `/tree/`): fetch the latest release from GitHub. Compare the release tag against the current manifest version. If no newer version exists, tell the user and stop.
- **Commit-based** (URL contains `/commit/`): fetch the latest commit on the default branch. If it differs from the current commit, report it. Ask the user what version string to use for the new manifest.

If the user specified a target version, use that instead of the latest.

### 3. Verify packages

Fetch the `Packages/` directory listing from the GitHub tag/commit for the **newest Delphi version folder** available (e.g. `D13`, `D12`). List all `.dpk` files found there.

Compare against the current manifest's `packages` array:
- Every runtime and designtime package in the manifest must exist as a `.dpk` in the repo
- Every `.dpk` in the repo should be accounted for in the manifest
- If there are differences, report them and ask the user how to proceed

### 4. Verify source paths

For each path listed in `platforms.*.sourcePath`, verify the directory exists in the GitHub tree at the target version/commit.

If a source path is missing, report it and ask the user.

### 5. Check Delphi version folders

Fetch the `Packages/` directory from the target version and list all version-specific subfolders (e.g. `DXE6`, `D10`, `D11`, `D12`, `D13`).

Compare against the current manifest's `packageOptions.folders` mapping:
- Report any **new folders** in the repo not mapped in the manifest (the user may want to add support)
- Report any **removed folders** that are still in the manifest
- If differences exist, ask the user

### 6. Check README for Delphi version changes

Fetch the README.md from the target version. Look for mentions of supported Delphi versions. If the supported range has changed compared to what the manifest covers, report the difference.

### 7. Create the new manifest

Once all verifications pass (or the user has resolved all differences):

1. Create the directory `.blocks/repository/<owner>/<repo>/<new-version>/`
2. Write the new manifest file `<id>.manifest.json` with:
   - `version` updated to the new version
   - `repository.url` updated to point to the new tag/commit
   - All other fields carried over from the previous manifest
   - Any changes the user approved in steps 3-6

### 8. Summary

Report what was done:
- Old version → New version
- Any package changes
- Any Delphi version changes
- Path of the new manifest file

## Important notes

- Always use `WebFetch` to check GitHub content (this project may not have `gh` CLI installed)
- Add a small delay between GitHub API calls to avoid rate limiting
- Preserve the exact formatting style of the existing manifest (indentation, field order, tabs vs spaces)
- The `repository.url` format must match the pattern: for releases use `https://github.com/<owner>/<repo>/tree/v<version>`, for commits use `https://github.com/<owner>/<repo>/commit/<sha>`
- The tag prefix may or may not include `v` — check the actual GitHub tag name and use it as-is in the URL
- FMX packages typically have `"products": ["delphi103+"]` — preserve these constraints
