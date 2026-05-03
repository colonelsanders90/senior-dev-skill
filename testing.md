# Testing

Load at the **RED** step (03) of the core workflow, or whenever you're writing, reviewing, or revising tests.

---

## TDD — Red, Green, Refactor

The loop *is* the process. Don't write production code without a failing test pointing at it. Tests are the specification that actually executes.

Test behaviour, not implementation. A test that breaks when you rename an internal variable is a bad test.

---

## Unit Testing

Tests are first-class code. They get the same care as production code — same naming, same cleanliness, same review.

### The F.I.R.S.T. principles

- **F**ast — milliseconds, not seconds. Slow tests don't get run.
- **I**ndependent — any test can run in any order, alone or with others.
- **R**epeatable — same result every time, on any machine.
- **S**elf-validating — pass or fail, no human reading logs.
- **T**imely — written *with* the code, not after (see TDD).

### Structure — Arrange, Act, Assert

```python
# Arrange — set up the world
user = create_user(role="admin")

# Act — do the one thing under test
result = can_access_dashboard(user)

# Assert — verify the outcome
assert result is True
```

Each test exercises one behaviour. The name should describe that behaviour in plain English: `test_admin_user_can_access_dashboard`, not `test_1` or `test_user`.

### What to test

- Happy path.
- Boundary conditions (empty, one, many, max).
- Error paths — what happens when inputs are invalid, dependencies fail, or the network drops.
- Regressions — every bug fix comes with a test that would have caught it.

### What NOT to test

- The language's built-ins. `assert 1 + 1 == 2` is not a test.
- Third-party libraries — trust that `json.dumps` works.
- Private implementation details — test behaviour through the public interface.

### Mocking

Mock at architectural seams — external APIs, databases, the clock, filesystems. Don't mock your own domain objects; that's a smell that you're testing implementation, not behaviour.
