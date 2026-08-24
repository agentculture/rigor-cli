# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this project is

`rigor-cli` is an AgentCulture mesh agent whose intended domain is **performing
logic against a ledger, so reasoning stays tractable and provable** — every
premise, rule application and conclusion recorded as an append-only ledger entry
that can be replayed, audited and checked independently of the agent that
produced it.

**None of that domain logic exists on disk yet.** What is checked in today is the
scaffold this repo was minted from (`culture-agent-template`, commit `65e66e2`):
an agent-first CLI, a mesh identity, the vendored skill kit, and a
build/lint/deploy baseline. The ledger, the rule engine, and the replay/audit
verbs are **roadmap**, not code — see [Roadmap](#roadmap). Keep this file
grounded in checked-in reality; if a section drifts ahead of the repo, mark it
`(planned)` or move it under Roadmap.

Siblings in the Organic Development framework:
[`guildmaster`](https://github.com/agentculture/guildmaster) (skills supplier),
[`steward`](https://github.com/agentculture/steward) (alignment — `steward
doctor`), [`teken`](https://github.com/agentculture/teken) (the `afi-cli`
"Agent First Interface" scaffolder this CLI is cited from), and
[`devague`](https://github.com/agentculture/devague) (the idea→spec→plan skills).

## Commands

```bash
uv sync                                     # install (dev group included)
uv run pytest -n auto                       # full suite (22 tests, ~1s)
uv run pytest tests/test_cli.py::test_whoami_json -v   # a single test
uv run pytest -n auto --cov=rigor --cov-report=term    # coverage (fail_under = 60)
uv run teken cli doctor . --strict          # the agent-first rubric gate CI runs
```

Lint — CI runs all five, so run them before opening a PR:

```bash
uv run black --check rigor tests            # line-length 100
uv run isort --check-only rigor tests
uv run flake8 rigor tests
uv run bandit -c pyproject.toml -r rigor
markdownlint-cli2 "**/*.md" "#node_modules" "#.local" "#.claude/skills" "#.teken"
```

Prefer the `run-tests` skill (`.claude/skills/run-tests/scripts/test.sh`) when
you just want the standard pytest+xdist+coverage invocation.

**The installed console script is `rigor`, not `rigor-cli`.** The dist name is
`rigor-cli` and argparse's `prog` (and every help/`learn`/`explain` string) says
`rigor-cli`, but `[project.scripts]` maps `rigor = "rigor.cli:main"`. So:

```bash
uv run rigor whoami        # works
uv run rigor-cli whoami    # fails: no such executable
```

`README.md` and the CLI's own docs strings still print `rigor-cli` in examples.
Treat that as known drift, not as a command to copy.

## The CLI

Cited (cite-don't-import) from teken's `python-cli` reference, so the runtime
package has **no third-party dependencies** — `teken` is a dev dependency only.
Verbs: `whoami`, `learn`, `explain <path>`, `overview`, `doctor`, and the `cli`
noun group (`cli overview`).

Three contracts hold the surface together; all three are rubric-enforced by
`teken cli doctor . --strict` in CI:

- **Output split** (`rigor/cli/_output.py`) — results to stdout, errors and
  diagnostics to stderr, never mixed. Every command takes `--json`.
- **Error propagation** (`rigor/cli/_errors.py`, `rigor/cli/__init__.py`) —
  handlers raise `CliError(code, message, remediation)`; `_dispatch` catches it,
  routes through `emit_error`, and wraps any other exception so no traceback
  reaches stderr. Text mode renders `error: …` + `hint: …` (the `hint:` line is
  what the rubric greps for). Exit codes: `0` success, `1` user error, `2`
  environment error, `3+` reserved.
- **Argparse errors use the same shape** — subparsers are built with
  `parser_class=_CliArgumentParser`, whose `.error()` emits the structured form
  and exits `1` (not argparse's default `2`). Parse-time errors happen before
  `args.json` exists, so `main()` pre-scans raw argv for `--json` and stashes it
  on the class-level `_CliArgumentParser._json_hint`. If you add a nested noun
  group, propagate `parser_class=type(p)` into its subparsers the way
  `_commands/cli.py` does, or its errors bypass the contract.

Each verb is a module under `rigor/cli/_commands/` exposing `register(sub)` and
wired into `_build_parser()`. Identity is parsed out of `culture.yaml` **without
a YAML dependency** (`_commands/whoami.py`, hand-rolled line scanner over the
first agent block) — that constraint is deliberate; don't add PyYAML to fix it.
`whoami.find_culture_yaml()` walks up from `__file__`, not the CWD, so identity
is always this agent's own; a wheel install with no `culture.yaml` alongside the
package degrades to literal defaults and `doctor` reports a single info check.

### Adding a verb or noun

1. New module in `rigor/cli/_commands/` with a `register(sub)` and a handler
   that takes `--json` and returns an int (or `None` for 0).
2. Register it in `_build_parser()` (`rigor/cli/__init__.py`).
3. **Add a catalog entry** in `rigor/explain/catalog.py` keyed by the
   command-path tuple — `explain` resolves only what is in `ENTRIES`, and an
   unknown path is a `CliError`. `tests/test_cli.py` iterates `known_paths()`.
4. Update `learn.py` (`_TEXT` **and** `_as_json_payload()`) and the `_VERBS`
   list in `_commands/overview.py` — both feed rubric checks.
5. Rubric rules to respect: descriptive verbs (`overview`) must never hard-fail
   on a bogus target (hence the accepted-and-ignored `target` positional); any
   noun carrying action-verbs must also expose its own `overview`; `doctor` must
   return `{healthy, checks: [{id, passed, severity, message, remediation}]}`.

## Skills

`.claude/skills/` vendors the guildmaster skill kit **cite-don't-import** — the
scripts are cited verbatim; never reformat or edit them, re-sync instead.
Provenance, the re-sync procedure, and three tracked local divergences
(`agex`→`devex`, `outsource`→`ask-colleague`, and four skills vendored straight
from devague) live in [`docs/skill-sources.md`](docs/skill-sources.md).

Known bookkeeping gaps (verify before trusting either doc):

- 18 skills are on disk; the `docs/skill-sources.md` table documents 16 —
  `remember` and `recall` have no provenance row. `README.md` still says 11.
- `remember`/`recall` **SKILL.md prose contradicts their scripts**: the prose
  says records default to `--visibility private` in `~/.eidetic/memory`, while
  `scripts/remember.sh` (the thing that actually runs) defaults a
  suffix-resolved record to `--visibility public`, landing it in
  `<repo-root>/.eidetic/memory`. The script wins.

Tooling prerequisites: **`devex`** (>=0.21) on PATH — `cicd` delegates the PR
lifecycle to `devex pr`; **`agtag`** (>=0.1) on PATH — `communicate` wraps
`agtag issue`. **`colleague`** on PATH is *optional*, needed only when
`ask-colleague` is invoked (it exits with an install hint if absent).
Per-machine paths (culture server manifest, sibling-project list for the `cicd`
alignment delta) come from `.claude/skills.local.yaml` — copy
`.claude/skills.local.yaml.example`; it is git-ignored.

## Conventions

- **Reach for `ask-colleague` reflexively.** Treat it as the teammate at the
  next desk, not a last resort — its value is a *second, independent mind* (a
  different backend/model), not a stronger one. Before presenting or opening a
  PR on a non-trivial committed diff, run `review`; for a fresh read of an
  unfamiliar area whose answer is independent of your current context, run
  `explore`. Both are read-only (throwaway worktree, zero side effects), so the
  reflex is always safe. The side-effecting `write --apply` / `write --pr` needs
  the user's go-ahead. Colleague's output is a second opinion to verify and own,
  never authority.
- **Every PR bumps the version** — even docs/config/CI. Use the `version-bump`
  skill; the `version-check` CI job comments on the PR and fails otherwise. It
  only runs on `pull_request` events.
- **PRs** go through the `cicd` skill (`devex pr` + SonarCloud gating:
  `status`, `await`). Sign online posts as `- rigor-cli (Claude)` — the `cicd` /
  `communicate` scripts resolve that nick from `culture.yaml` automatically, so
  don't hand-sign in a body those scripts author.
- **Deploy**: pushing to `main` publishes to PyPI via Trusted Publishing
  (`.github/workflows/publish.yml`, path-filtered to `pyproject.toml` and
  `rigor/**`); PRs from this repo do a TestPyPI dry-run with a `.devN` suffix.
  The `pypi` / `testpypi` GitHub environments and a PyPI Trusted Publisher must
  be configured before either job can succeed.
- **SonarCloud** (`agentculture_rigor-cli`) gates CI only when `SONAR_TOKEN` is
  set — the scan step is guarded by `if: env.SONAR_TOKEN != ''`, so fork PRs and
  token-less clones stay green. Coverage maps only because
  `[tool.coverage.run] relative_files = true`; don't remove it.

### Git worktrees

Every worktree you create by hand — workforce fan-out lanes, scratch checkouts —
lives in one repo-named directory beside the checkout:

```bash
git worktree add ../.worktrees.rigor-cli/<name> -b <branch>
```

Not a shared `../worktrees/`: this workspace holds many sibling projects, and a
generic folder accumulates orphaned trees from several repos with nothing
indicating ownership — a stale-tree sweep can't tell a live lane from junk. Use
a branch prefix scoped to the work (`ledger/t2`, not `agent/t2`); plain `agent/*`
collides with leftovers from earlier fan-outs and `git worktree add -b` fails on
an existing branch.

The vendored `assign-to-workforce` skill's fan-out example uses both the shared
path *and* `agent/<task-id>` branches. It is cited verbatim and must not be
edited — override both when following it.

Tear down with `git worktree remove <path>` (deletes directory + bookkeeping);
`git worktree prune` only clears metadata for directories already gone. Never
`rm -rf` a worktree you did not create. Exception: `ask-colleague`'s read-only
verbs create a detached worktree under `${TMPDIR:-/tmp}` and reap it on an EXIT
trap — expect one in `git worktree list` while such a command is in flight.

### Memory discipline — recall before, remember after

A plain `/remember` here lands in `<repo-root>/.eidetic/memory` — committed, and
shared with the team and mesh peers (the `claude` and `colleague` backends both
resolve the `rigor-cli` scope). Pass `--visibility private` to route a record to
`$HOME/.eidetic/memory` instead; `/recall` reads both stores and merges.

- **`/recall` before you start** non-trivial work — prior decisions, gotchas,
  "have we done this before?" — so you build on what's known instead of
  re-deriving it.
- **`/remember` when something worth keeping surfaces**: a non-obvious decision
  and its rationale, a constraint, a fix and *why*, a gotcha that cost time.
  Capture it as it happens.

Don't store what the repo already records (code structure, git history, this
file, `CHANGELOG.md`) — store what you'd otherwise have to re-derive.

## Layout

```text
rigor/                    agent-first CLI (cited from teken's python-cli reference)
  cli/                    parser + error/output contract; _commands/ holds the verbs
  explain/                markdown catalog for `explain`
tests/                    pytest smoke + introspection tests
.claude/skills/           vendored guildmaster skill kit (cite-don't-import)
docs/skill-sources.md     skill provenance ledger
culture.yaml              mesh identity (suffix + backend)
AGENTS.colleague.md       resident prompt for backend: colleague
.github/workflows/        tests + lint + version-check, and PyPI publish
```

## Identity

`culture.yaml` declares `suffix: rigor-cli`, `backend: colleague`, and a served
model. `backend: colleague` fixes the resident prompt file to
**`AGENTS.colleague.md`** — the mesh runtime reads that file, while `CLAUDE.md`
(this file) stays the Claude Code guidance file. Together they satisfy the two
invariants `steward doctor` verifies: **prompt-file-present** and
**backend-consistency**. `rigor doctor` checks the same pair locally, plus a
skills-present check. Changing `culture.yaml` changes what `whoami`, `overview`,
and `doctor` report, with no code change.

## Roadmap

The ledger domain is unimplemented. The CLI's self-description has not caught up
either: `learn.py`, `explain/catalog.py`, `cli/__init__.py`'s parser description,
and `overview.py`'s artifact list all still describe this repo as "a clonable
template for AgentCulture mesh agents", while `pyproject.toml` and `README.md`
carry the ledger description. Rewriting that prose is part of the first
domain-bearing change, not a separate cleanup.

Nothing in `rigor/` models premises, rules, entries, replay, or audit yet. When
that work starts, use the devague chain the vendored skills provide — `/scope`,
`/think`, `/challenge`, `/spec-to-plan` — rather than growing verbs ad hoc; the
append-only-ledger contract is exactly the kind of thing that wants a converged
spec first.
