# Testing

Load at the **RED** step (03) of the core workflow, or whenever you're writing, reviewing, or revising tests.

---

## TDD — The Operational Protocol

The loop *is* the process. Don't write production code without a failing test pointing at it. Tests are the specification that actually executes.

This section is procedural on purpose: vague TDD guidance doesn't survive contact with a real session. Follow the steps in order and don't skip the "run it and see it fail" checkpoint.

### Step 0 · Detect the test runner

Before writing the test, find how this project runs tests. Look for:

| Signal | Likely runner | Typical command |
| --- | --- | --- |
| `pytest.ini`, `pyproject.toml` with `[tool.pytest]`, `tests/` | pytest | `pytest path/to/test_file.py::test_name -x` |
| `package.json` with `"test"` script, `jest.config.*` | jest / vitest | `npx jest path/to/file.test.ts -t 'name'` |
| `go.mod`, `*_test.go` | go test | `go test ./pkg -run TestName` |
| `Cargo.toml` | cargo test | `cargo test test_name` |
| `pom.xml`, `build.gradle` | JUnit / Maven / Gradle | `mvn -Dtest=ClassName#method test` |
| `Gemfile`, `spec/` | RSpec | `bundle exec rspec spec/file_spec.rb -e 'name'` |
| `*.csproj` | dotnet test | `dotnet test --filter FullyQualifiedName~Name` |

Also check `README.md`, `CONTRIBUTING.md`, `Makefile`, and CI config (`.github/workflows/*`) for the canonical command — match what CI uses.

### Step 1 · RED — write one failing test

- Name it for the behaviour: `test_admin_user_can_access_dashboard`, not `test_1` or `test_user`.
- Test through the public interface, not internal helpers.
- Use Arrange / Act / Assert structure (see below).
- Make the failure mode specific. `assert result == 42` beats `assert result`.

### Step 2 · RED — run the test and observe the failure

Run the *single* test you just wrote (not the whole suite — fast feedback). Show the failing output in the conversation, or if you're working solo, paste it into your scratchpad.

A test that has **not been observed failing** is not a RED step. Why this matters:
- A test that passes on first run usually means the behaviour already exists, the assertion is wrong, or the test isn't running at all.
- Seeing the failure proves the test is wired up and exercising the code path you think it is.

Confirm the failure is for the *right reason* — the assertion failed, not an `ImportError`, syntax error, or fixture problem. If the failure is for the wrong reason, fix the test first.

### Step 3 · GREEN — simplest code to pass

Write the minimum code to make this one test pass. Hardcoded return values are acceptable here; the next failing test will force you to generalise. Run the test and confirm it passes. Run the broader suite and confirm nothing else broke.

### Step 4 · Refactor

With tests green, clean up. Re-run the suite after each meaningful change. If a refactor breaks tests, the refactor is wrong (or the test was coupled to implementation — see "What NOT to test").

### Step 5 · Repeat

Next behaviour, next failing test. Keep cycles small — minutes, not hours.

---

## No-test-runner fallback

If the project has no test harness:

1. **Don't silently skip TDD.** State explicitly: "This project has no test runner. I'm going to add one before writing logic."
2. Pick the language-default runner (pytest for Python, jest/vitest for JS/TS, `go test` for Go, etc.). Add the minimum config and a single passing smoke test to prove the harness works.
3. Then resume the normal RED → GREEN loop.

If the user explicitly refuses the test harness ("no, just write the script"), comply but:
- Note the risk in one sentence.
- Add at least one runnable example invocation that demonstrates the happy path (e.g. an `if __name__ == "__main__":` block, a `main()` smoke run, or a brief shell command in the response).
- Leave a `TODO(tests):` marker.

---

## F.I.R.S.T. principles

- **F**ast — milliseconds, not seconds. Slow tests don't get run.
- **I**ndependent — any test runs in any order, alone or with others. No shared mutable state between tests.
- **R**epeatable — same result every time, on any machine. No reliance on wall-clock, network, or random seed.
- **S**elf-validating — pass or fail, no human reading logs.
- **T**imely — written *with* the code, not after.

---

## Structure — Arrange, Act, Assert

```python
def test_admin_user_can_access_dashboard():
    # Arrange — set up the world
    user = create_user(role="admin")

    # Act — do the one thing under test
    result = can_access_dashboard(user)

    # Assert — verify the outcome
    assert result is True
```

One behaviour per test. Keep Arrange short — if setup takes 30 lines, the design under test probably wants smaller seams.

---

## What to test

- Happy path.
- Boundary conditions (empty, one, many, max, off-by-one).
- Error paths — invalid input, dependency failure, network drop, timeout.
- Regressions — every bug fix ships with a test that would have caught it.

## What NOT to test

- The language's built-ins (`assert 1 + 1 == 2` is not a test).
- Third-party libraries — trust that `json.dumps` works.
- Private implementation details — test behaviour through the public interface. A test that breaks when you rename an internal variable is a bad test.

---

## Mocking

Mock at architectural seams: external APIs, databases, the clock, filesystems, network. Don't mock your own domain objects — that's a smell that you're testing implementation, not behaviour.

Prefer real objects with in-memory adapters (e.g. an in-memory repository) over heavy mocking frameworks where you can. The closer your test setup looks to production wiring, the more bugs the test will actually catch.

---

## Worked example — RED → GREEN → Refactor

Task: implement `is_palindrome(s: str) -> bool` that ignores case and non-alphanumerics.

**RED — test first**

```python
# tests/test_palindrome.py
from text_utils import is_palindrome

def test_simple_palindrome_returns_true():
    assert is_palindrome("racecar") is True
```

Run it:

```
$ pytest tests/test_palindrome.py::test_simple_palindrome_returns_true -x
ImportError: cannot import name 'is_palindrome' from 'text_utils'
```

Wrong reason — fix the import path / create the module:

```python
# text_utils.py
def is_palindrome(s):
    raise NotImplementedError
```

```
$ pytest tests/test_palindrome.py::test_simple_palindrome_returns_true -x
NotImplementedError
```

Now failing for the right reason. RED ✓.

**GREEN — simplest code**

```python
def is_palindrome(s):
    return s == s[::-1]
```

```
$ pytest tests/test_palindrome.py::test_simple_palindrome_returns_true -x
PASSED
```

**Next RED — drive out the case/punctuation rule**

```python
def test_ignores_case_and_punctuation():
    assert is_palindrome("A man, a plan, a canal: Panama") is True
```

Fails. Now generalise:

```python
import re

def is_palindrome(s):
    cleaned = re.sub(r"[^a-z0-9]", "", s.lower())
    return cleaned == cleaned[::-1]
```

Both tests pass. **Refactor**: extract the normalisation if it's used elsewhere. Otherwise leave it.

This is the rhythm: one test, one failure, one minimal change, repeat.
