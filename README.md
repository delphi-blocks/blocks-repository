# Blocks Repository

This is the official package registry for [DelphiBlocks](https://github.com/delphi-blocks/blocks) — a package manager for Delphi.

It contains the manifest files for all packages compatible with DelphiBlocks. Each manifest describes a specific version of a package: its source location, supported Delphi versions, included packages, and dependencies.

## Structure

```
.blocks/
  repository/
    <author>/
      <package-name>/
        <version>/
          <author>.<package-name>.manifest.json
```

## Contributing

To add a new package or a new version of an existing package:

1. Create the directory `.blocks/repository/<author>/<package>/<version>/`.
2. Add a manifest file named `<author>.<package>.manifest.json` inside it.
3. The `version` field in the manifest must exactly match the `<version>` directory name and follow [SemVer](https://semver.org/).
4. Open a pull request against this repository.


