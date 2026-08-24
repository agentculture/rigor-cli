# rigor-cli

A tool for performing logic against a ledger, so reasoning stays tractable and provable. Every premise, rule application and conclusion is recorded as an append-only ledger entry that can be replayed, audited and checked independently of the agent that produced it.

## Status

**The ledger domain is not implemented yet.** What is checked in today is the
agent scaffold `rigor-cli` was minted from: an agent-first CLI, a mesh identity,
the vendored skill kit, and a build/lint/deploy baseline. Nothing in `rigor/`
models premises, rules, entries, replay, or audit so far — the verbs below are
the scaffold's introspection surface, not the tool described above.

## What you get

- **An agent-first CLI** cited from [teken](https://github.com/agentculture/teken)
  (`afi-cli`) — the runtime package has no third-party dependencies.
- **A mesh identity** — `culture.yaml` (`suffix` + `backend`) and the matching
  resident prompt file (`AGENTS.colleague.md`, since this agent runs
  `backend: colleague`).
- **The guildmaster skill kit** (18 skills) under `.claude/skills/`, vendored
  cite-don't-import. See [`docs/skill-sources.md`](docs/skill-sources.md).
- **A build + deploy baseline** — pytest, lint, the agent-first rubric gate, and
  PyPI Trusted Publishing wired into GitHub Actions.

## Quickstart

The distribution is named `rigor-cli`; the console script it installs is
**`rigor`**.

```bash
uv sync
uv run pytest -n auto                 # run the test suite
uv run rigor whoami                   # identity from culture.yaml
uv run rigor learn                    # self-teaching prompt (add --json)
uv run teken cli doctor . --strict    # the agent-first rubric gate CI runs
```

## CLI

| Verb | What it does |
|------|--------------|
| `whoami` | Report this agent's nick, version, backend, and model from `culture.yaml`. |
| `learn` | Print a structured self-teaching prompt. |
| `explain <path>` | Markdown docs for any noun/verb path. |
| `overview` | Read-only descriptive snapshot of the agent. |
| `doctor` | Check the agent-identity invariants (prompt-file-present, backend-consistency). |
| `cli overview` | Describe the CLI surface itself. |

Every command supports `--json`. Results go to stdout, errors/diagnostics to
stderr (never mixed). Exit codes: `0` success, `1` user error, `2` environment
error, `3+` reserved.

The CLI's own `learn` and `explain` output still describes this repo as a
clonable agent template — leftover scaffold prose that the first domain-bearing
change replaces.

## Development

```bash
uv run pytest -n auto                        # tests
uv run black --check rigor tests             # lint (CI runs black, isort,
uv run isort --check-only rigor tests        # flake8, bandit, markdownlint)
uv run flake8 rigor tests
uv run bandit -c pyproject.toml -r rigor
```

Every PR bumps the version — even docs and CI — and the `version-check` job
blocks merge otherwise. See [`CLAUDE.md`](CLAUDE.md) for the full conventions:
the CLI's output/error contracts, how to add a verb, the `cicd` PR lane, the
skill kit's cite-don't-import rule, worktree layout, and deploy setup.

## License

Apache 2.0 — see [`LICENSE`](LICENSE).
