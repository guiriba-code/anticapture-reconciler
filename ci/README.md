# GitHub Actions workflows (not active yet)

These two workflow files are ready to use but live here, not in `.github/workflows/`, because the token used for the first push could not create workflow files (missing `workflow` scope).

To activate them, move them into place and push with an account or token that has the `workflow` scope:

```bash
mkdir -p .github/workflows
git mv ci/workflows/ci.yml ci/workflows/hourly.yml .github/workflows/
git commit -m "ci: enable lint/test and opt-in hourly workflows"
git push
```

What they do once activated:
- `ci.yml` runs `ruff check`, `ruff format --check` and `pytest` on Python 3.10 and 3.12 for every push and pull request. It makes no network calls.
- `hourly.yml` runs the reconciler and uploads `alerts.json`, `alerts.md` and `metrics.prom` as an artifact. Manual runs ("Run workflow") always work. The hourly schedule stays off unless the repository variable `RECONCILER_SCHEDULE_ENABLED` is `true`.
