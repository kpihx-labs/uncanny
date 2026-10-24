# KpihX-Labs 0.1.2

- Ship the original MIT license in both wheel and sdist; verify its exact bytes in tests.
- Exclude editor backup files from both archives.
- Make bootstrap, documentation, benchmarks and CI Python provisioning UV-only.
- Replace the legacy Homebrew path with UV and split optional ML hardware profiles.
- Name the import-only CI job accurately and test the release workflow manually.
- Store release build artifacts for 14 days; keep PyPI publishing locally authorized.

## 0.1.1

- Preserve upstream MIT attribution and full Git history.
- Publish as `k-uncanny` without changing the `uncanny` executable or import.
- Adopt uv_build and uv-only validation, build, install, and release commands.
- Add `make push` and `make puhsb` for the GitHub and GitLab SSH remotes.
- Keep upstream detector behavior unchanged; tests are not an independent benchmark.
