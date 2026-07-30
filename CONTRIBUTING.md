# Contributing

Contributions that improve reliability, documentation, accessibility, audio behavior, or maintainability are welcome for permitted noncommercial purposes.

## Before starting

- Read `LICENSE` and `NOTICE`.
- Search existing issues before opening a duplicate.
- Keep credentials, personal media, recordings, and local configuration out of commits.
- Discuss major architectural changes before implementing them.

## Development setup

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python src\lqp_hifi_rack_player.py
```

## Validation

Run:

```powershell
python scripts\validate_repository.py
```

The validation checks Python syntax, common secret patterns, required documentation, and screenshot references.

## Pull requests

A good pull request should:

- Explain the problem and the chosen solution.
- Keep unrelated changes separate.
- Include reproduction or testing steps.
- Update English and Spanish documentation when user-facing behavior changes.
- Include real application screenshots when the interface changes.
- Avoid reformatting the entire source unless the pull request is specifically about formatting or modularization.

## Commit messages

Use short imperative messages, for example:

```text
fix: preserve active track after playlist reorder
feat: read ICY stream title metadata
docs: expand NVIDIA API key setup
```

## Licensing of contributions

By submitting a contribution, you represent that you have the right to provide it and agree that it will be distributed under the repository's PolyForm Noncommercial License 1.0.0 and required notices.
