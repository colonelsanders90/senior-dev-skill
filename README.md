# senior-developer skill

A Claude Code skill that enforces a senior-engineer workflow on every code-writing, modifying, debugging, or reviewing task. It anchors work to a mandatory **Restate → Design → RED → GREEN → Refactor → Review** loop and applies TDD, DDD, separation of concerns, disciplined error handling, judicious singleton use, and secure-by-design engineering.

## Files

- [`SKILL.md`](SKILL.md) — entry point and core workflow
- [`references/design.md`](references/design.md) — design principles (DDD, SoC, dynamic programming)
- [`references/testing.md`](references/testing.md) — TDD protocol and unit-testing guidance
- [`references/errors.md`](references/errors.md) — exception-handling discipline
- [`references/security.md`](references/security.md) — secure-by-design engineering
- [`references/patterns.md`](references/patterns.md) — judicious use of singletons and other patterns
- [`senior-developer.skill`](senior-developer.skill) — packaged bundle for one-step install

## Install

### Option 1 — install the bundle

Download [`senior-developer.skill`](senior-developer.skill) and drop it into your skills directory:

```bash
cp senior-developer.skill ~/.claude/skills/
```

Claude Code will pick it up on the next session.

### Option 2 — clone the repo

```bash
git clone git@github.com:colonelsanders90/senior-dev-skill.git ~/.claude/skills/senior-developer
```

## Usage

Once installed, the skill triggers automatically whenever you ask Claude Code to write, modify, debug, or review code. You can also invoke it explicitly:

```
/senior-developer
```
